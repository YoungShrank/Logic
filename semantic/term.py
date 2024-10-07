import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from words import Word,shift,union
from lrparser import LRParser,LR1Table
from grammar import Grammar
from abtree import ABTree

#预定义类
REFER = {"any","one","bound"}
SORT = {"Set","Prop","Math"}

class Var:
    """
    变量类
    """
    def __init__(self,name:str,value:str,sort:str,refer:str) -> None:
        """
        变量类
        - name: 变量名
        - value: 变量值
        - sort: 变量数学类型
        - refer: 变量指代类型
        """
        assert refer in REFER
        self.name = name
        self.value = value
        self.sort = sort
        self.refer = refer
    def todict(self) -> dict:
        return {"name":self.name,"value":self.value,"sort":self.sort,"refer":self.refer}

class Context:
    """
    环境类
    """
    def __init__(self) -> None:
        """
        环境类
        """
        self.vars:dict[str,Var] = {
            "z":Var("z","0","Set","any"),
            "Set":Var("Set","Set","Sort","one"),
            "Num":Var("Num","Num","Sort","one")
        }#变量
    def get_var(self,name:str) -> Var:
        """
        获取变量
        - name: 变量名
        # returns
        - var: 变量
        """        
        return self.vars[name]



class TermParser:
    def __init__(self,grammar_path:str) -> None:
        """
        项的语义分析类
        - grammar_path: 语法文件路径
        """
        self.grammar = Grammar(S="<term>")
        self.grammar.from_file(grammar_path)
        self.grammar.extend(end="#")
        self.grammar.init(solve=True)
        priority  = ["¬","∧","∨","<->","->","∀","∃"]
        associativity = {"¬":"r","∧":"l","∨":"l","<->":"r","->":"r","∀":"r","∃":"r"}
        table = LR1Table(self.grammar,ambiguity=True,priority=priority,associativity=associativity)
        self.lrparser = LRParser(table)
        self.context = Context()
    def patterns(self):
        """
        词法的正则式
        # returns
        - pattern: 正则表达式
        - vask: 词法分析的保留字（一字一类）
        - key2type: key和symbol的映射
        """
        pattern = {
        "op":union(["¬","->","<->","∧","∨","∀","∃"]),
        "del": "[{}]".format(shift("(){}<>[],;:'.*&^%$#@!~")),
        "var":r"[a-zA-Z_][a-zA-Z0-9]*",
        "num":r"[0-9]+",
        "space":r"\s+",
        "other":r"."
        }
        vask = {"op","del"}
        key2type = {
            "var":"<id>",
            "num":"<num>",
            "space":"<space>",
            "other":"other"
        }
        return pattern,vask,key2type
    # 词法分析
    def lexical(self,text:str) -> None:
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
    
    def solve_var(self,abt:ABTree):
        """
        计算变元的名字
        - abt: 语法分析树
        # returns
        <type>.name = <id>.name
        <id>.name = value
        """
        for i,data in abt.iter(order="post"):#自底向上，可以计算值
            production = data.get("production")
            value = data.get("value")
            childs = [e.i2 for e in abt.get_adj(i)]
            if data["symbol"] == "<id>":
                data["name"] = value
                data["isvar"] =True
            if production == ['<type>', '<id>']:
                data["name"] = abt.get_vex(childs[0])["name"]
                data["isvar"] =True

    def solve_bound(self,abt:ABTree):
        """
        计算约束变元的约束节点
        - abt: 语法分析树
        """
        for i,data in abt.iter(order="pre"):
            production = abt.get_vex(i).get("production")
            value = data.get("value")
            childs = [e.i2 for e in abt.get_adj(i)]
            parent = abt.parents[i]
            if parent :
                parent_bounded_ids = abt.get_vex(parent).get("bounded_ids",{})
            else :
                parent_bounded_ids = {}
            new_bounded = {}
            new_bounded_ids = {}
            if production == ['<term>', '∃', '<id>', ':', '<type>', ',', '<term>']:
                name = abt.get_vex(childs[1])["name"]
                sort = abt.get_vex(childs[3])["name"]
                new_bounded.setdefault(name,Var(name,name,sort,"bound").todict())
                new_bounded_ids[name] = i
            elif production == ['<term>', '∀', '<id>', ':', '<type>', ',', '<term>']:
                name = abt.get_vex(childs[1])["name"]
                sort = abt.get_vex(childs[3])["name"]
                new_bounded.setdefault(name,Var(name,name,sort,"bound").todict())
                new_bounded_ids[name] = i
            data["bounded_ids"]=parent_bounded_ids | new_bounded_ids
            data["new_bounded"] = new_bounded

    def solve_domain(self,abt:ABTree):
        """
        计算变元域(约束或者全局)
        - abt: 语法分析树
        """
        for i,data in abt.iter(order="post"):
            name = data.get("name") #不为空的是变元
            bounded_ids = data.get("bounded_ids",{})
            if name in bounded_ids:#约束变元
                depend = abt.get_vex(bounded_ids[name])
                data["var"] = depend["new_bounded"][name] #var
            elif name is not None:#全局变元
                data["var"] = self.context.get_var(name).todict()
            else:
                del data["bounded_ids"]#这种间接依赖没有用了
            if len(data["new_bounded"]  ) == 0:
                del data["new_bounded"]     
            print(data)
        


    #计算变元域(约束或者全局)和类(数学类型和指代类型)
    def solve_domain_sort(self,abt:ABTree) -> None:
        """
        计算变元域(约束或者全局)和类(数学类型和指代类型)
        暂时还只是域，和指代类型
        - abt: 语法分析树
        """
        abt.init_parents()
        self.solve_var(abt)
        self.solve_bound(abt)
        self.solve_domain(abt)
        print(abt.tosymbols())
    #计算

    def parse(self,text:str) -> None:
        symbol_values = self.lexical(text)
        abt = self.build_tree(symbol_values)
        self.solve_domain_sort(abt)
        abt.view("var",see_vaule=True)
    
