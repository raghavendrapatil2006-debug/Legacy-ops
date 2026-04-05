import json

def load_config(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at: {path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {path}")

def get_fs_node(fs: dict, path: str):
    if path == "/" or path == "":
        return fs
    
    parts = [p for p in path.split("/") if p]
    current = fs
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current