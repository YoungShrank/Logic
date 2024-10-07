import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from commander import Commander
def test():
    cmder = Commander()
    cmd, pos_params, _, expression = cmder.parse("add 1 2 | mul 3 4")
    print(cmd, pos_params, expression)

if __name__ == "__main__":
    test()