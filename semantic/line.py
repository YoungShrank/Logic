import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from words import Word,shift,union
from lrparser import LRParser,LR1Table
from grammar import Grammar
from abtree import ABTree

from context import Context, Var
from sort import Sort, SortTuple, Func
from utils import basiccopy



class LineParser:
    def __init__(self,grammar_path:str) -> None:
        """
        项的语义分析类
        - grammar_path: 语法文件路径
        """
        self.grammar = Grammar(S="<line>")
        self.grammar.from_file(grammar_path)
        self.grammar.extend(end="#")
        self.grammar.init(solve=True)
        priority  = ["=","∈","¬","∧","∨","<->","->","∀","∃","λ",""]
        associativity = {"¬":"r","∧":"l","∨":"l","<->":"r","->":"r","∀":"r","∃":"r","λ":"r","":"r"}
        table = LR1Table(self.grammar,ambiguity=True,priority=priority,associativity=associativity)
        self.lrparser = LRParser(table)
    def patterns(self):
        """
        词法的正则式
        # returns
        - pattern: 正则表达式
        - vask: 词法分析的保留字（一字一类）
        - key2type: key和symbol的映射
        """
        pattern = {
        "op":union(["=","∈","¬","∧","∨","<->","->","∀","∃","λ",":="]),
        "del": "[{}]".format(shift("(){}<>[],;:'.*&^%$#@!~|")),
        "key":union(["one","any","theorem","lemma","qed","assert","assume"]), #关键字
        "var":r"[a-zA-Z_][_a-zA-Z0-9]*",
        "char" :r"[\+\-⊥]", # 符号
        "num":r"[0-9]+",
        "space":r"\s+",
        "other":r"."
        }
        vask = {"op","del","key"}
        key2type = {
            "var":"<var>",
            "char" :"<var>", # 符号
            "num":"<num>",
            "space":"<space>",
            "other":"other"
        }
        return pattern,vask,key2type
    # 词法分析
    def lexical(self,text:str) -> list[tuple[str,str]]:
        """
        词法分析
        - text: 文本
        # returns
        - symbol_values: 词法分析结果[(symbol,value)]
        """
        pattern,vask,key2type = self.patterns()
        word = Word(text,patterns=pattern,vask=vask,key2type=key2type)
        value_types = word.parse_all()
        symbol_values = [(t,v) for v,t in value_types ]
        return symbol_values
        #构建语法分析树
    def build_tree(self,symbol_values:list[tuple[str,str]]) -> ABTree:
        """
        构建语法分析树
        - symbol_values: 词法分析结果[(symbol,value)]
        # returns
        - abt: 语法分析树
        """ 
        abt = self.lrparser.parse(symbol_values,meaning=True)
        abt.init_parents()
        return abt
    def parse(self,text:str) -> ABTree:
        """
        语法分析，将文本解析为语法分析树
        - text: 文本
        # returns
        - abt: 语法分析树
        """ 
        symbol_values = self.lexical(text)
        abt = self.build_tree(symbol_values)
        return abt

