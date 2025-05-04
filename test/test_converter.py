import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from semantic import LineParser, LineAnalyzer, Context, TermAnalyzer, TermConverter, Sort, Var
from line_reader import LineReader
from Structure import VTree
from utils import tostr, basiccopy

def test():
    from resource_service import ResourceService
    lines_path = ResourceService.get("test/sentences/lines_for_bracket.txt")
    line_parser = LineParser(ResourceService.get("grammars/line.txt"))
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

        line = TermConverter(abt).rename("x", "y")
        print(line)
        symbol_values = line_parser.lexical(line)
        abt = line_parser.build_tree(symbol_values)
        TermAnalyzer(abt, env).solve()
        
        brace = line_parser.build_tree(line_parser.lexical("(t)"))
        tsymbol_values = line_parser.lexical("p->q")
        tabt = line_parser.build_tree(tsymbol_values)
        print(tostr(tabt.totext(" ")))
        line = TermConverter(tabt).fillin(brace, {"t": tabt})
        tabt = line_parser.build_tree(line_parser.lexical(line))
        tabt = tabt.copy_subtree(tabt.get_child(tabt.root, 1)[0])
        print(tostr(tabt.totext(" ")))
        abt = abt.copy_subtree(abt.get_child(abt.root,1)[0], basiccopy)

        line = TermConverter(abt).instance({"y": tabt})
        print(line)
        abt = line_parser.build_tree(line_parser.lexical(line))
        k, x = list(abt.iter_leafs())[18]
        print(tostr(x))
        j = TermConverter(abt).select([k])
        subt = abt.copy_subtree(j,basiccopy)
        print(tostr(subt.totext(" ")))
        line = TermConverter(abt).replace(j, brace)
        print(line)
        abt = line_parser.build_tree(line_parser.lexical(line))
        env.mode = "Proof"
        env.add_var("p", Sort("Prop"), "any")
        env.add_var("q", Sort("Prop"), "any")
        TermAnalyzer(abt, env).solve()
        abt = abt.copy_subtree(abt.get_child(abt.root,1)[0], basiccopy)
        line = TermConverter(abt).instance({"a": TermConverter(brace).line2term(),"b":TermConverter(brace).line2term()})
        print(line)
        q = Var("qq", Sort("Prop"), "any")
        p = Var("pp", Sort("Prop"), "any")
        abt = line_parser.build_tree(line_parser.lexical(line))
        term = abt.copy_subtree(abt.get_child(abt.root,1)[0], basiccopy)
        TermAnalyzer(term, env).solve()
        line = TermConverter(abt).introduce(term, {"q": q,"p":p}, "∀")
        print(line)

        # 建立辅助项
        assist  = line_parser.parse("p -> q")
        print("assist : ", assist.totext(" "))
        # 选择 (pp - > pp)
        abt = line_parser.parse(line)
        i = TermConverter(abt).select_by_pos([9])
        term = abt.copy_subtree(i, basiccopy)
        print("(pp -> pp)" , term.totext(" "))
        # 用 (assist 替换)
        result = TermConverter(abt).regular_replace(i, assist)
        print(line_parser.parse(result).totext(" "))




if __name__ == "__main__":
    test()