# 语义环境
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abtree import ABTree
from sort import Sort
from typing import Any
from utils import Printer


#预定义类
REFER = ["any","one","bound"]
SORT = ["Set","Prop","Math","Tuple","Func","M"]

# 预定义变量
VARS = {
    "T" : "Prop",
    "⊥" : "Prop"
}

# 预定义函数
FUNC = {
    "Union": "λ A : Set[Set,], . { x : Math | ∃ a : A , x ∈ a } ", 
    "Insect": "λ A : Set[Set,], .  { x: Math | ∀ a : A , x ∈ a } ", 
    "Subset": "λ A : Set, B : Set, .   ∀ a :A, a ∈ B ",
    "Power": "λ A : Set, .  { x : Set |  Subset (x,A,) }"
}

# 定理
THEOREM = {}

# 公理
AXIOM = {}

# 模式
MODE = ["Proof", "Assert", "Global"]



class Var:
    """
    变量语义
    """
    def __init__(self, name:str, sort:Sort, type_:str, value:ABTree = None) -> None:
        """
        - name : 变量名
        - sort : 变量数学类型
        - type_ : 变量指代类型
        - value : 值
        """
        assert type_ in REFER
        self.name = name
        self.sort = sort
        self.type_ = type_
        self.value = value
    def __str__(self) -> str:
        return self.name + "|" + str(self.sort) + "|" + self.type_

