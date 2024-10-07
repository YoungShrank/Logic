import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import CMDLogicY0
from line_reader import LineReader

def test():
    grammer_path = "../grammars/line.txt"
    rules_path = "../semantic/rules.txt"
    predefine_path = "./sentences/predefine2.txt"
    logic = CMDLogicY0(
        grammer_path=grammer_path, rules_path=rules_path,
        predefine_path=predefine_path)
    
    for line in LineReader("./sentences/lines_for_cmd.txt"):
        logic.execute(line)
    while True:
        line = input(">>> ")
        if line == "exit":
            break
        logic.execute(line)

if __name__ == "__main__":
    test()