class Matcher:
    """
    模式匹配，将语法树匹配到一个句型
    """
    def __init__(self) -> None:
        pass
    def match(self,sentence:ABTree,abt:ABTree) -> None:
        """
        匹配句型和串
        - sentence: 句型的语法树 (<term> <-> <term> ∧ <term>)
        - abt: 串的语法树 (<id> <-> (<id> -> <id>) ∧ <id>)
        # returns
        - ismatch : bool 是否匹配成功
        - mapper :{int:int} 句型叶子和串子树的对应关系
        """
        mapper = {}
        def match_node(i,j):
            myself = sentence.get_vex(i)["symbol"] == abt.get_vex(j)["symbol"]
            if not myself: return False
            sentence_childs = [e.i2 for e in sentence.get_adj(i)]
            if len(sentence_childs) == 0:#没有后继，是句型
                mapper[i] = j
                return True
            else :
                abt_childs = [e.i2 for e in abt.get_adj(j)]
                if len(sentence_childs) != len(abt_childs): return False
                for ei,ej in zip(sentence.get_adj(i),abt.get_adj(j)):#后继
                    if not match_node(ei.i2,ej.i2):
                        return False
                return True #子树匹配
        ismatch = match_node(sentence.root,abt.root)
        return ismatch,mapper

class Converter:
    """
    执行转换规则
    """
    def __init__(self,abt:ABTree) -> None:
        self.abt = abt
    def rename(self,x:str,y:str):
        """
        换名规则，改变约束变元名称,∀x:T,P(x)  ∀y:T,P(x)[x->y]
        - x: 旧变元名称
        - y: 新变元名称
        """
        for i,data in self.abt.iter(order="post"):#自底向上
            new_bounded = data.get("new_bounded",{})
            bounded_ids = data.get("bounded_ids",{})
            if x in new_bounded:#被依赖的
                new_bounded[y] = new_bounded[x]
                del new_bounded[x]
                new_bounded[y]["name"]= y
                print(new_bounded)
            if bounded_ids:#依赖的
                if x == data["name"]:
                    j = bounded_ids[x]
                    bounded_ids[y] = j
                    del bounded_ids[x]
                    data["var"] = self.abt.get_vex(j)["new_bounded"][x]
                    data["name"] = y
                    if data.get("value"):
                        data["value"] = y
    def instance(self,x:str,y:str):
        """
        消去规则，将约束变元替换为全局变元，消去量词 如 y, ∀x:T,P(x)   P(y)[x->y]
        已知项的模式为 ∀x:T,P(x)
        后期改成支持子项替换规则的
        """
        i ,data = self.abt.get_child(self.abt.root,6) # P(x)
        self.abt = ABTree(self.abt.get_subtree(i))
        #改为全局变量
        for i,data in self.abt.iter(order="post"):
            if data.get("name") == x:
                data["name"] = y
                data["value"] = y
                data.pop("bounded_ids")
                print(data)

    def substitute(self,x:str,t:ABTree):
        """
        代入规则，将自由变元用项替换，如 x = t(z), P(x)  P(x)[x->(t(z))]
        - x: 自由变元名称
        - t: 项的语法树
        """
        variants = [i for i,data in self.abt.iter(order="post") if data.get("name") == x ]
        for i in variants:
            self.abt.substitute(i,t)
    
    def select_term(self,n:int) -> None:
        """
        根据终结符选择term,最深的祖先<term>
        - abt: 语法分析树
        - n : 第n个非终结符
        """
        leafs = [i for i,data in self.abt.iter_leafs()]
        i = leafs[n]
        for j,data in self.abt.iter_ancestor(i):#自底向上
            symbol = data.get("symbol")
            if symbol == "<term>":
                return j
    def compound(self,sentence:ABTree,terms:list[ABTree]):
        """
        将项进行复合生成新项（将项代入句型），不直接生成语法树，而是先生成串再解析
        如 p,q |- p ∧ q
        """
        j = 0
        leafs = [(i,data) for i,data in sentence.iter_leafs()]
        print((sentence.tosymbols()))
        for i,data in leafs:
            if data.get("symbol") == "<term>":#需要代入
                term = terms[j]
                sentence.substitute(i,term)
                j+=1
            else :
                data["value"] = data.get("symbol")
        #对于只考虑语法的sentence,没有value语义，当然,
        # 1.可以用symbol赋值给value.2.使用有语义的snetence（如p->p而不是<term>→<term>）
        # 要考虑定位替换节点，这涉及到语法细节，<term>-><id>，即<id>的父节点
        #计算语义
        print((sentence.totext()))

        