class Context:
    """
    推理机环境
    """
    def __init__(self) -> None:
        # 输入
        self.lines: list[ABTree] = []
        # 定理
        self.theorems: dict[str, ABTree]= {}
        # 待证
        self.theorem: ABTree = None
        # 公理
        self.axioms: dict[str, ABTree] = {}
        # 预定义类
        self.refer = REFER
        self.sort = SORT
        # 自定义类(集合)
        self.sets = []
        # 全局变量 {name:type}
        self.globals:dict[str,Var] = {}
        for name,sort in VARS.items():
            self.globals[name] = Var(name, Sort.from_str(sort), "one")
        # 局部变量
        self.locals:dict[str,Var] = {}
        # 局部结论
        self.conclusions:list[ABTree] = []
        # 假设
        self.assumptions:list[ABTree] = []
        # 推理规则
        self.rules: dict[str, tuple[list[ABTree],ABTree]] = {}
        # 当前模式
        self.mode = MODE[2]

        #---辅助环境----#
        # 构造的项
        self.terms:dict[str,ABTree] = {}
    def print(self, *items):
        """
        打印当前环境
        - items : 显示项, 默认为所有
        LN: 输入行| TH: 待证 | AX: 公理 | TS: 定理 | LC: 局部变量 | GL: 全局变量 | CC: 局部结论 | AS: 假设 | MD: 模式 | TM: 辅助项| RL: 规则
        """
        Printer.print_head("CONTEXT")
        matcher = {
            "LN":lambda :Printer.print_attr("Lines",self.lines, mapper= lambda x:x.totext(" ")),
            "TH":lambda :Printer.print_attr("Theorem",None if self.theorem is None else self.theorem.totext(" ")),
            "AX":lambda :Printer.print_attr("Axioms",self.axioms, mapper=lambda x:x.totext(" ")),
            "TS":lambda :Printer.print_attr("Theorems",self.theorems, mapper=lambda x:x.totext(" ")),
            "LC":lambda :Printer.print_attr("Locals",self.locals),
            "GL":lambda :Printer.print_attr("Globals", self.globals),
            "CC":lambda :Printer.print_attr("Conclusions",self.conclusions, mapper=lambda x:x.totext(" ")),
            "AS":lambda :Printer.print_attr("Assumptions",self.assumptions, mapper=lambda x:x.totext(" ")),
            "MD":lambda :Printer.print_attr("Mode",self.mode),
            "TM":lambda :Printer.print_attr("Terms",self.terms, mapper=lambda x:x.totext(" ")),
            "RL":lambda :Printer.print_attr("Rules",self.rules, mapper=lambda x:self.rule2str(x))
        }
        if len(items) == 0 :
            items = ["LN","TH","AX","TS","LC","GL","CC","AS","MD","TM", "RL"]
        for item in items:
            matcher[item]()
        Printer.print_head()
    
    def rule2str(self,rule: tuple[list[ABTree],ABTree]):
        """
        规则([presumption],conclusion)转换为字符串
        """
        presumptions, conclusion = rule
        return ",".join([x.totext(" ") for x in presumptions]) + "|-" + conclusion.totext(" ")
    def set_rules(self, rules:dict[str, tuple[list[ABTree],ABTree]]):
        """
        设置规则
        """
        self.rules = rules
    def get_rule(self,x:str):
        """
        按名访问规则
        - x : str
        """
        return self.rules[x]
        
    def get_var(self,x:str):
        """
        按名访问变量,优先访问局部变量
        - x : str
        """
        if x in self.locals:
            return self.locals[x]
        elif x in self.globals:
            return self.globals[x]
        else :
            return None
    def add_term(self, name:str, term:ABTree):
        """
        添加辅助项
        - name : 辅助项名
        - term : 辅助项
        """ 
        self.terms[name] = term
        print("Add Term {}: {}", name, term.totext(" "))
    def get_term(self, name:str):
        """
        按名访问辅助项
        - name : str
        """ 
        return self.terms[name]
    def add_var(self, name:str, sort:Sort, type_:str, value:ABTree = None):
        """
        添加变量
        - name : 变量名
        - sort : 变量数学类型
        - type_ : 变量指代类型 
        """
        match self.mode, type_:
            case "Assert", "one":
                self.globals[name] = Var(name, sort, type_, value)
            case "Global", "one":
                self.globals[name] = Var(name, sort, type_, value)
            case "Proof", "one":
                self.locals[name] = Var(name, sort, type_, value)
            case "Proof", "any":
                self.locals[name] = Var(name, sort, type_, value)
            case _:
                raise Exception("Add Var Error: {} {} {}".format(name,sort,type_))
    def index_conclusion(self,x:ABTree):
        """
        定位局部结论
        - x : str
        """ 
        str_x = x.totext(" ")
        for i,c in enumerate(self.conclusions):
            str_c = c.totext(" ")
            if str_c == str_x:
                return i
        return -1
    def append_conclusion(self,x:ABTree):
        """
        添加局部结论
        - x : 结论
        """ 
        print("Append Conclusion:",x.totext(" "))
        self.conclusions.append(x)
    def assume(self,t:ABTree):
        """
        添加假设
        - t : 假设
        """ 
        if self.mode == "Proof":# 证明模式
            print("Assume:",t.totext(" "))
            self.assumptions.append(t)
        else :
            raise("Assume Error:",t.totext(" "))
    def get_theorem(self,x:str):
        """
        按名访问定理
        - x : str
        """ 
        if x in self.theorems:
            return self.theorems[x]
        else :
            return None
    def find_theorem(self,x:ABTree):
        """
        按值查找定理
        - x : 定理值
        """ 
        str_x = x.totext(" ")
        for k,v in self.theorems.items():
            if v.totext(" ") == str_x:
                return k,v
    def add_theorem(self,name:str,value:ABTree):
        """
        添加定理
        - name : 定理名
        - value : 定理值
        """
        self.theorems[name] = value
        print("Add Theorem:",name,value.totext(" "))
    def get_axiom(self,x:str):
        """
        按名访问公理
        - x : str
        """ 
        if x in self.axioms:
            return self.axioms[x]
        else :
            return None
    def find_axiom(self,x:ABTree):
        """
        按值查找公理
        - x : 公理值
        """ 
        str_x = x.totext(" ")
        for k,v in self.axioms.items():
            if v.totext(" ") == str_x:
                return k,v
    def add_axiom(self,name:str,value:ABTree):
        """
        添加定理
        - name : 公理名
        - value : 公理值
        """
        self.axioms[name] = value
        print("Add Axiom:",name,value.totext(" "))
    def qed(self):
        """
        结束证明
        """
        if self.theorem.totext(" ") == self.conclusions[-1].totext(" "):#结论匹配
            self.mode = MODE[2]
            self.theorems[f"theorem_{len(self.lines)}"] = self.theorem
            self.theorem = None   # 证毕
            self.conclusions.clear() #清空结论
            self.locals.clear()  #清空局部变量
            self.assumptions.clear()#清空假设
        else :
            raise Exception("QED Error: {}".format(self.theorem,self.conclusions[-1]))
    def proof(self,theorem:ABTree):
        """
        开始证明
        - theorem : 定理值
        """
        if self.mode == MODE[2]:#全局模式
            self.theorem = theorem
            self.mode = MODE[0]
        else :
            raise("Proof Error:",theorem)
    def assert_(self):
        """
        开始断言
        """
        if self.mode == MODE[2]:#全局模式
            self.mode = MODE[1]
        else :
            raise("Assert Error:")
    def conclude_start(self, assume_ids: list[int]):
        """
        假设归结
        - assume_ids : 假设序号
        """
        if self.mode == MODE[0]:#证明模式
            used = [self.assumptions[i] for i in range(len(assume_ids)) if i  in assume_ids]
            self.assumptions = [self.assumptions[i] for i in range(len(assume_ids)) if i not in assume_ids]
            print("Conclude:",[ass.totext(" ") for ass in used])
            return used
        else :
            raise("Conclude Error:",assume_ids)
    def end_assert(self):
        """
        结束断言
        """
        if self.mode == MODE[1]:#断言模式
            self.mode = MODE[2]
        else :
            raise("End Assert Error:")
    
    

if __name__ == "__main__":
    pass
        
        


    
    
