
from commander import Commander
from semantic import LogicApi

class CMDLogicY0():
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
        # 推理机逻辑接口
        self.logic_api = LogicApi(grammer_path, rules_path, predefine_path)
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
    def dispatch(self, cmd: str, pos_params: list[str], key_params: dict[str, str], expression: str = ""):
        """
        根据命令和参数调用相应函数
        - cmd : 命令名
        - pos_params : 位置参数
        - key_params : key-value 参数
        - expression : line_parser可以解析的句子（不包含具体环境信息）
        """            
        match cmd:
            ## --------推理------ ##
            # 量词消去 instance i {-<name> <term_i>}
            case "instance": 
                conclusion_id, = pos_params
                conclusion_id = int(conclusion_id)
                name_i = key_params
                self.logic_api.instance(conclusion_id, name_i)
            # 量词引入 introduce i quantifier {-<free> <bound>}
            case "introduce":
                conclusion_id, quantifier= pos_params
                free_bound = key_params
                self.logic_api.introduce(conclusion_id, quantifier, free_bound)
            # 演绎 deduce  {conclusion_i} rule_i {-name instance_i}
            case "deduce":
                presumptions = pos_params[:-1]
                rule_i = pos_params[-1]
                name_instance = {n: int(i) for n, i in key_params.items()}
                self.logic_api.deduce(presumptions, rule_i, name_instance)
            # 写（定义，待证定理）
            case "write":
                self.logic_api.write(expression)
            # 使用假设或公理 use assume_or_axiom i
            case "use" :
                assume_or_axiom, i = pos_params
                self.logic_api.use(assume_or_axiom, i)
            # 等值替换 eqrepl equal_i conclusion_i first last old_side
            case "eqrepl":
                #
                equal_i, conclusion_i, first, last, old_side = pos_params
                self.logic_api.eqrepl(equal_i, conclusion_i, first, last, old_side)
            # 去括号 bra  off_on conclusion_i first last,如果不可去，则提示
            case "bra":
                off_on, conclusion_i, first, last = pos_params
                self.logic_api.bra(off_on, conclusion_i, first, last)
            #假设归结  conclude assumption_ids
            case "conclude":
                assumption_ids = pos_params
                assumption_ids = [int(i) for i in assumption_ids]
                self.logic_api.conclude(assumption_ids)
            case "qed":
                self.logic_api.qed()
            ##--------查询------##
            # 查看 环境 read {item}
            case "read":
                self.logic_api.env.print(*pos_params)
            # 选择子项 select conclusion_id, first, last name
            case "select":
                conclusion_id, first, last, name = pos_params # 索引 左叶的父必然 在左
                self.logic_api.select(conclusion_id, first, last, name)
            case "help":
                cmd_name = None if len(pos_params) == 0 else pos_params[0]
                self.show_help(cmd_name)
            case _ :
                raise Exception("Unknown command: {}".format(cmd))

    def show_help(self, item:str = None):
        """
        打印帮助文档
        - item : 命令名，如果为None，则打印所有命令
        """
        if item is None:
            for name, description in self.help.items():
                print("  {} : {}".format(name, description))
        else :
            cmd_name = item
            if cmd_name in self.help:
                print(self.help[cmd_name])
            else:
                print("Unknown command: {}".format(cmd_name))
                print("Available commands:")
                for name, description in self.help.items():
                    print("  {} : {}".format(name, description))
    def execute(self, cmdline: str):
        """
        读入与执行命令
        - cmdline : 命令行，格式为： cmd {pos_params} {-key1 <value1>} | expression
        """
        cmd, pos_params, key_params, remainder = self.cmder.parse(cmdline)
        self.dispatch(cmd, pos_params, key_params, remainder)