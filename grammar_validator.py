import re
import config
from config import GRAMMAR_LEGIT_REPEATS
from collections import Counter

def validate_grammar_and_formatting(text: str) -> tuple:
    """
    Validates question grammar: length (content words count) and word/bigram repetitions.
    Returns: (score, details_dict)
    """
    penalties = 0.0
    issues = []
    
    text_stripped = text.strip()
    words = text_stripped.split()
    
    # Read ignore list from config
    repetition_ignore = getattr(config, "REPETITION_IGNORE_WORDS", set())
    
    # 1. Minimum Content Words check
    words_raw = re.findall(r"\b\w+\b", text_stripped.lower())
    content_words = [w for w in words_raw if w not in repetition_ignore]
    
    min_content_words_val = getattr(config, "MIN_CONTENT_WORDS", 2)
    is_too_short = len(content_words) < min_content_words_val
    
    if is_too_short:
        penalties += 5.0
        issues.append(f"Question is too short (less than {min_content_words_val} content words).")
        
    # 2. Repetition check (words & bigrams)
    duplicate_phrase_found = False
    legit_repeats = GRAMMAR_LEGIT_REPEATS
    
    for i, w in enumerate(words_raw):
        if w in repetition_ignore or w in legit_repeats:
            continue
        for j in range(1, 4):
            if i + j < len(words_raw) and words_raw[i] == words_raw[i + j]:
                duplicate_phrase_found = True
                issues.append(f"Word repetition detected: '{w}' repeated nearby.")
                break
        if duplicate_phrase_found:
            break
            
    if not duplicate_phrase_found:
        bigrams = [f"{words_raw[i]} {words_raw[i + 1]}" for i in range(len(words_raw) - 1)]
        bigram_counts = Counter(bigrams)
        for bg, count in bigram_counts.items():
            if count >= 3:
                duplicate_phrase_found = True
                issues.append(f"Bigram repeated 3+ times: '{bg}'.")
                break
            elif count == 2:
                bg_indices = [i for i, b in enumerate(bigrams) if b == bg]
                if len(bg_indices) == 2 and bg_indices[1] - bg_indices[0] <= 2:
                    duplicate_phrase_found = True
                    issues.append(f"Consecutive bigram repetition: '{bg}'.")
                    break
                    
    if duplicate_phrase_found:
        penalties += 2.0
        
    grammar_score_max = getattr(config, "GRAMMAR_SCORE", 5.0)
    score = max(0.0, grammar_score_max - penalties)
    
    return score, {
        "issues": issues,
        "duplicate_phrase_found": duplicate_phrase_found,
        "is_too_short": is_too_short,
        "content_words_count": len(content_words),
        "penalties": penalties
    }

