import os, glob

py_files = glob.glob('**/*.py', recursive=True)
unmoved_modules = [
    'question_understanding', 'question_profile', 'candidate_ranker',
    'spacy_utils', 'pipeline_context', 'prompt_templates', 'retry_context',
    'domain_hierarchy_builder', 'validation_engine', 'semantic_validator',
    'concept_validator', 'bloom_validator', 'entity_validator',
    'duplicate_validator', 'grammar_validator', 'number_validator',
    'knowledge_consistency_validator', 'topic_validator', 'validation_models'
]

matches = 0
for filepath in py_files:
    if filepath.startswith('.venv') or filepath.startswith('node_modules') or filepath.startswith('archive'):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if any(mod in line for mod in unmoved_modules):
                if 'from core' not in line and 'from validation' not in line and 'import core' not in line and 'import validation' not in line and 'def ' not in line and 'class ' not in line and not line.strip().startswith('"""') and not line.strip().startswith('#'):
                    print(f"{filepath}:{i}: {line.strip()}")
                    matches += 1

print(f"Scan Complete. Total lingering raw module imports found: {matches}")
