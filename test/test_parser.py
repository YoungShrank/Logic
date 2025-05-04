import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from semantic import LineParser
from line_reader import LineReader
from Structure import VTree
def test():
    """
    测试 LineParser
    """
    from resource_service import ResourceService
    line_parser = LineParser(ResourceService.get("grammars/line.txt"))
    reader = LineReader(ResourceService.get("test/sentences/lines_for_analyser.txt"))
    for i, line in enumerate(reader, 1):
        symbol_values = line_parser.lexical(line)
        print("*"*30)
        print(line)
        print(symbol_values)
        tree = line_parser.build_tree(symbol_values)
        VTree(tree).view(path = ResourceService.get("out/line_parser.html"))
        input("{} lines parsed, to next line?".format(i))


if __name__ == "__main__":
    test()