class TermAnalyzer:
    def __init__(self, abt: ABTree, env : Context):
        """
        term的语义器
        - abt: term的语法分析树
        - env: 推理机上下文
        """
        self.abt = abt
        self.env = env
    def solve(self):
        """
        计算变量语义，并且完成类型推断
        """
        self.solve_var_names()
        self.solve_type()
        self.solve_varT_list()
        self.solve_var()
        self.sort_deduce()
    def solve_var(self):
        """
        变量的语义分析<term> <var>  或者 <var>
        语义包含： 变量数学类型，变量名
        """
        # 自顶向下，求约束变元及约束出现，同时解决自由变元
        for i, node in self.abt.iter("pre"):
            # 继承
            node["bound"] = {}
            node["bound_for_appear"] = {} #  name : i
            parent_bound = {}
            parent_bound_for_appear = {}
            if i != self.abt.root:
                parent_bound = self.abt.get_vex(self.abt.parents[i])["bound"]
                node["bound"].update(parent_bound)
                parent_bound_for_appear = self.abt.get_vex(self.abt.parents[i])["bound_for_appear"]
                node["bound_for_appear"].update(parent_bound_for_appear)
            production = node.get("production")
            if (production == "<term> ∀ <varT_list> <term>".split() or  #约束变元
                production == "<term> ∃ <varT_list> <term>".split() or
                production == "<func> λ <varT_list> . <term>".split()):
                j, varT_list = self.abt.get_child(i,2)
                varTs = varT_list["varTs"]
                node["bound"].update(varTs)
                node["appear"] = {name:set() for name, sort in varTs}
                for name, sort in varTs:
                    node["bound_for_appear"][name] = i
            elif production == "<set> { <term> | <varT_list> | <term> }".split():
                j, varT_list = self.abt.get_child(i, 4)
                j1, t1 = self.abt.get_child(i, 2)
                j2, t2 = self.abt.get_child(i, 6)
                varTs = varT_list["varTs"]
                t1["bound"] = parent_bound | dict(varTs)
                t2["bound"] = parent_bound | dict(varTs)
            elif production == "<set> { <varT> | <term> }".split():
                j, varT = self.abt.get_child(i, 2)
                k , t = self.abt.get_child(i, 4)
                varTs = varT["varTs"]
                t["bound"] = parent_bound | dict(varTs)
            elif production == "<term> <var>".split():
                j, var = self.abt.get_child(i, 1)
                if var["name"] in node["bound_for_appear"]:
                    k = node["bound_for_appear"][var["name"]]
                    self.abt.get_vex(k)["appear"][var["name"]].add(i)
            if node.get("name"): #计算变元类型
                name = node["name"]
                if name in node["bound"]: #约束
                    sort = node["bound"][name]
                else:
                    var = self.env.get_var(name)
                    if var:
                        sort = var.sort
                    else:
                        sort = Sort("Set") # 暂时这么整
                node["sort"] = sort
                if sort.name not in self.env.sort: #自定义类型
                    var = self.env.get_var(sort.name)
                    if var :
                        if var.sort.name == "Set" and var.sort.subsorts: # x : Set[A,]
                            node["sort"] =  var.sort.subsorts[0]
                    else: # 约束
                        parent_sort = node["bound"][sort.name]
                        if parent_sort.name == "Set" and parent_sort.subsorts:
                            node["sort"] = parent_sort.subsorts[0]

        # 自底向上，获得自由变量的自由出现
        for i, node in self.abt.iter("post"):
            production = node.get("production")
            if production == ["<term>","<var>"]: #变量
                j, var = self.abt.get_child(i,1)
                if var["name"] not in node["bound"]: #自由
                    node["free"] = {var["name"]:{j}}
            elif production : #非叶子
                children = self.abt.get_childs(i)
                node["free"] = {}
                for j, child in children:
                    if child.get("free"):
                        for k, v in child["free"].items():
                            node["free"].setdefault(k, set())
                            node["free"][k].update(v)



    def solve_var_names(self):
        """
        求出所有变量的 名 (标识符 节点语义解析)
        """
        for i, node in self.abt.iter("post"):
            if node.get("symbol") == "<var>":
                node["name"] = node["value"]
            else:
                production = node.get("production")
                if production and production[1:] == ["<var>"]:
                    j, var = self.abt.get_child(i,1)
                    node["name"] = var["value"]
    def solve_type(self):
        """
        解析类型代表的 Sort (type /type_list 节点语义解析)
        """
        for i, node in self.abt.iter("post"):
            production = node.get("production")
            if production is None: #叶子节点
                continue
            children = self.abt.get_childs(i)
            production = " ".join(production)
            if production == "<type> <var>":
                j, var = children[0]
                node["sort"] = Sort(var["name"])
            elif production == "<type_list> <type> ,":
                j, type_ = children[0]
                node["sorts"] = [type_["sort"]]
            elif production == "<type_list> <type_list> <type> ,":
                j, type_list = children[0]
                k, type_ = children[1]
                node["sorts"] = type_list["sorts"] + [type_["sort"]]
            elif production == "<type> <var> [ <type_list> ]":
                j, var = children[0]
                k, type_list = children[2]
                node["sort"] = Sort(var["name"],type_list["sorts"])

    def solve_varT_list(self):
        """
        解析 <varT_list> 的语义 (name, type)/ (name, var_node_index)
        # returns
        [ (var,type) ]
        """
        for i, node in self.abt.iter("post"):
            production = node.get("production")
            if production == "<varT_list> <varT> ,".split():
                j, varT = self.abt.get_child(i,1)
                node["varTs"] =  varT["varTs"]
                node["varTs_i"] =  varT["varTs_i"] # var的索引
            elif production == "<varT_list> <varT_list> <varT> ,".split():
                k, varT_list = self.abt.get_child(i,1)
                j, varT = self.abt.get_child(i,2)
                node["varTs"] = varT_list["varTs"]+  varT["varTs"]
                node["varTs_i"] = varT_list["varTs_i"]+  varT["varTs_i"]
            elif production == "<varT> <var> : <type>".split():
                k, var  = self.abt.get_child(i,1)
                j, sort = self.abt.get_child(i,3)
                node["varTs"] = [ (var["name"], sort["sort"]) ]
                node["varTs_i"] = [ (var["name"], k) ]


    def sort_deduce(self):
        """
        类型推断，自底向上
        """
        for i, node in self.abt.iter("post"):
            production = node.get("production")
            if production is None: #叶子节点
                continue
            production = " ".join(production)
            children = self.abt.get_childs(i)
            match production:
                case "<term> <var>" \
                    | "<term> <tuple>" \
                    | "<term> <set>" \
                    | "<term> <func>" \
                    | "<term> <varT>":
                    j, var = children[0]
                    node["sort"] = var["sort"]
                case "<term_list> <term> ,":
                    j, t = children[0]
                    node["terms"] = [(j, t["sort"])]
                case "<term_list> <term_list> <term> ,":
                    j, ts = children[0]
                    k, t = children[1]
                    node["terms"] = ts["terms"]+[(k, t["sort"])]
                case "<set> { <term_list> }":
                    j, ts = children[1]
                    node["sort"] = Sort("Set", ["Math"])
                case "<term> <term> = <term>":
                    j, t1 = children[0]
                    k, t2 = children[2]
                    node["sort"] = Sort("Prop")
                case "<term> <term> ∈ <term>":
                    j, t1 = children[0]
                    k, t2 = children[2]
                    assert t2["sort"].name == ("Set")
                    node["sort"] = Sort("Prop")
                case "<term> <term> <term>":
                    j, t1 = children[0]  # (func, A, B)
                    k, t2 = children[1]  # A
                    t1 : dict[str, Func]
                    t2 : dict[str, Sort]
                    print(t1["sort"], t2["sort"])
                    assert t1["sort"].name == "Func"
                    assert Sort.is_super(t1["sort"].subsorts[0] , t2["sort"])
                    node["sort"] = t1["sort"].subsorts[1]
                case  "<term> <term> -> <term>" | "<term> <term> ∨ <term>" | "<term> <term> ∧ <term>" | "<term> <term> <-> <term>":
                    j, t1 = children[0]
                    k, t2 = children[2]
                    assert t1["sort"].name == "Prop" and  t2["sort"].name == "Prop"
                    node["sort"] = Sort("Prop")
                case "<term> ¬  <term>":
                    j, t1 = children[1]
                    assert t1["sort"].name == "Prop"
                    node["sort"] = Sort("Prop")
                case "<term> ∀ <varT_list> <term>" |  "<term> ∃ <varT_list> <term>":
                    j, t = children[2]
                    assert t["sort"].name == "Prop"
                    node["sort"] = Sort("Prop")
                case "<term> ( <term> )":
                    j, t = children[1]
                    node["sort"] = t["sort"]
                case "<term> <varT>":
                    node["sort"] = Sort("Prop")
                case "<func> λ <varT_list> . <term>":
                    j, t = children[3]
                    k, varT_list = children[1]
                    varTs = varT_list["varTs"]
                    if len(varTs) == 1:
                        in_sort = varTs[0][1]
                    elif len(varTs) > 1:
                        in_sort = SortTuple( [t for k, t in varTs])
                    node["sort"] = Func(in_sort, t["sort"])
                case "<varT> <var> : <type>":
                    j, var = children[0]
                    k, sort = children[2]
                    node["sort"] = Sort("Prop")
                case "<tuple> ( <term_list> )":
                    j, ts = children[1]
                    node["sort"] = SortTuple([t for k, t in ts["terms"]])
                case "<set> { <term> | <varT_list> | <term> }":
                    j1, t1 = children[1]
                    j2, t2 = children[5]
                    assert t2["sort"].name == "Prop"
                    node["sort"] = Sort("Set", [t1["sort"]])
                case "<set> { <varT> | <term> }":
                    _, varT = children[1]
                    j, t = children[3]
                    assert t["sort"].name == "Prop"
                    node["sort"] = Sort("Set", [varT["varTs"][0][1]])
