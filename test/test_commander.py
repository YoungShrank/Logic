import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from interface.commander import Commander
def test():
    cmder = Commander()
    cmd, pos_params, _, expression = cmder.parse("add 1 2 | mul 3 4")
    print(cmd, pos_params, expression)

if __name__ == "__main__":
    test()