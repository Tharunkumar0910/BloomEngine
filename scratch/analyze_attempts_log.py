import json

try:
    with open("attempt_logs.json", "r", encoding="utf-8") as f:
        logs = json.load(f)
    print(f"Loaded {len(logs)} attempt logs.")
    
    # Let's count keys
    advisor_activated_vals = [log.get("advisor_activated") for log in logs if "advisor_activated" in log]
    advisor_guidance_vals = [log.get("advisor_guidance_produced") for log in logs if "advisor_guidance_produced" in log]
    advisor_skipped_vals = [log.get("advisor_skipped") for log in logs if "advisor_skipped" in log]
    missing_preferred_vals = [log.get("missing_preferred") for log in logs if "missing_preferred" in log]
    
    print(f"Number of logs with 'advisor_activated': {len(advisor_activated_vals)}")
    print(f"True 'advisor_activated': {sum(1 for x in advisor_activated_vals if x)}")
    print(f"Number of logs with 'advisor_guidance_produced': {len(advisor_guidance_vals)}")
    print(f"True 'advisor_guidance_produced': {sum(1 for x in advisor_guidance_vals if x)}")
    print(f"Number of logs with 'advisor_skipped': {len(advisor_skipped_vals)}")
    print(f"True 'advisor_skipped': {sum(1 for x in advisor_skipped_vals if x)}")
    
    # Print a few logs with non-empty missing_preferred or generic_terms_detected
    non_empty = [log for log in logs if log.get("missing_preferred") or log.get("generic_terms_detected")]
    print(f"Logs with terminology fields: {len(non_empty)}")
    if non_empty:
        print("Example log:", json.dumps(non_empty[0], indent=2))
        
except Exception as e:
    print("Error:", e)
