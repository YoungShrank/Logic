import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from context import Context, Var
from sort import Sort, SortTuple, Func
from utils import basiccopy, LineReader, ListAlgorithms
from semantic import LineParser, Switcher, Context, TermAnalyzer, TermConverter, Sort, Var
from ruler import RuleSet
from abtree import ABTree
class LogicApi:
    """
    推理机逻辑的接口
    """
    def __init__(self, grammer_path, rules_path, predefine_path) -> None:
        """
        - grammer_path : 语义分析的文法文件路径
        - rules_path : 推理规则文件路径
        - predefine_path : 预定义输入文件路径
        """
        # 推理机环境
        self.env = Context()
        # 语义分析
        self.line_parser = LineParser(grammar_path = grammer_path)
        # 推理规则
        self.set_rules(rules_path)
        # 预定义输入
        self.predefine(predefine_path)
    def set_rules(self, rules_path: str):
        """
        设置推理规则
        - rules_path 规则文件地址
        内容可能如下
        ```
        {p}  |- p∨q
        {q}  |- p∨q
        {p,q} |- p∧q
        ```
        """
        self.rule_set = RuleSet([ rule for rule in LineReader(rules_path)])
        print("【rules】")
        print(self.rule_set.rules)
        rules = {}
        for i, (presumption_strs, conclusion_str) in enumerate(self.rule_set.rules):
            presumptions = [ self.line_parser.parse(x) for x in presumption_strs]
            conclusion = self.line_parser.parse(conclusion_str)
            rules[i] = (presumptions, conclusion)
        self.env.set_rules(rules)
            
        
    def predefine(self, predefine_path):
        """
        预定义  (函数，数集，公理等), 省去了对基本对象和公理的自定， 
        可能如下：
        ```
        one Union := λ A : Set[Set,], . { x : Math | ∃ a : A , x ∈ a } 
        one N : Set,  
        one ADD : Func[Tuple[N,N,],N,],
        one _0 : N,  
        ∀ x :N,  (ADD (x,_0,)) = x  
        ```
        - predefine_path : 预定义文件路径
        """
        for line in LineReader(predefine_path):
            abt = self.semantic_parse(line)
            self.switch(abt)
        
    def semantic_parse(self, text: str, to_term = False, copy = True):
        """
        对text进行语法和静态语义分析
        - text 待分析的文本
        - to_term : 是否返回term，默认为False (当为True时，和text2term等价)
        - copy: 是否生成副本
        """
        abt = self.line_parser.parse(text) 
        TermAnalyzer(abt, self.env).solve()
        if to_term:
            return TermConverter.line2term(abt, copy_abt=copy)
        return abt
    
    def switch(self, abt: ABTree):
        """
        环境转换
        - abt : 输入行的语法分析树，已经分析静态语义
        """
        Switcher(abt, self.env).switch()
    def switch_line(self, line: str):
        """
        环境转换
        - line : 输入行（也有可能是生成的）
        """
        abt = self.semantic_parse(line)
        Switcher(abt, self.env).switch()
        
        
    def text2term(self, text:str):
        """
        text解析为term，并计算语义
        """
        line = self.line_parser.parse(text)
        term = TermConverter.line2term(line)
        TermAnalyzer(term, self.env).solve()
        return term
    
    def instance(self, conclusion_id: int, name_i: dict[str, str]):
        """
        量词消去
        - conclusion_id : 推论id
        - name_i : {变量名 : 代入项id}, 
        """
        conclusion = self.env.conclusions[conclusion_id]
        name_t = { name : self.env.terms[i] for name,i in name_i.items() }
        self.switch_line(TermConverter.regular_instance(conclusion, name_t))

    def introduce(self, conclusion_id: int, quantifier: str, free_bound: dict[str, str]):
        """
        量词引入
        - conclusion_id : 推论id
        - quantifier : 量词
        - free_bound : {自由变量名 : 引入的约束变量名}
        """
        free_sort = { free : self.env.get_var(free).sort for free in free_bound }
        free_bound_var = { bound : Var(bound, free_sort[free], "bound") for free, bound in free_bound.items() }
        conclusion = self.env.conclusions[int(conclusion_id)]
        line = TermConverter.introduce(conclusion, free_bound_var, quantifier)
        self.switch_line(line)

    def deduce(self, presumptions:list[int], rule_i:int, name_instance_i: dict[str, int]):
        """
        演绎
        - presumptions : 前提id列表
        - rule_i : 规则id
        - name_instance_i : {占位名 : 实例id}
        """
        presumptions = [ self.env.conclusions[i] for i in presumptions]
        rule = self.env.get_rule(rule_i)
        templates, conclusion = rule
        name_instance = { name : self.env.terms[i] for name,i in name_instance_i.items() }
        line = TermConverter.regular_deduce(presumptions, templates, name_instance, conclusion)
        if line is None:
            print("warning : invalid deduce")
        else:
            self.switch_line(line)
    
    def write(self, expression: str):
        """
        写（定义，待证定理）
        - expression : 输入行
        """
        line = self.semantic_parse(expression, to_term=False)
        self.switch(line)
    
    def use(self, assume_or_axiom: str, index: str):
        """
        使用假设或公理 use assume_or_axiom i
        - assume_or_axiom : assume or axiom or theorem
        - index : index of assume_or_axiom
        """
        match assume_or_axiom:
            case "assume":
                index: int = int(index)
                self.switch_line(self.env.assumptions[index].totext(" "))
            case "axiom":
                self.switch_line(self.env.axioms[index].totext(" "))
            case "theorem":
                self.switch_line(self.env.theorems[index].totext(" "))
            case _:
                print("warning : invalid use")
    
    def eqrepl(self, equal_i: str, conclusion_i: str, first: str, last: str, old_side: str):
        """
        等价代换
        - equal_i : 等式id
        - conclusion_i : 推论id
        - first : 子项起始
        - last : 子项结束
        - old_side : 被替换项所在等式侧
        """
        equal_t = self.env.conclusions[int(equal_i)]
        conclusion = self.env.conclusions[int(conclusion_i)]
        oldi = TermConverter.select_by_pos(conclusion, [int(first), int(last)])
        line = TermConverter.equal_replace(equal_t, conclusion, oldi, old_side)
        self.switch_line(line)
    
    def bra(self, off_on: str, conclusion_i: str, first: str, last: str):
        """
        去括号或者加括号
        - off_on : off or on
        - conclusion_i : 推论id
        - first : 子项起始
        - last : 子项结束
        """
        conclusion = self.env.conclusions[int(conclusion_i)]
        i = TermConverter.select_by_pos(conclusion, [int(first), int(last)])
        print(conclusion.get_vex(i))
        conclusion.view(see_vaule=True)
        if off_on == "on":
            line = TermConverter.on_bracket(conclusion, i)
            self.switch_line(line)
        else:
            line, expect_abt = TermConverter.off_bracket(conclusion, i)
            expect_abt.view(see_vaule=True,path="expect.html")
            res_abt = TermConverter.line2term(self.line_parser.parse(line))
            if ABTree.equal(res_abt, expect_abt):
                self.switch_line(line)
            else :
                print("warning : invalid off bracket")
    def conclude(self, assumption_ids: list[int]):
        """
        假设归结
        - assumption_ids : 假设id列表
        """
        assumptions = self.env.conclude_start(assumption_ids)
        line = TermConverter.conclude(assumptions, self.env.conclusions[-1])
        self.switch_line(line)
    
    def qed(self):
        """
        证毕
        """
        self.env.qed()

    def select(self, conclusion_id: str, first: str, last: str, name:str):
        """
        选择子项
        - conclusion_id : 推论id
        - first : 子项起始
        - last : 子项结束
        - name : 变量名
        """
        conclusion_id, first, last =int(conclusion_id), int(first), int(last)
        conclusion: ABTree = self.env.conclusions[conclusion_id]
        i = TermConverter.select_by_pos(conclusion, [first, last])
        self.env.add_term(name, conclusion.copy_subtree(i, basiccopy))

    def char_pos_to_token_pos(self, conclusion_id: str, first: str, last: str, text:str) -> tuple[int, int]:
        """
        字符索引转换为token索引
        - conclusion_id : 推论id
        - first : 子项起始(字符位置)
        - last : 子项结束(字符位置, exclusive)
        - text : 推论文本
        """
        conclusion_id, first, last =int(conclusion_id), int(first), int(last) - 1
        while text[first] == " ": 
            first += 1
        while text[last] == " ": 
            last -= 1
        print("first, last : ", first, last, "sub : ", text[first:last+1])
        conclusion: ABTree = self.env.conclusions[conclusion_id]
        tokens = conclusion.totext(" ").split(" ")
        token_lens = [len(token) for token in tokens]
        sub_text, origin2sub, sub2origin = ListAlgorithms.map_sublist(list(text), lambda x: not x.isspace())
        
        tfirst, inner_tfirst = ListAlgorithms.item_index_to_seg_index(token_lens, origin2sub[first])
        tlast, inner_tlast = ListAlgorithms.item_index_to_seg_index(token_lens, origin2sub[last])
        i = TermConverter.select_by_pos(conclusion, [tfirst, tlast])
        tfirst, tlast = conclusion.get_leaf_range(i)
        tlast -= 1
        cfirst= ListAlgorithms.seg_index_to_item_index(token_lens, tfirst, 0)
        clast= ListAlgorithms.seg_index_to_item_index(token_lens, tlast, token_lens[tlast] - 1)
        return tfirst, tlast, sub2origin[cfirst], sub2origin[clast]


