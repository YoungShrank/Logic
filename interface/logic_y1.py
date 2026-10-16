

from semantic import LogicApi

# 图形UI 的推理机 前后端分离
class GUILogicY1:
    """
    图形UI 的推理机 前后端分离
    """
    def __init__(self):
        """
        - grammer_path : 语义分析的文法文件路径
        - rules_path : 推理规则文件路径
        - predefine_path : 预定义输入文件路径
        """
        from resource_service import ResourceService
        grammer_path = ResourceService.get("grammars/line.txt")
        rules_path = ResourceService.get("first-order/rules.txt")
        predefine_path = ResourceService.get("test/sentences/predefine2.txt")
        self.logic_api = LogicApi(grammer_path, rules_path, predefine_path)
        

gui_logic_y1 = GUILogicY1()