def test_term_parser():
    """
    测试 语法分析, 语义计算（变量数学类和指代类）
    """
    term_parser = TermParser("grammars/term.txt")
    abt1 = term_parser.build_tree(term_parser.lexical("∀x:Set,x<->x ∧ ∃y:Num,(x->y)∧(x->z)")) #有单词语义
    abt2 = term_parser.lrparser.parse("∀ <id> : <type> , <id> <-> <term>".split(),meaning=False) #无单词语义
    abt1.view(see_vaule=True,path="abt1.html")
    abt2.view(see_vaule=True,path="abt2.html")

    term_parser.solve_var(abt1)
    abt1.view("name",see_vaule=True,path="abt_solve_var.html")
    term_parser.solve_bound(abt1)
    abt1.view("new_bounded",see_vaule=True,path="abt_solve_bound.html")
    term_parser.solve_domain(abt1)
    abt1.view("var",see_vaule=True,path="abt_solve_domain.html")
def test_matcher():
    """
    测试  项的匹配, 语法树转串 ,获得子树
    """
    term_parser = TermParser("grammars/term.txt")
    abt1 = term_parser.build_tree(term_parser.lexical("∀x:Set,x<->x ∧ ∃y:Num,(x->y)∧(x->z)"))
    abt2 = term_parser.lrparser.parse("∀ <id> : <type> , <id> <-> <term>".split(),meaning=False)
    matcher = Matcher()
    ismatch,mapper = matcher.match(abt2,abt1)
    print(ismatch,mapper)
    if ismatch:
        for i,j in mapper.items():
            print(ABTree(abt2.get_subtree(i)).tosymbols(" ") ,ABTree(abt1.get_subtree(j)).totext(" "))
            
        
def test_converter():
    """
    测试  换名规则，消去量词，代入规则，复合规则，项选择
    """
    term_parser = TermParser("../grammars/term.txt")
    abt1 = term_parser.build_tree(term_parser.lexical("∀x:Set,x<->x ∧ ∃y:Num,(x->y)∧(x->z)"))
    term_parser.solve_domain_sort(abt1)
    converter = Converter(abt1)
    print(converter.abt.totext())
    #换名
    converter.rename("x","q")
    converter.rename("q","p")
    print(converter.abt.totext(" "))
    #消去
    converter.instance("p","t")
    print(converter.abt.totext(" "))
    #代入
    term = term_parser.build_tree(term_parser.lexical("(u->u)"))
    converter.substitute("t",term)
    print(converter.abt.totext(" "))
    #选择
    i = converter.select_term(13)
    print(list(converter.abt.iter_leafs())[13-1])
    print(ABTree(converter.abt.get_subtree(i)).totext(" "))
    #复合
    sentence = term_parser.lrparser.parse("<term> ∧ <term>".split())
    sentence.init_parents()
    term2 = term_parser.build_tree(term_parser.lexical("(m->m)"))
    converter.compound(sentence,[term,term2])








if __name__ == "__main__":
    #test_term_parser()
    #test_matcher()
    test_converter()


