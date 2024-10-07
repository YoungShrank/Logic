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
        求出所有变量的 名
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
        解析类型代表的 Sort
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
        解析 <varT_list> 的语义
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

            
class Converter():
    """
    项变换器
    """
    def __init__(self,abt:ABTree):
        """
        - abt: 项的语法分析树
        """
        self.abt = abt
    def select(self, leafs:list[int]):
        """
        选择项,选择规则是，叶子的最近公共<term>祖先
        - leafs: 叶子的id
        # returns
        - ancestor: 祖先节点id
        """
        ancestors = self.abt.common_ancestors(leafs)
        for ancestor in ancestors:
            node = self.abt.get_vex(ancestor)
            if node.get("symbol") == "<term>":
                return ancestor
    def substitute(self,vars:list[int],t:ABTree):
        """
        代入项
        t 必须为 (t)
        - var: 变量（term:=var）的Id
        - t: 待代入的项
        """
        for i in vars:
            self.abt.substitute(i,t.copy_subtree(t.root))
    def replace(self,t0i,t1:ABTree):
        """
        替换项
        t1 必须为 (t)
        - t0i: 被替换的项的id
        - t1: 待替换的项
        """
        self.abt.substitute(t0i,t1.copy())
    def rename(self,x:str,y:str):
        """
        变量重命名
        - x:原名
        - y:新名
        """
        pass

    def instance(self,name_t:dict[str, ABTree]):
        """
        量词消去/或者函数应用
        t 必须为 (t)
        - name_t: {name:t}
        """
        node = self.abt.get_vex(self.abt.root)
        production = " ".join(node["production"])
        match production:
            case "<term> ∀ <varT_list> <term>" :
                j, term = self.abt.get_child(self.abt.root, 2)
            case "<term> ∃ <varT_list> <term>":
                j, term = self.abt.get_child(self.abt.root, 2)
            case "<term> λ <varT_list> . <term>":
                j, term = self.abt.get_child(self.abt.root, 3)
        for x, t in name_t.items():
            appears = node["appear"][x]
            for i in appears:
                self.abt.substitute(i,t.copy())
        return self.abt.copy_subtree(j)
