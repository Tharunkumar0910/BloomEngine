import re
import unicodedata
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Any
import config
from knowledge.domains import get_normalized_domains
from knowledge.topics import TOPIC_MAP
from knowledge.concepts import _SUPPLEMENTS
from domain_hierarchy_builder import TOPIC_TO_SUBJECT, capitalize_words, build_domain_hierarchy

def normalize_term(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    abbrev_map = getattr(config, "ABBREVIATION_MAP", {})
    for abbrev, expansion in abbrev_map.items():
        text = re.sub(rf"\b{re.escape(abbrev)}\b", expansion, text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Call original builder to construct DOMAIN_HIERARCHY and other indexes for backward compatibility
(
    DOMAIN_HIERARCHY,
    DOMAIN_INDEX,
    SUBJECT_INDEX,
    TOPIC_INDEX,
    ALIAS_INDEX,
    ENTITY_INDEX,
    PHRASE_INDEX,
    KEYWORD_INDEX,
    VERB_INDEX
) = build_domain_hierarchy(
    get_normalized_domains(),
    TOPIC_MAP,
    _SUPPLEMENTS,
    getattr(config, "TECH_ENTITY_DICTIONARY", []),
    getattr(config, "ABBREVIATION_MAP", {})
)

# Build the single unified LOOKUP dictionary
LOOKUP = defaultdict(list)

# Populate LOOKUP
for dom_name, subjects in DOMAIN_HIERARCHY.items():
    dom_norm = normalize_term(dom_name)
    LOOKUP[dom_norm].append({"category": "domain", "target": (dom_name, None, None)})
    
    for sub_name, topics in subjects.items():
        sub_norm = normalize_term(sub_name)
        LOOKUP[sub_norm].append({"category": "subject", "target": (dom_name, sub_name, None)})
        
        for top_name, meta in topics.items():
            top_norm = normalize_term(top_name)
            target = (dom_name, sub_name, top_name)
            
            # Map topic name
            LOOKUP[top_norm].append({"category": "topic", "target": target})
            
            # Keywords and phrases
            for kw in meta["keywords"]:
                cat = "phrase" if " " in kw else "keyword"
                LOOKUP[kw].append({"category": cat, "target": target})
                
            # Aliases
            for al in meta["aliases"]:
                cat = "phrase" if " " in al else "alias"
                LOOKUP[al].append({"category": cat, "target": target})
                
            # Entities
            for ent in meta["entities"]:
                cat = "phrase" if " " in ent else "entity"
                LOOKUP[ent].append({"category": cat, "target": target})
                
            # Verbs
            for v in meta["verbs"]:
                cat = "phrase" if " " in v else "verb"
                LOOKUP[v].append({"category": cat, "target": target})

# Convert LOOKUP to standard dict
LOOKUP = dict(LOOKUP)
