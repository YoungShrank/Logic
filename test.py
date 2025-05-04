# 导入磁盘上其他的python文件
# 在模块被导入时，__init__.py文件会被自动执行, 这里非其他导入情况，手动执行
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR) # 父目录路径
RESOURCE_DIR = os.path.join(CURRENT_DIR, "resource")
sys.path.append(RESOURCE_DIR) # 资源路径
sys.path.extend(
    [
        "D:/WorkPlace/github"
    ]
)  # 依赖的路径
print("system paths: ", sys.path)  # 打印当前的sys.path列表


from test.line_reader import test as test_line_reader
from test.test_analyser import test as test_analyser
from test.test_commander import test as test_commander
from test.test_char_pos_to_token_pos import test as test_char_pos_to_token_pos
from test.test_logicY0 import test as test_logicY0
from test.test_bracket import test as test_bracket
from test.test_axiom import test as test_axiom
from test.test_eq_replace import test as test_eq_replace
from test.test_deduce import test as test_deduce
from test.test_context_vert import test as test_context_vert
from semantic.convert import test_deduce as test_convert_deduce
from semantic.convert import test_fillin as test_convert_fillin
from semantic.line import test_analyzer as test_line_analyzer
from semantic.line import test_term_parser as test_line_term_parser
from interface.logic_flask import run as run_logic_flask
#test_line_analyzer()
from grammar import test as test_grammar
run_logic_flask()