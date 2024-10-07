import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import LineParser, Switcher, Context, TermAnalyzer, LasyConverter, Sort, Var
from line_reader import LineReader
from Structure import VTree
from utils import tostr, basiccopy
from abtree import ABTree

def test():
    lines_path = "./sentences/lines_for_axiom.txt"
    line_parser = LineParser("../grammars/line.txt")

    env = Context()
    env.mode = "Assert"
    for line in LineReader(lines_path):
        name, func = line.split("&")
        print(name, func)
        line = f"one {name} := {func}"
        abt = line_parser.parse(line)
        TermAnalyzer(abt,env).solve()
        VTree(abt).view(viewf= lambda i,d :str(d.get("sort").__str__()if  d.get("sort") else None) + str(d.get("symbol")))
        Switcher(abt,env).switch()
    

    abt = line_parser.parse("one N : Set,")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    abt = line_parser.parse("one R : Func[Tuple[N,N,],N,],")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    abt = line_parser.parse("one _0:N,_1 : N,")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    abt = line_parser.parse("∀  x: N, (R (x,_0,)) = x")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    abt = line_parser.parse("one _2 := { _1,}")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    abt = line_parser.parse("one _3 := { _1,_2,{_2,},}")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    abt = line_parser.parse("one p := Power _3")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    env.mode = "Global"
    abt = line_parser.parse("theorem ∀ p : Prop, q: Prop, p ∧ q -> p")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    print(env.mode)
    abt = line_parser.parse("any p : Prop, q: Prop,")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    abt = line_parser.parse("assume p ∧ q")
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    pre = [env.assumptions[-1]]

    leafs = list(pre[0].iter_leafs())
    p , q = leafs[0][0], leafs[2][0]
    p,q = LasyConverter(abt).select([p]),LasyConverter(abt).select([q])
    print(p,q)
    p,q = abt.copy_subtree(p,basiccopy),abt.copy_subtree(q,basiccopy)
    temp = line_parser.parse("p ∧ q")
    conclusion = LasyConverter(abt).deduce(pre,[temp],name_t={"p":p,"q":q},conclusion=p)
    abt = line_parser.parse(conclusion)
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    line = LasyConverter(abt).conclude(pre,abt)
    abt = line_parser.parse(line)
    TermAnalyzer(abt,env).solve()
    Switcher(abt,env).switch()
    print(env.conclusions[-1].totext(" "))
    print(env.assumptions[-1].totext(" "))

if __name__ == "__main__":
    test()

