import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from semantic import Sort

def test():
    sort = Sort("Set",["str", Sort("tuple",["str", Sort("Func",["A", "B"]), "int"])])
    print(sort.compound)
    print(sort)
if __name__ == "__main__":
    test()