import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from interface import CMDLogicY0
from line_reader import LineReader

def test():
    from resource_service import ResourceService
    grammer_path = ResourceService.get("grammars/line.txt")
    rules_path = ResourceService.get("first-order/rules.txt")
    predefine_path = ResourceService.get("test/sentences/predefine2.txt")
    logic = CMDLogicY0(
        grammer_path=grammer_path, rules_path=rules_path,
        predefine_path=predefine_path)
    
    for line in LineReader(ResourceService.get("test/sentences/lines_for_cmd.txt")):
        print("input: ", line)
        logic.execute(line)
    while True:
        line = input(">>> ")
        if line == "exit":
            break
        logic.execute(line)

if __name__ == "__main__":
    test()