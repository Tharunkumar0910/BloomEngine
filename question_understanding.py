import re
import time
import unicodedata
from typing import Optional, Dict, Tuple
from collections import defaultdict

import config
from spacy_utils import get_spacy_doc
from question_profile import QuestionProfile
from knowledge import (
    DOMAIN_HIERARCHY,
    DOMAIN_INDEX,
    SUBJECT_INDEX,
    TOPIC_INDEX,
    ALIAS_INDEX,
    ENTITY_INDEX,
    PHRASE_INDEX,
    KEYWORD_INDEX,
    VERB_INDEX
)

# Composite cache: key = (normalized_text, KNOWLEDGE_VERSION, SPACY_MODEL_VERSION)
profile_cache: Dict[Tuple[str, str, str], QuestionProfile] = {}
_cache_hits:   int = 0
_cache_misses: int = 0

# Intent detection signals (deterministic, ordered)
_INTENT_SIGNALS = [
    ("compare",    ["compare", "contrast", "differentiate", "distinguish", "difference between"]),
    ("evaluate",   ["evaluate", "assess", "justify", "critique", "appraise", "judge"]),
    ("design",     ["design", "architect", "construct", "model", "create", "formulate", "develop"]),
    ("implement",  ["implement", "write", "code", "program", "build"]),
    ("analyze",    ["analyze", "analyse", "examine", "investigate", "determine"]),
    ("recommend",  ["recommend", "suggest", "propose", "advise"]),
    ("define",     ["define", "what is", "state", "give the definition", "give"]),
    ("list",       ["list", "enumerate", "name", "mention", "identify"]),
    ("explain",    ["explain", "describe", "discuss", "elaborate", "illustrate"]),
]

