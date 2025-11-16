import os, json

def load_json(filename, default=None):
    if os.path.exists(filename):
        try:
            with open(filename,'r',encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print('Failed to read', filename, e)
    if default is None:
        return None
    try:
        with open(filename,'w',encoding='utf-8') as f:
            json.dump(default, f, indent=2)
    except Exception as e:
        print('Failed to write default to', filename, e)
    return default

def save_json(filename, data):
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(data, f, indent=2)