class Switcher:
    def __init__(self, abt: ABTree, env: Context):
        """
        环境切换
        - abt: switcher的语法分析树
        - env: 环境
        """
        self.abt = abt
        self.env = env
    def switch(self) -> None:
        """
        环境切换
        """
        i, child = self.abt.get_child(self.abt.root, 1)
        print("switch")
        production = " ".join(child["production"])
        cchilds = self.abt.get_childs(i)
        print(production)
        match production:
            case "<assume> assume <term>": #假设
                j, t = cchilds[1]
                term = self.abt.copy_subtree(j,basiccopy)
                self.env.assume(term)
            case "<declare> any <varT_list>":  # 声明变量
                j, varT_list = cchilds[1]
                varTs = varT_list["varTs"]
                for var, type_ in varTs:
                    self.env.add_var(var, type_, "any")
                print(self.env.globals)
                print(self.env.locals)
            case "<declare> one <varT_list>":  # 声明变量
                j, varT_list = cchilds[1]
                varTs = varT_list["varTs"]
                for var, type_ in varTs:
                    self.env.add_var(var, type_, "one")
                print(self.env.globals)
                print(self.env.locals)
            case "<assign> one <var> := <term>":
                j, var = cchilds[1]
                k, t = cchilds[3]
                type_ = t["sort"]
                print(type_)
                self.env.add_var(var["name"], type_, "one", self.abt.copy_subtree(k,basiccopy))

            case "<assert> assert": #断言模式
                self.env.assert_()
                print("begin assert")
            case "<theorem> theorem <term>" | "<theorem> lemma <term>": #证明模式
                j, t = cchilds[1]
                self.env.proof(self.abt.copy_subtree(j))
                print("begin proof",self.env.theorem.totext())
            case "<qed> qed": #退出证明
                print("qed",self.env.theorem.totext(" "),self.env.conclusions[-1].totext(" "))
                self.env.qed()
            case "<end> ;": #退出断言
                self.env.end_assert()
                print("end assert")
        if child["symbol"] == "<term>":
            if self.env.mode == "Proof": #结论
                self.env.append_conclusion(self.abt.copy_subtree(i,basiccopy))
            elif self.env.mode == "Assert": #断言
                self.env.add_axiom("theorem_name",self.abt.copy_subtree(i,basiccopy))
            elif self.env.mode == "Global":
                print("waring: term in global mode will be ignored")




