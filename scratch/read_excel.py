import pandas as pd
try:
    df = pd.read_excel("final_dataset_v2.xlsx")
    print(f"Excel shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("First 5 rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading excel: {e}")
