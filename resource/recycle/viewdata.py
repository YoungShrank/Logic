# 界面上输入和输出的数据

# 输入
class BasicInput:
    """
    基本输入：选择的项和应用的规则，选项
    """
    def __init__(self,
                 command,
                 conclusion_ids,
                 assumption_ids,
                 axiom_id,
                 rule_id,
                 option,
                 bool_option,
                 text
                 ):
        self.command = command
        self.conclusion_ids = conclusion_ids
        self.assumption_ids = assumption_ids
        self.axiom_id = axiom_id
        self.rule_id = rule_id
        self.option = option
        self.bool_option = bool_option
        self.text = text

class SubTermInput(BasicInput):
    """
    涉及子项输入：选择的子项和应用的规则，子项范围
    """
    def __init__(self,
                 command,
                 conclusion_ids,
                 assumption_ids,
                 axiom_id,
                 rule_id,
                 option,
                 bool_option,
                 text,
                 first,
                 last,
                 ):
        """
        可使用组合，而不是继承
        """
        super().__init__(command, 
                         conclusion_ids, 
                         assumption_ids, 
                         axiom_id, 
                         rule_id, option, 
                         bool_option, text)
        self.first = first
        self.last = last
        

# 输出

class BasicOutput:
    """
    """
    def __init__(self,
                 render_function,
                ):
        self.render_function = render_function # 前台渲染方法
        self.forend_props = {} # 前台状态量

class TermOutput(BasicOutput):
    """
    输出一个项
    """
    def __init__(self,
                 render_function,
                 termName,
                 termIndex,
                 termContent,
                 ):
        super().__init__(render_function)
        self.termName = termName
        self.termIndex = termIndex
        self.termContent = termContent

class VarOutput(BasicOutput):
    """
    输出一个变量
    """
    def __init__(self,
                 render_function,
                 var,
                 ):
        super().__init__(render_function)
        self.var = var

class ListOutput(BasicOutput):
    """
    输出一个列表
    """
    def __init__(self,
                 render_function,
                 items,
                 ):
        super().__init__(render_function)
        self.items = items