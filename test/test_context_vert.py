import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import LineParser, LineAnalyzer, Context, TermAnalyzer
from line_reader import LineReader
from Structure import VTree
from utils import tostr

def test():
    lines_path = "./sentences/lines_for_context.txt"
    line_parser = LineParser("../grammars/line.txt")
    env = Context()
    for line in LineReader(lines_path):
        input("to next line ?")
        print(line)
        symbol_values = line_parser.lexical(line)
        abt = line_parser.build_tree(symbol_values)
        line_analyzer = LineAnalyzer(abt, env)
        term_analyzer = TermAnalyzer(abt, env)
        term_analyzer.solve()
        VTree(abt).view(viewf=lambda i, data:"{} {}".format(data["symbol"],tostr(data.get("sort"))), path="./sort_deduce.html" )
        line_analyzer.env_switch()


if __name__ == "__main__":
    test()