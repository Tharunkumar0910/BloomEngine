import pandas as pd
import os

try:
    df = pd.read_excel("final_dataset_v2.xlsx")
    questions = df["Question"].dropna().astype(str).tolist()
    # Take 1050 questions to satisfy 1000+ requirement
    subset = questions[:1050]
    
    os.makedirs("tests", exist_ok=True)
    with open("tests/large_dataset.txt", "w", encoding="utf-8") as f:
        for q in subset:
            # Strip extra quotes if present
            q_clean = q.strip().strip('"').strip("'")
            f.write(q_clean + "\n\n")
            
    print(f"Successfully wrote {len(subset)} questions to tests/large_dataset.txt")
except Exception as e:
    print(f"Error preparing dataset: {e}")
