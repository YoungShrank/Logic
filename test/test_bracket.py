import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from semantic import LineParser, LineAnalyzer, Context, TermAnalyzer, TermConverter, Sort, Var
from line_reader import LineReader
from Structure import VTree
from utils import tostr, basiccopy
from abtree import ABTree

def test():
    from resource_service import ResourceService
    lines_path = ResourceService.get("test/sentences/lines_for_bracket.txt")
    line_parser = LineParser(ResourceService.get("grammars/line.txt"))
    lines = list(LineReader(lines_path))
    line = lines[0]
    term = line_parser.parse(line)
    i = TermConverter.select(term, [list(term.iter_leafs())[6][0]])
    line, off_abt = TermConverter.off_bracket(term, i)
    print(line)
    term = line_parser.parse(line)
    print(ABTree.equal(term,off_abt))
    i = TermConverter.select(term, [list(term.iter_leafs())[3][0]])
    print(term.copy_subtree(i,basiccopy).totext(" "))
    line = TermConverter.on_bracket(term, i)
    print(line)


if __name__ == "__main__":
    test()