class LasyConverter():
    """
    不涉及附加语义的语义转换器，符号级/语法级的语义转换（也就是只要语法树结构/符号序列相同）
    """
    def __init__(self,abt:ABTree):
        self.abt = abt
    def instance(self,name_t:dict[str, ABTree]):
        """
        量词消去/或者函数应用
        t 必须为 (t)
        - name_t: {name:t}
        """
        node = self.abt.get_vex(self.abt.root)
        production = " ".join(node["production"])
        match production:
            case "<term> ∀ <varT_list> <term>" :
                j, term = self.abt.get_child(self.abt.root, 3)
            case "<term> ∃ <varT_list> <term>":
                j, term = self.abt.get_child(self.abt.root, 3)
            case "<term> λ <varT_list> . <term>":
                j, term = self.abt.get_child(self.abt.root, 4)
        for x, t in name_t.items():
            assert  LasyConverter.into_able(t)
            appears = node["appear"][x]
            for i in appears:
                self.abt.substitute(i,t.copy(basiccopy))
        return self.abt.copy_subtree(j,basiccopy).totext(" ")
    def regular_instance(self,name_t:dict[str, ABTree]):
        """
        规范化的量词消去/或者函数应用，采用regular_replace
        - name_t: {name:t}
        """
        node = self.abt.get_vex(self.abt.root)
        production = " ".join(node["production"])
        match production:
            case "<term> ∀ <varT_list> <term>" :
                j, term = self.abt.get_child(self.abt.root, 3)
            case "<term> ∃ <varT_list> <term>":
                j, term = self.abt.get_child(self.abt.root, 3)
            case "<term> λ <varT_list> . <term>":
                j, term = self.abt.get_child(self.abt.root, 4)
        for x, t in name_t.items():
            appears = node["appear"][x] #出现位置
            for i in appears:
                self.regular_replace(i,t.copy(basiccopy))
        return self.abt.copy_subtree(j,basiccopy).totext(" ")
    def rename(self,x:str,y:str):
        """
        变量重命名
        - x:原名
        - y:新名
        """
        node = self.abt.get_vex(self.abt.root)
        production = " ".join(node["production"])
        match production:
            case "<term> ∀ <varT_list> <term>" :
                j, term = self.abt.get_child(self.abt.root, 3)
            case "<term> ∃ <varT_list> <term>":
                j, term = self.abt.get_child(self.abt.root, 3)
            case "<term> λ <varT_list> . <term>":
                j, term = self.abt.get_child(self.abt.root, 4)
        for i, node in self.abt.iter(order="post"):
            if node.get("symbol") == "<var>" and node["value"] == x:
                node["value"] = y
        return self.abt.copy(basiccopy).totext(" ")
    def select(self, leafs:list[int]):
        """
        选择项,选择规则是，叶子的最近公共<term>祖先
        - leafs: 叶子的id
        # returns
        - ancestor: 祖先节点id
        """
        ancestors = self.abt.common_ancestors(leafs)
        for ancestor in ancestors:
            node = self.abt.get_vex(ancestor)
            if node.get("symbol") == "<term>":
                return ancestor
    def select_by_pos(self, poses:list[int]):
        """
        选择项，但是poses是叶子的序号(0,1,..)
        - poses: 叶子的序号
        # returns
        - ancestor: 祖先节点id
        """
        all_leafs = [i for i,_ in self.abt.iter_leafs()]
        leafs = [all_leafs[i] for i in poses]
        return self.select(leafs)
    @staticmethod
    def into_able(t: ABTree):
        """
        判断是否可直接代入，即(t)或者 var
        - t : 待判断的 <term>
        """
        t_production = t.get_vex(t.root).get("production")
        return " ".join(t_production) in ["<term> ( <term> )", "<term> <var>"]

    def substitute(self,vari:int,t:ABTree):
        """
        代入项
        t 必须为 (t)
        - vari: 变量（term:=var）的Id
        - t: 待代入的项
        """
        
        self.abt.substitute(vari,t.copy(basiccopy))
        return self.abt.totext(" ")

    def equal_replace(self,equal_t:ABTree, t:ABTree, t1_id:int, side:str = "left"):
        """
        等值替换, t(t1→(t2))
        - equal_t: 等式 (t2) = (t1) 或者(t1) = (t2)
        - t : 待替换的项
        - t1_id: t1的id
        - side: t1所在的边
        """
        equal_root = equal_t.get_vex(equal_t.root)
        production = equal_root.get("production") 
        print(production)
        p1, p2 = (1,3) if side == "left" else (3,1)
        # 获得 t1,t2,并验证
        assert production == ["<term>","<term>","=","<term>"]
        j1, t1 = equal_t.get_child(equal_t.root, p1)
        assert t1.get("production") == ["<term>","(","<term>",")"]
        j1, t1 = equal_t.get_child(j1, 2)

        j2, t2 = equal_t.get_child(equal_t.root, p2)
        assert t2.get("production") == ["<term>","(","<term>",")"]
        # 判断 等式中的t1和待替换的t1相等
        t1_in_e = equal_t.copy_subtree(j1,basiccopy)
        t1_in_t = t.copy_subtree(t1_id, basiccopy)
        print(t1_in_e.totext(" "), t1_in_t.totext(" ")  )
        assert ABTree.equal(t1_in_t,t1_in_e)
        t.substitute(t1_id,equal_t.copy_subtree(j2,basiccopy))
        return t.totext(" ")
    def replace(self,t0i,t1:ABTree):
        """
        替换项
        t1 必须为 (t)
        - t0i: 被替换的项的id
        - t1: 待替换的项
        """
        self.abt.substitute(t0i,t1.copy(basiccopy))
        return self.abt.totext(" ")
    def regular_replace(self, t0i: int, t1: ABTree):
        """
        规范替换项，即替换前加括号，会改变 self.abt
        - t0i: 被替换的项的id
        - t1: 待替入的项
        """
        holder = {"value":"( " +t1.totext(" ")+ " )"}
        abt = ABTree()
        root = abt.add_nameless_vex(holder)
        abt.set_root(root)
        self.abt.substitute(t0i, abt)
        return self.abt.totext(" ")

    @staticmethod
    def fillin(template:ABTree,name_t:dict[str, ABTree]):
        """
        模板填充,模板不需要有语义
        - template: 模板（如 p->q）
        - name_t: {name:t}
        """
        ivars = [(i, node) for i, node in template.iter(order="post") if node.get("production") == ["<term>","<var>"]]
        for i, node in ivars:
            j, var = template.get_child(i, 1)
            name = var["value"]
            t = name_t[name]
            template.substitute(i,t.copy())
        return template.totext(" ")
    @staticmethod
    def regular_fillin(template:ABTree,name_t:dict[str, ABTree]):
        """
        规范的模板填充
        - template: 模板（如 p->q）
        - name_t: {name:t}
        """
        ivars = [(i, node) for i, node in template.iter(order="post") if node.get("production") == ["<term>","<var>"]]
        for i, node in ivars:
            j, var = template.get_child(i, 1)
            name = var["value"]
            t = name_t[name]
            LasyConverter(template).regular_replace(i,t)
        return template.totext(" ")
    @staticmethod
    def deduce(presumptions:list[ABTree],templates:list[ABTree],name_t:dict[str,ABTree],conclusion:ABTree):
        """
        演绎
        - presumptions: 前提
        - templates: 前提模板
        - name_t: {name:t} 实例
        - conclusion: 结论模板
        """
        filled_templates = [LasyConverter.fillin(tmp.copy(basiccopy),name_t) for tmp in templates ]
        presumption_strs = [abt.totext(" ") for abt in presumptions]
        if presumption_strs == filled_templates:
            print([t.totext(" ") for t in templates],"|-",conclusion.copy(basiccopy).totext(" "))
            return LasyConverter.fillin(conclusion,name_t)
        else:
            return None
    @staticmethod
    def regular_deduce(presumptions:list[ABTree],templates:list[ABTree],name_t:dict[str,ABTree],conclusion:ABTree):
        """
        规范化的演绎
        - presumptions: 前提
        - templates: 前提模板
        - name_t: {name:t} 实例
        - conclusion: 结论模板
        """
        filled_templates = [LasyConverter.regular_fillin(tmp.copy(basiccopy),name_t) for tmp in templates ]
        presumption_strs = [abt.totext(" ") for abt in presumptions]
        if presumption_strs == filled_templates:
            print([t.totext(" ") for t in templates],"|-",conclusion.copy(basiccopy).totext(""))
            return LasyConverter.regular_fillin(conclusion,name_t)
        else:
            return None
    def introduce(self,t:ABTree,name_var:dict[str, Var],type_: str):
        """
        量词引入
        - t : 待引入的项
        - name_var: {name:var}, 待引入的变量
        - type_: "∀"(all) or "∃"(exist) 
        """
        if type_ == "exist":
            type_ = "∃"
        elif type_ == "all":
            type_ = "∀"
        assert type_ in ["∀","∃"]
        # 换名
        term = t.get_vex(t.root)
        frees = term["free"]
        for name in name_var.keys():
            free = frees[name]
            new_name = name_var[name].name
            for i in free:
                t.get_vex(i)["value"] = new_name
        term_str = t.totext(" ")
        varTs = " ".join([f"{var.name} : {var.sort.to_words()}," for name, var in name_var.items()])
        return f"{type_} {varTs} {term_str}"
    def apply(self,f:Var,name_t:dict[str, ABTree]):
        """
        函数应用:  f (t1,t2,) = t (a->t1,b->t2)
        t 必须为 (t)
        - name_t: {name:t}
        """
        instance = self.instance(name_t)  #t (a->t1,b->t2)
        if len(name_t) == 1:#一个参数
            param = list(name_t.values())[0].totext(" ")
            return f"( {f.name} ( {param} ) ) = ( {instance} )"
        params = ""
        for x, t in name_t.items():
            params += f"{t.totext(' ')},"
        return f"( {f.name} ({params}) ) = ( {instance} )"
    def off_bracket(self, i:int = None):
        """
        去掉括号
        - i: term := ( term ) 的节点id，默认为 root
        # returns
        - text: 替换后的文本
        - abt: 预期的语法结构
        """
        i = i if i is not None else self.abt.root
        assert self.abt.get_vex(i).get("production") == ["<term>","(","<term>",")"]
        j, _ = self.abt.get_child(i, 2)
        subt = self.abt.copy_subtree(j, basiccopy)
        self.abt.substitute(i, subt)
        return self.abt.totext(" "), self.abt
    def on_bracket(self, i:int = None):
        """
        加上括号
        - i: term := ... 的节点id, 默认 root
        """
        i = i if i is not None else self.abt.root
        term = self.abt.copy_subtree(i, basiccopy)
        holder = {"value":"( " +term.totext(" ")+ " )"}
        abt = ABTree()
        root = abt.add_nameless_vex(holder)
        abt.set_root(root)
        self.abt.substitute(i, abt)
        return self.abt.totext(" ")
    @staticmethod
    def conclude(assumptions:list[ABTree],conclusion:ABTree):
        """
        假设归结
        - assumptions: 假设
        - conclusion: 结论
        """
        assumptions_strs = [abt.totext(" ") for abt in assumptions]
        assumptions_str = " ∧ ".join([f"( {assumption} )" for assumption in assumptions_strs])
        return f"( {assumptions_str} ) -> ( {conclusion.totext(' ')} )"
    def line2term(self):
        """
        将line转换为term
        """
        line = self.abt
        assert line.get_vex(line.root).get("production") == ["<line>","<term>"]
        i,_ = line.get_child(line.root, 1)
        term = line.copy_subtree(i, basiccopy)
        return term
        
        
    

            
