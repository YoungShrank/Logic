import re
class Sort:
    """
    类型，为树状结构
    """
    PATTERN = re.compile(r"(?P<name>[a-zA-Z_][_a-zA-Z0-9]*)(?P<subsorts>(\[.*\])?)")
    def __init__(self,name:str, subsorts:list[object] = None):
        """
        - compound: (name, *subsorts)
        """
        self.name = name
        self.subsorts: list[Sort] = subsorts
        if subsorts:
            for i in range(len(subsorts)):
                if isinstance(subsorts[i], str):
                    subsorts[i] = Sort(subsorts[i])
        self.compound = (name, *subsorts) if subsorts else name
    def __str__(self) -> str:
        """
        t[sub1,sub2,...]
        """
        def _tostr(sort: Sort|str) -> str:
            if isinstance(sort, str):
                return sort
            if sort.subsorts :
                return "{}[{}]".format(sort.name,",".join(map(_tostr, sort.subsorts)))
            else:
                return sort.name
                
        return _tostr(self)
    def __eq__(self, o: object) -> bool:
        return self.compound == o.compound
    @staticmethod
    def from_str(s:str) :
        """
        从字符串构造
        - s: 字符串
        # returns
        - sort: 类型
        """
        stack = []
        s_ = ""
        for i, x in enumerate(s):
            if x == "[":
                if s_:
                    stack.append(s_)
                    s_ = ""
                stack.append(x)
            elif x == "]":
                if s_:
                    stack.append(s_)
                    s_ = ""
                sorts = []
                while True:
                    y = stack.pop()
                    if isinstance(y, str) and  y == "[":
                        name = stack.pop()
                        stack.append(Sort(name,sorts))
                        break
                    else:
                        sorts.insert(0,y if isinstance(y, Sort) else Sort(y))
            elif x == ",":
                if s_:
                    stack.append(s_)
                    s_ = ""
            else:
                s_ += x
        if s_:
            stack.append(Sort(s_))
            s_ = ""
        stack: list[Sort]
        return stack.pop()
            

    def to_words(self) -> str:
        """
        将类型分解为句子
        # returns
        - words: 代表类的句子
        """
        def _to_words(sort: Sort|str) -> str:
            if isinstance(sort, str):
                return sort
            if sort.subsorts :
                return "{}[{}]".format(sort.name,"".join([_to_words(sub)+"," for sub in sort.subsorts])) # A[B,C,]
            else:
                
                return sort.name
        return _to_words(self)
    @ staticmethod
    def is_super(sort1, sort2) -> bool:
        """
        判断sort1是否是sort2的超类,或者说sort2是sort1的实例
        # returns
        - bool: sort1是否是sort2的子类
        """
        sort1 : Sort = sort1
        sort2 : Sort = sort2
        if sort1.name == sort2.name:
            if sort1.subsorts:
                if sort2.subsorts:
                    for i in range(len(sort1.subsorts)):
                        if not Sort.is_super(sort1.subsorts[i], sort2.subsorts[i]):
                            return False
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

class Func(Sort):
    """
    函数类
    """
    def __init__(self,in_sort:Sort, out_sort: Sort):
        """
        - in_sort: 输入类型
        - out_sort: 输出类型
        """
        super().__init__("Func",[in_sort, out_sort])
        self.in_sort = in_sort
        self.out_sort = out_sort
class SortTuple(Sort):
    """
    元组类
    """
    def __init__(self,subsorts:list[Sort]):
        """
        - subsorts: 元组子类型
        """
        super().__init__("Tuple",subsorts)
    
if __name__ == "__main__":
    sort1 = Sort.from_str("Set")
    sort2 = Sort.from_str("Set[Math,Set[Math],Set[Set[Math]]]")
    print(Sort.is_super(sort1, sort2))