import json

def dump_notebook(nb_path, out_file):
    out_file.write(f"\n==================================================\n")
    out_file.write(f"NOTEBOOK: {nb_path}\n")
    out_file.write(f"==================================================\n")

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for i, cell in enumerate(nb.get("cells", [])):
        cell_type = cell.get("cell_type")
        source = "".join(cell.get("source", []))
        out_file.write(f"\n--- [Cell {i}] ({cell_type}) ---\n")
        out_file.write(f"SOURCE:\n{source}\n")

        outputs = cell.get("outputs", [])
        for out in outputs:
            out_type = out.get("output_type")
            if out_type in ["stream", "execute_result"]:
                text = "".join(out.get("text", [])) or "".join(out.get("data", {}).get("text/plain", []))
                out_file.write(f"\nOUTPUT:\n{text}\n")

with open(r".\scratch\notebook_dump.txt", "w", encoding="utf-8") as out:
    dump_notebook(r".\NoteBook\class.ipynb", out)
    dump_notebook(r".\NoteBook\FFlan.ipynb", out)

print("Dumped notebook contents to scratch/notebook_dump.txt")