class LineAnalyzer:
    def __init__(self, abt: ABTree, env: Context):
        """
        line的语义器
        - abt: line的语法分析树
        """
        self.abt = abt
        self.env = env
        self.switcher = Switcher(abt, env)
    def get_line_type(self) -> list[str]:
        """
        获取line的类型
        # returns
        - line_type: line的类型
        """
        root: dict[str, list[str]] = self.abt.get_vex(self.abt.root)
        line_type = root["production"][1:]
        return line_type
    def get_specific(self) -> ABTree:
        """
        获得具体的line，也就是line的子树
        如 line := declare
        具体的line为 declare树
        """
        i = self.abt.get_child(self.abt.root, 1)
        specific = self.abt.copy_subtree(i, basiccopy)
        return specific
    def env_switch(self) -> None:
        """
        环境切换
        """
        self.switcher.switch()

        
        
    

            
def test_term_parser():
    """
    测试
    """
    from resource_service import ResourceService
    grammar_path = ResourceService.get("grammars/line.txt")
    text = "one prop_a := ¬(p->q)->{x : R|(f x)= y }"
    parser = LineParser(grammar_path)
    symbol_values = parser.lexical(text)
    print(symbol_values)
    tree = parser.build_tree(symbol_values)
    print(tree)
    from Structure import VTree
    vtree = VTree(tree)
    vtree.view()
    print(tree.totext())
    print(tree.tosymbols())
def test_analyzer():
    """
    测试 语义分析
    """
    from resource_service import ResourceService
    grammar_path = ResourceService.get("grammars/line.txt")
    text = "one prop_a := ¬(p->q)->{x : R|(f x)= y }"
    parser = LineParser(grammar_path)
    symbol_values = parser.lexical(text)
    tree = parser.build_tree(symbol_values)
    env = Context()
    analyzer = LineAnalyzer(tree, env)
    line_type = analyzer.get_line_type()
    print(line_type)

    
if __name__ == "__main__":
    #test_term_parser()
    #test_analyzer()
    #test_fillin()
    pass