class QuestionUnderstandingEngine:
    @staticmethod
    def normalize_pipeline(text: str) -> str:
        """
        Normalize text through a deterministic pipeline:
        Lowercase -> Abbreviation Expansion -> Unicode Cleanup -> Whitespace Cleanup.
        """
        if not text:
            return ""
        # 1. Lowercase
        text = text.lower()
        # 2. Abbreviation Expansion
        abbrev_map = getattr(config, "ABBREVIATION_MAP", {})
        for abbrev, expansion in abbrev_map.items():
            text = re.sub(rf"\b{re.escape(abbrev)}\b", expansion, text)
        # 3. Unicode Cleanup
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        # 4. Whitespace Cleanup
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def cache_stats(cls) -> dict:
        """Return cache hit/miss statistics."""
        global _cache_hits, _cache_misses
        total = _cache_hits + _cache_misses
        return {
            "hits":     _cache_hits,
            "misses":   _cache_misses,
            "size":     len(profile_cache),
            "hit_rate": round(_cache_hits / total, 4) if total > 0 else 0.0,
        }

    @classmethod
    def _detect_hierarchy(cls, doc, normalized_text: str) -> dict:
        """
        Performs weighted keyword matching against DOMAIN_HIERARCHY to detect
        Domain, Subject, and Topic along with their confidence scores.
        """

        matched_terms_by_path = defaultdict(dict)  # (dom, subj, top) -> {term: (category, weight)}
        weights = getattr(config, "MATCH_WEIGHTS", {})
        
        # 1. Exact matches of domain, subject, or topic names
        # Check domain names
        for dom_norm, dom_display in DOMAIN_INDEX.items():
            if re.search(rf"\b{re.escape(dom_norm)}\b", normalized_text):
                for subj_display in DOMAIN_HIERARCHY[dom_display]:
                    for top_display in DOMAIN_HIERARCHY[dom_display][subj_display]:
                        target = (dom_display, subj_display, top_display)
                        matched_terms_by_path[target][dom_norm] = ("exact", weights.get("exact", 10))
                        
        # Check subject names
        for dom_norm, subjects in SUBJECT_INDEX.items():
            dom_display = DOMAIN_INDEX[dom_norm]
            for subj_display in subjects:
                subj_norm = subj_display.lower()
                if re.search(rf"\b{re.escape(subj_norm)}\b", normalized_text):
                    for top_display in DOMAIN_HIERARCHY[dom_display][subj_display]:
                        target = (dom_display, subj_display, top_display)
                        matched_terms_by_path[target][subj_norm] = ("exact", weights.get("exact", 10))
                        
        # Check topic names
        for (dom_norm, subj_norm), topics in TOPIC_INDEX.items():
            dom_display = DOMAIN_INDEX[dom_norm]
            subj_display = None
            for s in DOMAIN_HIERARCHY[dom_display]:
                if s.lower() == subj_norm:
                    subj_display = s
                    break
            if not subj_display:
                continue
            for top_display in topics:
                top_norm = top_display.lower()
                if re.search(rf"\b{re.escape(top_norm)}\b", normalized_text):
                    target = (dom_display, subj_display, top_display)
                    matched_terms_by_path[target][top_norm] = ("exact", weights.get("exact", 10))

        # 2. Phrase matches
        for phrase, targets in PHRASE_INDEX.items():
            if re.search(rf"\b{re.escape(phrase)}\b", normalized_text):
                for target in targets:
                    current = matched_terms_by_path[target].get(phrase, ("", 0))
                    if current[1] < weights.get("phrase", 9):
                        matched_terms_by_path[target][phrase] = ("phrase", weights.get("phrase", 9))

        # 3. Alias matches
        for alias, targets in ALIAS_INDEX.items():
            if re.search(rf"\b{re.escape(alias)}\b", normalized_text):
                for target in targets:
                    current = matched_terms_by_path[target].get(alias, ("", 0))
                    if current[1] < weights.get("alias", 8):
                        matched_terms_by_path[target][alias] = ("alias", weights.get("alias", 8))

        # 4. Entity matches
        for entity, targets in ENTITY_INDEX.items():
            if re.search(rf"\b{re.escape(entity)}\b", normalized_text):
                for target in targets:
                    current = matched_terms_by_path[target].get(entity, ("", 0))
                    if current[1] < weights.get("entity", 7):
                        matched_terms_by_path[target][entity] = ("entity", weights.get("entity", 7))

        # 5. Token-level keyword, lemma, verb matches
        for token in doc:
            if token.is_stop or token.is_punct:
                continue
            token_text = token.text.lower()
            token_lemma = token.lemma_.lower()

            if token_text in KEYWORD_INDEX:
                for target in KEYWORD_INDEX[token_text]:
                    current = matched_terms_by_path[target].get(token_text, ("", 0))
                    if current[1] < weights.get("keyword", 6):
                        matched_terms_by_path[target][token_text] = ("keyword", weights.get("keyword", 6))

            if token_lemma in KEYWORD_INDEX:
                for target in KEYWORD_INDEX[token_lemma]:
                    current = matched_terms_by_path[target].get(token_lemma, ("", 0))
                    if current[1] < weights.get("lemma", 5):
                        matched_terms_by_path[target][token_lemma] = ("lemma", weights.get("lemma", 5))

            if token_text in VERB_INDEX:
                for target in VERB_INDEX[token_text]:
                    current = matched_terms_by_path[target].get(token_text, ("", 0))
                    if current[1] < weights.get("verb", 3):
                        matched_terms_by_path[target][token_text] = ("verb", weights.get("verb", 3))

        # Group matches by domain to avoid double-counting same term
        domain_unique_matches = defaultdict(dict)
        for target, term_matches in matched_terms_by_path.items():
            dom, _, _ = target
            for term, (cat, w) in term_matches.items():
                if term not in domain_unique_matches[dom] or domain_unique_matches[dom][term][1] < w:
                    domain_unique_matches[dom][term] = (cat, w)
        
        domain_scores = {dom: sum(w for c, w in terms.values()) for dom, terms in domain_unique_matches.items()}

        if not domain_scores:
            return {
                "domain": "Other Computer Science",
                "domain_confidence": 0.0,
                "candidate_domains": {},
                "subject": "General Computer Science",
                "subject_confidence": 0.0,
                "candidate_subjects": {},
                "topic": "General",
                "topic_confidence": 0.0,
                "candidate_topics": {},
                "matched_terms": {"keyword": (), "alias": (), "entity": (), "phrase": (), "verb": ()},
                "matched_domain_keywords": (),
                "matched_topic_keywords": ()
            }

        # Normalize domain scores
        sum_dom_scores = sum(domain_scores.values())
        candidate_domains = {dom: round(score / sum_dom_scores, 4) for dom, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)}
        best_domain = max(domain_scores, key=domain_scores.get)
        domain_conf = candidate_domains[best_domain]

        # Calculate subject scores within the best domain
        subject_unique_matches = defaultdict(dict)
        for target, term_matches in matched_terms_by_path.items():
            dom, subj, _ = target
            if dom == best_domain:
                for term, (cat, w) in term_matches.items():
                    if term not in subject_unique_matches[subj] or subject_unique_matches[subj][term][1] < w:
                        subject_unique_matches[subj][term] = (cat, w)

        subject_scores = {subj: sum(w for c, w in terms.values()) for subj, terms in subject_unique_matches.items()}
        if not subject_scores:
            best_subject = "General Computer Science"
            subject_conf = 0.0
            candidate_subjects = {}
        else:
            sum_subj_scores = sum(subject_scores.values())
            candidate_subjects = {subj: round(score / sum_subj_scores, 4) for subj, score in sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)}
            best_subject = max(subject_scores, key=subject_scores.get)
            subject_conf = candidate_subjects[best_subject]

        # Calculate topic scores within best domain and best subject
        topic_scores = {}
        for target, term_matches in matched_terms_by_path.items():
            dom, subj, top = target
            if dom == best_domain and subj == best_subject:
                topic_scores[top] = sum(w for c, w in term_matches.values())

        if not topic_scores:
            best_topic = "General"
            topic_conf = 0.0
            candidate_topics = {}
            best_topic_target = None
        else:
            sum_top_scores = sum(topic_scores.values())
            candidate_topics = {top: round(score / sum_top_scores, 4) for top, score in sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)}
            best_topic = max(topic_scores, key=topic_scores.get)
            topic_conf = candidate_topics[best_topic]
            best_topic_target = (best_domain, best_subject, best_topic)

        # Matched terms for selected path
        matched_terms_dict = {
            "keyword": [],
            "alias": [],
            "entity": [],
            "phrase": [],
            "verb": []
        }
        if best_topic_target and best_topic_target in matched_terms_by_path:
            for term, (cat, w) in matched_terms_by_path[best_topic_target].items():
                c = "keyword" if cat == "lemma" else cat
                if c in matched_terms_dict:
                    matched_terms_dict[c].append(term)
        matched_terms = {k: tuple(sorted(v)) for k, v in matched_terms_dict.items()}

        # For backward compatibility
        matched_domain_kws = tuple(sorted(domain_unique_matches[best_domain].keys()))
        matched_topic_kws = tuple(sorted(matched_terms_by_path[best_topic_target].keys())) if best_topic_target else ()

        # Apply canonical mapping to all candidates
        mapped_candidate_domains = {}
        for dom, score in candidate_domains.items():
            mapped_dom = config.CANONICAL_DOMAIN_MAPPING.get(dom.lower(), dom)
            mapped_candidate_domains[mapped_dom] = max(mapped_candidate_domains.get(mapped_dom, 0.0), score)
        candidate_domains = mapped_candidate_domains

        # General domain canonicalization
        best_domain_mapped = config.CANONICAL_DOMAIN_MAPPING.get(best_domain.lower(), best_domain)
        if best_domain_mapped != best_domain:
            best_domain = best_domain_mapped
            domain_conf = 1.0


        return {
            "domain": best_domain,
            "domain_confidence": domain_conf,
            "candidate_domains": candidate_domains,
            "subject": best_subject,
            "subject_confidence": subject_conf,
            "candidate_subjects": candidate_subjects,
            "topic": best_topic,
            "topic_confidence": topic_conf,
            "candidate_topics": candidate_topics,
            "matched_terms": matched_terms,
            "matched_domain_keywords": matched_domain_kws,
            "matched_topic_keywords": matched_topic_kws
        }

    @classmethod
    def _detect_domain(cls, doc) -> dict:
        """Deprecated: calls _detect_hierarchy for backward compatibility."""
        res = cls._detect_hierarchy(doc, cls.normalize_pipeline(doc.text))
        return {
            "domain": res["domain"],
            "confidence": res["domain_confidence"],
            "matched_keywords": list(res["matched_domain_keywords"])
        }

    @classmethod
    def _detect_topic(cls, doc, domain: str) -> dict:
        """Deprecated: calls _detect_hierarchy for backward compatibility."""
        res = cls._detect_hierarchy(doc, cls.normalize_pipeline(doc.text))
        return {
            "topic": res["topic"],
            "confidence": res["topic_confidence"],
            "matched_keywords": list(res["matched_topic_keywords"])
        }

    @staticmethod
    def _detect_intent(text: str):
        """
        Deterministic intent detection from normalized question text.
        Returns (intent: str, confidence: float).
        """
        text_lower = text.lower()
        for intent_name, signals in _INTENT_SIGNALS:
            for signal in signals:
                if signal in text_lower:
                    return intent_name, 1.0
        return "explain", 0.7   # default

    @classmethod
    def build_profile(cls, raw_text: str, source_bloom: Optional[str] = None) -> QuestionProfile:
        """
        Builds a versioned, immutable QuestionProfile.
        Uses a composite cache key to automatically invalidate when knowledge/spacy changes.
        """
        global _cache_hits, _cache_misses
        t_start = time.time()

        normalized_text = cls.normalize_pipeline(raw_text)
        k_ver   = getattr(config, "KNOWLEDGE_VERSION", "2.0")
        sp_ver  = getattr(config, "SPACY_MODEL_VERSION", "en_core_web_sm")
        cache_key = (normalized_text, k_ver, sp_ver)

        if cache_key in profile_cache:
            cached = profile_cache[cache_key]
            if source_bloom and cached.source_bloom != source_bloom:
                new_profile = QuestionProfile(
                    raw_question=raw_text,
                    normalized_question=normalized_text,
                    source_bloom=source_bloom,
                    domain=cached.domain,
                    domain_confidence=cached.domain_confidence,
                    matched_domain_keywords=cached.matched_domain_keywords,
                    topic=cached.topic,
                    topic_confidence=cached.topic_confidence,
                    matched_topic_keywords=cached.matched_topic_keywords,
                    concepts=cached.concepts,
                    technical_entities=cached.technical_entities,
                    numbers=cached.numbers,
                    keywords=cached.keywords,
                    noun_chunks=cached.noun_chunks,
                    dependency_tokens=cached.dependency_tokens,
                    intent=cached.intent,
                    intent_confidence=cached.intent_confidence,
                    processing_time=0.0,
                    parse_method="spacy",
                    profile_version=cached.profile_version,
                    subject=cached.subject,
                    subject_confidence=cached.subject_confidence,
                    candidate_domains=cached.candidate_domains,
                    candidate_subjects=cached.candidate_subjects,
                    candidate_topics=cached.candidate_topics,
                    matched_terms=cached.matched_terms
                )
                profile_cache[cache_key] = new_profile
                _cache_hits += 1
                return new_profile
            _cache_hits += 1
            return cached
        _cache_misses += 1

        # Parse with spaCy once
        doc = get_spacy_doc(normalized_text)

        # Detect Domain, Subject, and Topic in a single hierarchical pass
        hierarchy_info = cls._detect_hierarchy(doc, normalized_text)

        # 3. Extract Concepts (using concept_validator logic)
        from concept_validator import extract_concepts_with_compounds
        concepts, _ = extract_concepts_with_compounds(doc)

        # 4. Extract Technical Entities
        from entity_validator import detect_entities
        entities = tuple(sorted(detect_entities(doc)))

        # 5. Extract Numbers
        from number_validator import extract_numbers_and_standards
        numbers = tuple(sorted(extract_numbers_and_standards(normalized_text)))

        # 6. Extract Keywords
        kws = []
        for token in doc:
            if token.pos_ in ("NOUN", "PROPN", "ADJ", "VERB") and not token.is_stop and not token.is_punct:
                kws.append(token.text.lower())
        keywords = tuple(sorted(set(kws)))

        # 7. Extract Noun Chunks
        noun_chunks = tuple(sorted(set(chunk.text.lower() for chunk in doc.noun_chunks)))

        # 8. Extract Dependency Tokens
        dep_toks = []
        for token in doc:
            if token.dep_ in ("nsubj", "dobj", "pobj", "root") and not token.is_stop and not token.is_punct:
                dep_toks.append(token.text.lower())
        dependency_tokens = tuple(sorted(set(dep_toks)))

        # 9. Detect Intent
        intent, intent_conf = cls._detect_intent(normalized_text)

        processing_time = time.time() - t_start

        # Construct Immutable Profile
        profile = QuestionProfile(
            raw_question=raw_text,
            normalized_question=normalized_text,
            source_bloom=source_bloom if source_bloom else "Unknown",
            domain=hierarchy_info["domain"],
            domain_confidence=hierarchy_info["domain_confidence"],
            matched_domain_keywords=hierarchy_info["matched_domain_keywords"],
            topic=hierarchy_info["topic"],
            topic_confidence=hierarchy_info["topic_confidence"],
            matched_topic_keywords=hierarchy_info["matched_topic_keywords"],
            concepts=concepts,
            technical_entities=entities,
            numbers=numbers,
            keywords=keywords,
            noun_chunks=noun_chunks,
            dependency_tokens=dependency_tokens,
            intent=intent,
            intent_confidence=intent_conf,
            processing_time=processing_time,
            parse_method="spacy",
            profile_version="2.1",
            subject=hierarchy_info["subject"],
            subject_confidence=hierarchy_info["subject_confidence"],
            candidate_domains=hierarchy_info["candidate_domains"],
            candidate_subjects=hierarchy_info["candidate_subjects"],
            candidate_topics=hierarchy_info["candidate_topics"],
            matched_terms=hierarchy_info["matched_terms"]
        )

        profile_cache[cache_key] = profile
        return profile



