import json

def inspect_notebook(path):
    print(f"=== Inspecting {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    print("Cells count:", len(nb.get('cells', [])))
    for i, cell in enumerate(nb.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source = "".join(cell.get('source', []))
            if 'read_csv' in source or 'read_excel' in source or 'load_dataset' in source or 'pd.' in source or 'Dataset' in source:
                print(f"--- Cell {i} ---")
                print(source[:500])
                print("...")

inspect_notebook('NoteBook/class.ipynb')
inspect_notebook('NoteBook/FFlan.ipynb')
