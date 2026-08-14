import pandas as pd
import json

df = pd.read_excel('final_dataset_v2.xlsx')
print("--- DeBERTa Dataset Samples (final_dataset_v2.xlsx) ---")
for idx, row in df.head(10).iterrows():
    print(f"Row {idx+1}: Question='{row['Question']}', Bloom_Level='{row['Bloom_Level']}', Cognitive_Level_Number={row['Cognitive_Level_Number']}, Difficulty='{row['Difficulty']}'")

print("\n--- FLAN-T5 Dataset Samples (Datasets/combined_cleaned.json) ---")
with open('Datasets/combined_cleaned.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, item in enumerate(data[:10]):
    print(f"Pair {i+1}:")
    print(f"  Input: {item['input']}")
    print(f"  Output: {item['output']}")
