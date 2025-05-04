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
    
    for line in LineReader(ResourceService.get("test/sentences/lines_for_cp2tp.txt")):
        print("input: ", line)
        logic.execute(line)
    # 最后一句 Append Conclusion: ∀ x : N , ( ADD ( x , _0 , ) ) = x
    # 开始cp2tp
    text = "∀ x : N , ( ADD ( x , _0 , ) ) = x"
    add_pos = text.find("ADD")
    bracket_pos = text.find("(", add_pos)
    result = logic.logic_api.char_pos_to_token_pos(0, add_pos, bracket_pos +1 , text)
    print(result)
    print(text[result[2]:result[3] + 1])
    assert text[result[2]:result[3] + 1] == "ADD ( x , _0 , )"
    

if __name__ == "__main__":
    test()