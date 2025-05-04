import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from semantic import LineParser, Switcher, Context, TermAnalyzer, TermConverter, Sort, Var
from line_reader import LineReader
from Structure import VTree
from utils import tostr, basiccopy
from abtree import ABTree

def test():
    from resource_service import ResourceService
    predefine_path = ResourceService.get("test/sentences/predefine.txt")
    lines_path = ResourceService.get("test/sentences/lines_for_eq_replace.txt")
    line_parser = LineParser(ResourceService.get("grammars/line.txt"))
    env = Context()
    abt = line_parser.parse("assert")
    Switcher(abt, env).switch()
    for line in LineReader(predefine_path):
        print(line)
        abt = line_parser.parse(line)
        TermAnalyzer(abt, env).solve()
        Switcher(abt, env).switch()
    abt = line_parser.parse(";")
    Switcher(abt, env).switch()
    
    for line in LineReader(lines_path):
        print(line)
        abt = line_parser.parse(line)
        TermAnalyzer(abt, env).solve()
        Switcher(abt, env).switch()
    x = line_parser.parse("x")
    x = x.copy_subtree(x.get_childs(x.root)[0][0], basiccopy)
    TermAnalyzer(x, env).solve()
    line = TermConverter(env.get_axiom("theorem_name").copy(basiccopy)).instance({"x":x})
    abt = line_parser.parse((line))
    env.append_conclusion(TermConverter(abt).line2term())
    abt = env.conclusions[-1].copy(basiccopy)
    i = TermConverter(abt).select_by_pos([10])
    line = TermConverter(abt).on_bracket(i)
    abt = line_parser.parse(line)
    env.append_conclusion(TermConverter(abt).line2term())
    abt = env.conclusions[-2].copy(basiccopy)
    eq_abt = env.conclusions[-1].copy(basiccopy)
    i = TermConverter(abt).select_by_pos([3])
    line = TermConverter(abt).equal_replace(eq_abt, abt, i, "right")
    print(line)
    abt = line_parser.parse(line)
    env.append_conclusion(TermConverter(abt).line2term())
    abt = env.conclusions[-1].copy(basiccopy)
    TermAnalyzer(abt, env).solve()
    line = TermConverter(abt).introduce(abt, {"x":env.get_var("x")},"∀")
    print(line)
    abt = line_parser.parse(line)
    env.append_conclusion(TermConverter(abt).line2term())
    abt = line_parser.parse("qed")
    Switcher(abt, env).switch()

 

if __name__ == "__main__":
    test()

