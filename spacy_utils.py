import re
import spacy
import config

_nlp = None

def get_spacy_nlp():
    """Lazily load and return the spaCy NLP model."""
    global _nlp
    if _nlp is None:
        # Load with disabled components we don't need for speed
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

_doc_cache = {}
SPACY_CACHE_HITS = 0
SPACY_CACHE_MISSES = 0

def get_spacy_doc(text: str):
    """Parse text with spaCy and cache the resulting Doc object."""
    global _doc_cache, SPACY_CACHE_HITS, SPACY_CACHE_MISSES
    if text in _doc_cache:
        SPACY_CACHE_HITS += 1
        return _doc_cache[text]
    else:
        SPACY_CACHE_MISSES += 1
        nlp = get_spacy_nlp()
        _doc_cache[text] = nlp(text)
        return _doc_cache[text]

def clear_spacy_cache():
    """Clear the cached documents to free memory if needed."""
    global _doc_cache, SPACY_CACHE_HITS, SPACY_CACHE_MISSES
    _doc_cache.clear()
    SPACY_CACHE_HITS = 0
    SPACY_CACHE_MISSES = 0


def expand_abbreviations(text):
    """Normalize and expand abbreviations in text using the strict allowed map from config."""
    text_lower = text.lower()
    abbreviation_map = getattr(config, "ABBREVIATION_MAP", {})
    for abbr, expanded in abbreviation_map.items():
        text_lower = re.sub(r'\b' + re.escape(abbr) + r'\b', expanded, text_lower)
    return text_lower
def normalize_embedding_key(text: str) -> str:
    """Standardize cache keys for SentenceTransformer embedding lookups."""
    return " ".join(text.lower().strip().split())


def normalize_question(text: str) -> str:
    """Normalize question text formatting automatically:
    - Collapse multiple spaces.
    - Capitalize the first letter.
    - Correct trailing punctuation (avoid duplicate/mixed punctuation like ?? or .?).
    """
    text = text.strip()
    if not text:
        return text
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Capitalize the first character
    if not text[0].isupper():
        text = text[0].upper() + text[1:]
        
    # Correct trailing punctuation: remove any trailing spaces before trailing punctuation, e.g. "SQL ." -> "SQL."
    text = re.sub(r'\s+([?.!]+)$', r'\1', text)
    
    # Standardize trailing punctuation: if there are multiple, e.g., "??", "...", "?.", normalize to a single one.
    if text[-1] in ('?', '.', '!'):
        punctuation_suffix = re.search(r'[?.!]+$', text).group(0)
        base_text = text[:-len(punctuation_suffix)]
        if '?' in punctuation_suffix:
            text = base_text + '?'
        elif '!' in punctuation_suffix:
            text = base_text + '!'
        else:
            text = base_text + '.'
    else:
        # Check if the question starts with common question words to decide on '?' vs '.'
        question_words = ('what', 'how', 'why', 'which', 'who', 'when', 'where', 'explain', 'describe', 'define', 'list', 'state', 'compare', 'evaluate', 'design')
        first_word = text.split()[0].lower().strip(".,?!:;")
        if first_word in question_words or text.lower().startswith(('is ', 'are ', 'can ', 'could ', 'should ', 'would ', 'do ', 'does ', 'did ')):
            text += '?'
        else:
            text += '.'
            
    return text


class NLPContext:
    def __init__(self, text: str, st_model=None, get_cached_embedding_fn=None):
        self._raw_text = text
        self._text = None
        self._doc = None
        self.st_model = st_model
        self.get_cached_embedding_fn = get_cached_embedding_fn
        
        self._concepts = None
        self._compounds = None
        self._entities = None
        self._embedding = None

    @property
    def text(self):
        if self._text is None:
            self._text = normalize_question(self._raw_text)
        return self._text

    @property
    def doc(self):
        if self._doc is None:
            self._doc = get_spacy_doc(self.text)
        return self._doc

    @property
    def concepts_and_compounds(self):
        if self._concepts is None:
            # Import here to avoid circular dependency
            from concept_validator import extract_concepts_with_compounds
            self._concepts, self._compounds = extract_concepts_with_compounds(self)
        return self._concepts, self._compounds

    @property
    def concepts(self):
        return self.concepts_and_compounds[0]

    @property
    def compounds(self):
        return self.concepts_and_compounds[1]

    @property
    def entities(self):
        if self._entities is None:
            # Import here to avoid circular dependency
            from entity_validator import detect_entities
            self._entities = detect_entities(self)
        return self._entities

    def get_embedding(self):
        if self._embedding is None and self.st_model is not None and self.get_cached_embedding_fn is not None:
            self._embedding = self.get_cached_embedding_fn(self.text, self.st_model)
        return self._embedding

