import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import LineParser, LineAnalyzer, Context, TermAnalyzer, LasyConverter, Sort, Var
from line_reader import LineReader
from Structure import VTree
from utils import tostr, basiccopy
from abtree import ABTree

def test():
    lines_path = "./sentences/lines_for_bracket.txt"
    line_parser = LineParser("../grammars/line.txt")
    lines = list(LineReader(lines_path))
    line = lines[0]
    term = line_parser.parse(line)
    i = LasyConverter(term).select([list(term.iter_leafs())[6][0]])
    line, off_abt = LasyConverter(term).off_bracket(i)
    print(line)
    term = line_parser.parse(line)
    print(ABTree.equal(term,off_abt))
    i = LasyConverter(term).select([list(term.iter_leafs())[3][0]])
    print(term.copy_subtree(i,basiccopy).totext(" "))
    line = LasyConverter(term).on_bracket(i)
    print(line)


if __name__ == "__main__":
    test()

