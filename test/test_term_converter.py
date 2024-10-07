import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import LineParser, LineAnalyzer, Context, TermAnalyzer, TermConverter, Sort, Var
from line_reader import LineReader
from Structure import VTree
from utils import tostr, basiccopy

def test():
    lines_path = "./sentences/lines_for_converter.txt"
    line_parser = LineParser("../grammars/line.txt")
    env = Context()
    # 验证与环境切换无关的功能时，手动配置环境
    env.add_var("ADD", Sort("Set"), "one")
    env.add_var("R", Sort("Set"), "one")
    for line in LineReader(lines_path):
        input("to next line ?")
        print(line)
        symbol_values = line_parser.lexical(line)
        abt = line_parser.build_tree(symbol_values)
        line_analyzer = LineAnalyzer(abt, env)
        term_analyzer = TermAnalyzer(abt, env)
        term_analyzer.solve()

        line = TermConverter.rename(abt, "x", "y")
        print(line)
        assert line == "∀ y : ADD , ∃ a : R , b : R , c : R , y = ( ( a , b , ) , c , )"
        symbol_values = line_parser.lexical(line)
        abt = line_parser.build_tree(symbol_values)
        TermAnalyzer(abt, env).solve()
        
        brace = line_parser.build_tree(line_parser.lexical("(t)"))
        tsymbol_values = line_parser.lexical("p->q")
        tabt = line_parser.build_tree(tsymbol_values)
        print(tostr(tabt.totext(" ")))
        assert tostr(tabt.totext(" ")) == "p -> q"
        line = TermConverter.regular_fillin(brace, {"t": tabt})
        assert line == "( ( p -> q ) )"
        tabt = line_parser.build_tree(line_parser.lexical(line))
        print(tostr(tabt.totext(" ")))
        
        abt = abt.copy_subtree(abt.get_child(abt.root,1)[0], basiccopy)

        line = TermConverter.regular_instance(abt, {"y": tabt})
        print(line)
        assert line == "∃ a : R , b : R , c : R , ( ( ( p -> q ) ) ) = ( ( a , b , ) , c , )"
        abt = line_parser.build_tree(line_parser.lexical(line))
        k, x = list(abt.iter_leafs())[22]
        print(tostr(x))
        assert x["value"] == "="
        j = TermConverter.select(abt, [k])
        subt = abt.copy_subtree(j,basiccopy)
        print(tostr(subt.totext(" ")))
        assert tostr(subt.totext(" ")) == "( ( ( p -> q ) ) ) = ( ( a , b , ) , c , )"
        line = TermConverter.regular_replace(abt, j, tabt)
        print(line)
        abt = line_parser.build_tree(line_parser.lexical(line))
        env.mode = "Proof"
        env.add_var("p", Sort("Prop"), "any")
        env.add_var("q", Sort("Prop"), "any")
        abt.view()
        TermAnalyzer(abt, env).solve()
        abt = abt.copy_subtree(abt.get_child(abt.root,1)[0], basiccopy)
        line = TermConverter.regular_instance(abt, {"a": brace,"b":brace})
        print(line)
        q = Var("qq", Sort("Prop"), "any")
        p = Var("pp", Sort("Prop"), "any")
        abt = line_parser.build_tree(line_parser.lexical(line))
        term = abt.copy_subtree(abt.get_child(abt.root,1)[0], basiccopy)
        TermAnalyzer(term, env).solve()
        line = TermConverter.introduce(term, {"q": q,"p":p}, "∀")
        print(line)

        # 建立辅助项
        assist  = line_parser.parse("p -> q")
        print("assist : ", assist.totext(" "))
        # 选择 (pp - > pp)
        abt = line_parser.parse(line)
        i = TermConverter.select_by_pos(abt, [9])
        term = abt.copy_subtree(i, basiccopy)
        print("(pp -> pp)" , term.totext(" "))
        # 用 (assist 替换)
        result = TermConverter.regular_replace(abt, i, assist)
        print(line_parser.parse(result).totext(" "))




if __name__ == "__main__":
    test()