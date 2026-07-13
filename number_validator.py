import re
import config

def extract_numbers_and_standards(text: str) -> set:
    """Extract numbers, versions, normal forms, and standards using regex."""
    text_upper = text.upper()
    items = set()
    
    # 1. Normal Forms (e.g. 1NF, 3NF, BCNF)
    nfs = re.findall(r'\b\d+NF\b|\bBCNF\b', text_upper)
    for nf in nfs:
        items.add(nf)
        
    # 2. Protocol versions / standards / bit counts / speeds (e.g. IPv4, AES-256, 802.11)
    patterns = getattr(config, "NUMBER_PATTERNS", [])
    for pattern in patterns:
        matches = re.findall(pattern, text_upper)
        for m in matches:
            items.add(re.sub(r'\s+', '', m))
            
    # Remove matched standards from temp text to avoid double extraction
    temp_text = text_upper
    for item in items:
        temp_text = temp_text.replace(item, " ")
        
    # 3. Standing digits (integers or floats)
    digits = re.findall(r'\b\d+(?:\.\d+)?\b', temp_text)
    for d in digits:
        items.add(d)
        
    return items

def validate_numbers(original_q, candidate_q) -> tuple:
    """
    Validates number preservation.
    Returns: (score, details_dict)
    """
    if hasattr(original_q, "text"):
        orig_text = original_q.text
    else:
        orig_text = original_q

    if hasattr(candidate_q, "text"):
        cand_text = candidate_q.text
    else:
        cand_text = candidate_q

    orig_nums = extract_numbers_and_standards(orig_text)
    cand_nums = extract_numbers_and_standards(cand_text)
    
    number_score_max = getattr(config, "NUMBER_SCORE", 5.0)
    
    if not orig_nums:
        # No numbers to preserve
        return number_score_max, {
            "preservation_ratio": 1.0,
            "original_numbers": [],
            "candidate_numbers": list(cand_nums),
            "preserved_numbers": [],
            "missing_numbers": []
        }
        
    preserved = orig_nums.intersection(cand_nums)
    missing = orig_nums - cand_nums
    
    preservation_ratio = len(preserved) / len(orig_nums)
    score = round(number_score_max * preservation_ratio, 2)
    
    return score, {
        "preservation_ratio": preservation_ratio,
        "original_numbers": list(orig_nums),
        "candidate_numbers": list(cand_nums),
        "preserved_numbers": list(preserved),
        "missing_numbers": list(missing)
    }
