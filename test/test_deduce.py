import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import LineParser, LineAnalyzer, Context, TermAnalyzer, LasyConverter, Sort, Var
from line_reader import LineReader
from Structure import VTree
from utils import tostr, basiccopy

def test():

    lines_path = "./sentences/lines_for_deduce.txt"
    line_parser = LineParser("../grammars/line.txt")
    env = Context()
    env.mode = "Proof"
    # Q : Func[M,Prop]
    env.add_var("Q", Sort("Func",["M","Prop"]), "any")
    # P : Func[M,Prop]
    env.add_var("P", Sort("Func",["M","Prop"]), "any")
    # p -> q
    #¬ p ∨ q
    #( (∀ x : M, (Q x )) ∨ (∀ x : M, (P x )) )
    lines =  list(LineReader(lines_path))
    template = line_parser.build_tree(line_parser.lexical(lines[0]))
    # p -> q
    templates = [template]
    # ¬ p ∨ q
    conclusion = line_parser.build_tree(line_parser.lexical(lines[1]))
    # ( (∀ x : M, (Q x )) ∨ (∀ x : M, (P x )) )
    p = line_parser.build_tree(line_parser.lexical(lines[2]))
    q = line_parser.build_tree(line_parser.lexical(lines[3]))
    # line to term
    #p.view("production")
    p = p.copy_subtree(p.get_child(p.root,1)[0],basiccopy)
    print(p.totext(" "))
    q = q.copy_subtree(q.get_child(q.root,1)[0],basiccopy)
    TermAnalyzer(p,env).solve()
    TermAnalyzer(q,env).solve()
    presumption = line_parser.build_tree(line_parser.lexical(lines[4]))
    
    result = LasyConverter.deduce([presumption],templates,{"p":p,"q":q},conclusion)
    print(result)

if __name__ == "__main__":
    test()

