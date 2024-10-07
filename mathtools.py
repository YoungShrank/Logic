# 数学算法

def SetEquation(equation:list[list],solution:dict[str,set],operator:str="|"):
    """
    求解集合方程组
    1. A ⊃ B ∪ C
    2. B ⊃ C ∪ D
    ...
    - - -
    1. A ⊃ B ∩ C
    2. B ⊃ C ∩ D
    - - -
    包含关系构成一个图状结构，相互包含自然是相等的，属于一个等价类，最后可视为DAG
    准确来说是求最小集合
    使用迭代法，最多迭代n次
    - equation: 集合方程组,左部可多次出现
    - solution: 初始化集合和返回集合，非原地操作
    - operator: 运算符，默认为并集，可选并集|、交集&
    """
    assert operator in ["|","&"]
    op = {"|":set.union,"&":set.intersection}[operator]
    while True:
        flag = False
        for equ in equation:
            left = equ[0]
            right = equ[1:]
            new_items = op(*[solution[r] for r in right])
            before = len(solution[left])
            solution[left] = solution[left]|new_items
            after = len(solution[left])
            if after > before:
                flag = True
        if not flag: break

if __name__ == "__main__":
    equation = [
        ["A","B","C"],
        ["A","B","C"],
        ["B","C","D"],
        ["C","E","F"],
        ["D","E","F"],
        ["F","D"]
    ]
    solution = {
        "A":{"A"},
        "B":{"B"},
        "C":{"C"},
        "D":{"D"},
        "E":{"E"},
        "F":{"F"}
    }
    SetEquation(equation,solution,"&")
    print(solution)