def test_term_parser():
    """
    测试
    """
    grammar_path = r"../grammars/line.txt"
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
    grammar_path = r"../grammars/line.txt"
    text = "one prop_a := ¬(p->q)->{x : R|(f x)= y }"
    parser = LineParser(grammar_path)
    symbol_values = parser.lexical(text)
    tree = parser.build_tree(symbol_values)
    env = Context()
    analyzer = LineAnalyzer(tree, env)
    line_type = analyzer.get_line_type()
    print(line_type)
def test_fillin():
    """
    测试 fillin方法
    """
    grammar_path = r"../grammars/line.txt"
    parser = LineParser(grammar_path)
    template = parser.parse("p -> q")
    name_t = {"p":parser.parse("a->b"),"q":parser.parse("c->d")}
    print(LasyConverter.regular_fillin(template,name_t))
def test_deduce():
    """
    测试 deduce 方法
    """
    grammar_path = r"../grammars/line.txt"
    parser = LineParser(grammar_path)
    templates = [parser.parse("p -> q"),parser.parse("q -> r")]
    presumptions = [parser.parse("a->b -> (c->d)"),parser.parse("(c->d)->(e->f)")]
    name_t = {"p":parser.parse("a->b"),"q":parser.parse("c->d"),"r":parser.parse("e->f")}
    conclusion = parser.parse("p -> r")
    print(LasyConverter.regular_deduce(presumptions, templates,name_t,conclusion))
    
    
if __name__ == "__main__":
    #test_term_parser()
    #test_analyzer()
    #test_fillin()
    test_deduce()