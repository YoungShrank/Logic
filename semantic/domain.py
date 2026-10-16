from typing import Hashable
class Node:
    def __init__(self, key:Hashable, start: int, end: int = None) -> None:
        self.key = key
        self.start = start
        self.end = end
    
    def __repr__(self) -> str:
        return f"Node({self.key}, {self.start}, {self.end})"

class ListDomain:
    """
    表示域的概念（如作用域，假设域），域间的关系只能是包含或者无交集。
    用list实现，每个元素表示一个域，按创建顺序排列。
    """
    def __init__(self):
        """
        初始化id,以供后使用
        """
        self.ID = 0
        self.stack:list[Hashable] = []
        self.map:dict[Hashable, Node] = {}
        self.nodes:list[Node] = []
        #self.step_in(0, "global") # 初始化一个域，表示全局域
    
    def step_in(self, seq:int, key:Hashable = None):
        """
        进入一个新的域，seq表示当前域的开始位置
        - seq : 当前域的开始位置
        - key : 当前域的key, 如果没有指定，则使用ID作为key
        """
        if key is None:
            key = self.ID
            self.ID += 1
        self.stack.append(key)
        n = Node(key, seq)
        self.nodes.append(n)
        self.map[key] = n
    
    def step_out(self, seq:int):
        """
        退出当前域，返回上一个域
        - seq: 当前域的结束位置
        """
        if len(self.stack) == 0:
            raise Exception("域栈为空，无法退出")
        key = self.stack.pop()
        node = self.map[key]
        node.end = seq
    
    def current_domain(self):
        """
        获得当前域
        ### return
        当前域
        """
        return self.stack
    
    def get_domain(self, seq:int) -> list[Hashable]:
        """
        获取当前序列所在的域
        - seq : 当前序列
        ### return
        - list[Hashable] : 当前序列所在的域的key列表 (域path)
        """
        return [node.key for node in self.nodes if node.start <= seq and (node.end is None or node.end >= seq)]
    
    def get_domain_range(self, key:Hashable) -> tuple[int, int]:
        node = self.map[key]
        return node.start, node.end
    
    def get_domain_tree(self, end: int = 100) -> list[Node]:
        """
        ### return
        tree:{
            sub: list[tree] | None,
            ran: (int, int)
            key: Hashable | None 
        }
        """
        stack = [{"sub":[], "ran":[None, None]}]
        value_range = [0]
        events = []
        for node in self.nodes:
            events.append((node.start, node.key, "start"))
            if node.end is not None:
                events.append((node.end, node.key, "end"))
        events.sort(key=lambda x: x[0])
        def append_value_range(seq: int):
            value_range.append(seq)
            stack[-1]["sub"].append({"sub":None, "ran":value_range[-2:]})
            
        for event in events:
            if event[2] == "start":
                append_value_range(event[0])
                new_node = {"sub":[], "ran":[event[0], None], "key":event[1]}
                stack[-1]["sub"].append(new_node)
                stack.append(new_node)
            elif event[2] == "end":
                append_value_range(event[0])
                tree = stack.pop()
                tree["ran"][1] = event[0]
        while len(stack) > 1:
            append_value_range(end)
            tree = stack.pop()
            tree["ran"][1] = end
        return tree


        
        

def test():
    domain = ListDomain()
    domain.step_in(0, "a")
    domain.step_in(3, "b")
    domain.step_in(5, "c")
    domain.step_out(7)
    domain.step_out(8)
    domain.step_in(10, "d")
    print(domain.nodes)
    print("get domain of 1:", domain.get_domain(1))
    print("get_domain_range of a" ,domain.get_domain_range("a"))
    tree = domain.get_domain_tree()
    ## 缩进打印树结构
    def print_tree(tree, indent=0):
        if tree.get("sub") is None:
            print(" " * indent, tree.get("ran"))
        else:
            print(" " * indent, tree.get("key"))
            for sub in tree.get("sub"):
                print_tree(sub, indent + 2)
    print("domain tree:")
    print_tree(tree)