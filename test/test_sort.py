import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import Sort

if __name__ == "__main__":
    # Set[str, tuple[str, str, int]]
    sort = Sort("Set",["str", Sort("tuple",["str", Sort("Func",["A", "B"]), "int"])])
    print(sort.compound)
    print(sort)