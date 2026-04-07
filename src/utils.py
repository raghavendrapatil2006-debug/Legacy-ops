import json

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_fs_node(filesystem: dict, path: str):
    if not path or path == "/" or path == ".":
        return filesystem
    
    # Force clean path parsing to handle absolute and relative paths identically
    clean_path = path.lstrip('/')
    parts = [p for p in clean_path.split("/") if p and p != "."]
    
    current = filesystem
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current