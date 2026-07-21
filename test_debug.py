import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from question_understanding import QuestionUnderstandingEngine
from spacy_utils import get_spacy_doc

q = "Define the OSI model and state the function of each of its seven layers."
normalized = QuestionUnderstandingEngine.normalize_pipeline(q)
doc = get_spacy_doc(normalized)

print("Normalized:", normalized)

# Import builder components to see index content
from knowledge import (
    DOMAIN_HIERARCHY, DOMAIN_INDEX, SUBJECT_INDEX, TOPIC_INDEX,
    ALIAS_INDEX, ENTITY_INDEX, PHRASE_INDEX, KEYWORD_INDEX, VERB_INDEX
)

print("OSI model in PHRASE_INDEX:", "osi model" in PHRASE_INDEX)
if "osi model" in PHRASE_INDEX:
    print("Targets for osi model:", PHRASE_INDEX["osi model"])

res = QuestionUnderstandingEngine._detect_hierarchy(doc, normalized)
print("Result:")
for k, v in res.items():
    print(f"  {k}: {v}")
