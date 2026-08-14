import pandas as pd
import json

print("=== Reading final_dataset_v2.xlsx ===")
df = pd.read_excel('final_dataset_v2.xlsx')
print('Excel shape:', df.shape)
print('Excel columns:', df.columns.tolist())
print(df.head(5))

print("\n=== Reading Datasets/combined_cleaned.json ===")
with open('Datasets/combined_cleaned.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print('JSON length:', len(data))
if isinstance(data, list) and len(data) > 0:
    print('JSON sample keys:', list(data[0].keys()))
    print('JSON sample 0:', json.dumps(data[0], indent=2))
elif isinstance(data, dict):
    print('JSON top keys:', list(data.keys()))
