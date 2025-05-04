class JsonSerializer:
    def __init__(self):
        pass

    def serialize(self, obj) -> str:
        
        if obj is None:
            result = None
        elif isinstance(obj, (str, int, float, bool)):
            result = obj
        elif isinstance(obj, (list, tuple, set)):
            result = list(map(self.serialize, obj))
        elif isinstance(obj, dict):
            result = {k: self.serialize(v) for k, v in obj.items()}
        else:
            print("serialize...", obj, type(obj))
            result = self.serialize(obj.__dict__)
        return result

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from semantic import Context
    env = Context()
    result = JsonSerializer().serialize(env)
    print(result)
   