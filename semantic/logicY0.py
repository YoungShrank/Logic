import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from context import Context, Var
from sort import Sort, SortTuple, Func
from utils import basiccopy, LineReader
from commander import Commander
from semantic import LineParser, Switcher, Context, TermAnalyzer, TermConverter, Sort, Var
from ruler import RuleSet
from abtree import ABTree

class CMDLogicY0:
    """
    基于命令行的推理机Y0（即用户接口为命令）
    """
    def __init__(self, grammer_path, rules_path, predefine_path) -> None:
        """
        - grammer_path : 语义分析的文法文件路径
        - rules_path : 推理规则文件路径
        - predefine_path : 预定义输入文件路径
        """
        # 命令解析
        self.cmder = Commander()
        # 推理机环境
        self.env = Context()
        # 语义分析
        self.line_parser = LineParser(grammar_path = grammer_path)
        # 推理规则
        self.set_rules(rules_path)
        # 预定义输入
        self.predefine(predefine_path)
        # 命令帮助
        self.help = self.init_help()

        
    def init_help(self):
        """
        命令帮助文档的初始化
        """
        doc = """
        decude ::  演绎 deduce  {conclusion_i} rule_i {-name instance_i}
        introduce :: 量词引入 introduce i quantifier {-<free> <bound>}
        instance :: 量词消去 instance i {-<name> <term_i>}
        select :: 构造 select i j k name
        read :: 查看环境 read {item} LN: 输入行| TH: 待证 | AX: 公理 | TS: 定理 | LC: 局部变量 | GL: 全局变量 | CC: 局部结论 | AS: 假设 | MD: 模式 | TM: 辅助项| RL: 规则
        write :: 写入 write | line
        exit :: exit
        use :: 使用假设或公理 use assume_or_axiom i
        eqrepl ::  等值替换 eqrepl equal_i conclusion_i first last side
        conclude :: 假设归结  conclude assumption_ids
        bra :: 去括号或者添加括号 bra off_on conclusion_i first last
        help :: help
        """
        help = {}
        for line in doc.split("\n"):
            line = line.strip()
            if line:
                name, description = line.split("::")
                help[name.strip()] = description
        return help
        
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
        
    
    def dispatch(self, cmd: str, pos_params: list[str], key_params: dict[str, str], expression: str = ""):
        """
        根据命令和参数调用相应函数
        - cmd : 命令名
        - pos_params : 位置参数
        - key_params : key-value 参数
        - expression : line_parser可以解析的句子（不包含具体环境信息）
        """
        if expression :
            expression: ABTree = self.line_parser.parse(expression)
            expression.view(see_vaule= True)
            
        match cmd:
            ## --------推理------ ##
            # 量词消去 instance i {-<name> <term_i>}
            case "instance": 
                conclusion_id, = pos_params
                name_i = key_params
                conclusion = self.env.conclusions[int(conclusion_id)]
                name_t = { name : self.env.terms[i] for name,i in name_i.items() }
                self.switch_line(TermConverter.regular_instance(conclusion, name_t))
            # 量词引入 introduce i quantifier {-<free> <bound>}
            case "introduce":
                conclusion_id, quantifier= pos_params
                free_bound = key_params
                free_sort = { free : self.env.get_var(free).sort for free in free_bound }
                free_bound_var = { bound : Var(bound, free_sort[free], "bound") for free, bound in free_bound.items() }
                conclusion = self.env.conclusions[int(conclusion_id)]
                line = TermConverter.introduce(conclusion, free_bound_var, quantifier)
                self.switch_line(line)
            # 演绎 deduce  {conclusion_i} rule_i {-name instance_i}
            case "deduce":
                presumptionis = pos_params[:-1]
                rule_i = pos_params[-1]
                presumptions = [ self.env.conclusions[i] for i in presumptionis]
                rule = self.env.get_rule(rule_i)
                templates, conclusion = rule
                name_instance = key_params
                line = TermConverter.regular_deduce(presumptions, templates, name_instance, conclusion)
                if line is None:
                    print("warning : invalid deduce")
                else:
                    self.switch_line(line)
            # 写（定义，待证定理）
            case "write":
                TermAnalyzer(expression, self.env).solve()
                self.switch(expression)
            # 使用假设或公理 use assume_or_axiom i
            case "use" :
                assume_or_axiom, i = pos_params
                if assume_or_axiom == "assume":
                    self.switch_line(self.env.assumptions[int(i)].totext(" "))
                elif assume_or_axiom == "axiom" :
                    self.switch_line(self.env.axioms[i].totext(" "))
                elif assume_or_axiom == "theorem":
                    self.switch_line(self.env.theorems[i].totext(" "))
            # 等值替换 eqrepl equal_i conclusion_i first last old_side
            case "eqrepl":
                #
                equal_i, conclusion_i, first, last, old_side = pos_params
                equal_t = self.env.conclusions[int(equal_i)]
                conclusion = self.env.conclusions[int(conclusion_i)]
                oldi = TermConverter.select_by_pos(conclusion, [int(first), int(last)])
                line = TermConverter.equal_replace(equal_t, conclusion, oldi, old_side)
                self.switch_line(line)
            # 去括号 bra  off_on conclusion_i first last,如果不可去，则提示
            case "bra":
                off_on, conclusion_i, first, last = pos_params
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
            #假设归结  conclude assumption_ids
            case "conclude":
                assumption_ids = pos_params
                assumptions = self.env.conclude_start(assumption_ids)
                line = TermConverter.conclude(assumptions, self.env.conclusions[-1])
                self.switch_line(line)
            case "qed":
                self.env.qed()
            ##--------查询------##
            # 查看 环境 read {item}
            case "read":
                self.env.print(*pos_params)
            # 选择子项 select conclusion_id, first, last name
            case "select":
                conclusion_id, first, last, name = pos_params # 索引 左叶的父必然 在左
                conclusion_id, first, last =int(conclusion_id), int(first), int(last)
                conclusion: ABTree = self.env.conclusions[conclusion_id]
                i = TermConverter.select_by_pos(conclusion, [first, last])
                self.env.add_term(name, conclusion.copy_subtree(i, basiccopy)) 
            case "help":
                if len(pos_params) == 0:
                    for name, description in self.help.items():
                        print("  {} : {}".format(name, description))
                else :
                    cmd_name = pos_params[0]
                    if cmd_name in self.help:
                        print(self.help[cmd_name])
                    else:
                        print("Unknown command: {}".format(cmd_name))
                        print("Available commands:")
                        for name, description in self.help.items():
                            print("  {} : {}".format(name, description))
            case _ :
                raise Exception("Unknown command: {}".format(cmd))
    def execute(self, cmdline: str):
        """
        读入与执行命令
        - cmdline : 命令行，格式为： cmd {pos_params} {-key1 <value1>} | expression
        """
        cmd, pos_params, key_params, remainder = self.cmder.parse(cmdline)
        self.dispatch(cmd, pos_params, key_params, remainder)
                
class LogicY0:
    """
    推理机Y0
    """
    def __init__(self, env:Context) -> None:
        self.env = env
    def deduce(presumptions:list[int], rule:str):
        """
        应用推理规则推理，在推理
        - presumptions: 前提的索引
        - rule: 推理规则
        # returns
        产生结论
        """
        pass
    def instance():
        pass
    def introduce():
        pass
    def replace():
        pass
    def parseline(self):
        """
        解析行
        """
        pass
    
    def addline(self, line:str):
        """
        输入行
        """
        pass

if __name__ == "__main__":

    cmd_logic_y0 = CMDLogicY0("../grammars/line.txt", "../semantic/rules.txt", "../test/sentences/predefine.txt")
    cmd_logic_y0.dispatch("read", [], {}, "")