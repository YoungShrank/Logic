import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import LineParser, LineAnalyzer, Context, TermAnalyzer
from line_reader import LineReader
from Structure import VTree
from utils import tostr

def test():
    lines_path = "./sentences/lines_for_analyser.txt"
    line_parser = LineParser("../grammars/line.txt")
    env = Context()
    for line in LineReader(lines_path):
        input("to next line ?")
        print(line)
        symbol_values = line_parser.lexical(line)
        abt = line_parser.build_tree(symbol_values)
        line_analyzer = LineAnalyzer(abt, env)
        term_analyzer = TermAnalyzer(abt, env)
        term_analyzer.solve_var_names()
        VTree(abt).view(viewf=lambda i, data:"{} {}".format(data["symbol"],data.get("name")), path="./solve_var_names.html" )
        term_analyzer.solve_type()
        VTree(abt).view(viewf=lambda i, data:"{} {}".format(data["symbol"],data.get("sort")), path="./solve_type.html" )
        term_analyzer.solve_varT_list()
        VTree(abt).view(viewf=lambda i, data:"{} {}".format(data["symbol"],tostr(data.get("varTs"))), path="./solve_varT_list.html" )
        term_analyzer.solve_var()
        VTree(abt).view(viewf=lambda i, data:"{} {}".format(data["symbol"],tostr(data.get("appear"))), path="./solve_var.html" )
        #term_analyzer.sort_deduce()
        #VTree(abt).view(viewf=lambda i, data:"{} {}".format(data["symbol"],tostr(data.get("sort"))), path="./sort_deduce.html" )


if __name__ == "__main__":
    test()