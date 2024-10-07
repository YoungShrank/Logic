import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import LineParser
from line_reader import LineReader
from Structure import VTree
def test():
    """
    测试 LineParser
    """
    line_parser = LineParser("../grammars/line.txt")
    reader = LineReader("./sentences/lines.txt")
    for i, line in enumerate(reader, 1):
        symbol_values = line_parser.lexical(line)
        print("*"*30)
        print(line)
        print(symbol_values)
        tree = line_parser.build_tree(symbol_values)
        VTree(tree).view(path = "./view_abstract_tree.html")
        input("{} lines parsed, to next line?".format(i))


if __name__ == "__main__":
    test()