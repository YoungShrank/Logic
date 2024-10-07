
from grammar import Grammar
from tostring import toString
from pandas import DataFrame
import pandas
from mathtools import SetEquation
from Structure import DiGraph
from abtree import ABTree
ENDSYMBOL = "#"
class LR1Item :
    """
    LR1项目
    """
    def __init__(self, production:list, position:int=1,follow:set=set()):
        """
        - production: 产生式[left,*right]
        - position: 解析位置 A->.aBb, position = 1
        - follow: 后跟符号
        """
        self.production = production
        self.position = position
        self.follow:set[str] = follow
    def __eq__(self, value: object) -> bool:
        """
        重载 ==，lR1项目集相等还要看follow
        """
        if isinstance(value, LR1Item):
            return self.production == value.production and self.position == value.position and self.follow == value.follow
        else:
            return False
    def __str__(self) -> str:
        return toString.tuple2str(toString.list2str(self.production) , self.position,toString.set2str(self.follow))
    def __hash__(self) -> int:
        """
        修改会导致hash值变化
        """
        return hash(self.__str__())
    def relax_eq(self, value: object) -> bool:
        """
        不需要follow相等
        """
        if isinstance(value, LR1Item):
            return self.production == value.production and self.position == value.position
        else:
            return False
    def isreduce(self) -> bool:
        """
        规约项
        """
        return self.position == len(self.production)
    def isend(self,S:str) -> bool:
        """
        终项
        - S 开始符号
        """
        return self.isreduce() and self.production[0] == S
    
        
class LR1ItemSet :
    """
    LR1项目集
    """
    def __init__(self, items: set[LR1Item]):
        """
        - items: 项目集
        """
        self.items = items
        self.reductions:set[LR1Item] = set()
    def __len__(self) -> int:
        return len(self.items)
    def __eq__(self, value: object) -> bool:
        """
        重载 ==，lR1项目集相等还要看follow
        """
        if isinstance(value, LR1ItemSet):
            return self.items == value.items
        else:
            return False
    def __str__(self) -> str:
        return toString.set2str(self.items,seperator="\n")
    def __hash__(self) -> int:
        """
        修改会导致hash值变化
        """
        return hash(self.__str__())
    def isend(self, S:str) -> bool:
        """
        判断是否是终态
        """
        for item in self.items:
            if item.isend(S): return True
        return False
        
    def closure(self, grammar: Grammar):
        """
        计算闭包
        """
        item_queue = [item for item in self.items]
        equation = []
        for item in item_queue:
            if item.isreduce():#规约项目
                self.reductions.add(item)
                continue
            if item.production[item.position] in grammar.NV:
                for production in grammar.rule_L[item.production[item.position]]:
                    first_after = grammar.get_first(item.production[item.position+1:])
                    addeq = False
                    if '' in first_after:
                        new_item = LR1Item(production,follow=(first_after-{''}))
                        addeq = True#需要添加方程
                    else :
                        new_item = LR1Item(production,follow=first_after)
                    #相同的项
                    eq_items = [eq_item for eq_item in item_queue if eq_item.relax_eq(new_item)]
                    if len(eq_items) ==1:
                        eq_items[0].follow.update(new_item.follow)
                        new_item = eq_items[0]
                    elif len(eq_items) ==0:
                        item_queue.append(new_item)
                    #添加方程
                    if addeq:
                        equation.append([new_item,item])
        solution = {item:item.follow.copy() for item in item_queue}
        SetEquation(equation,solution)
        for item in item_queue:
            item.follow = solution[item]
        self.items = set(item_queue)
    def next(self, symbol: str):
        """
        计算下一状态
        """
        item_queue = []
        for item in self.items:
            if item.position == len(item.production):#规约项目
                continue
            if item.production[item.position] == symbol:
                new_item = LR1Item(item.production, item.position + 1,item.follow)#同类项目follow一致
                item_queue.append(new_item)#不会出现相同的项目
        return LR1ItemSet(set(item_queue))
    def get_LR1ItemSets(self, grammar: Grammar):
        """
        计算所有项目集
        """
        start  = ID = 0  #初态
        self.closure(grammar)
        LR1ItemSets:dict[int,LR1ItemSet] = {start:self}
        terminals =set()#终态
        gotomap = {}  # goto表，移入后的状态
        queue = [start]
        while queue:
            i = queue.pop(0)
            item_set = LR1ItemSets[i]
            for symbol in grammar.V:
                next_item_set = item_set.next(symbol)
                next_item_set.closure(grammar)
                if len(next_item_set) == 0:
                    continue#空集跳过
                i2s = [j for j,item in LR1ItemSets.items() if item == next_item_set] #新项目集或者旧项目集
                if len(i2s) == 0:#新项目集
                    ID += 1
                    LR1ItemSets[ID] = next_item_set
                    queue.append(ID)

                    i2 = ID
                    if next_item_set.isend(grammar.S):#终态
                        terminals.add(i2)
                else :#旧项目集
                    i2 = i2s[0]
                gotomap[i,symbol] = i2
        return LR1ItemSets, gotomap ,start, terminals

class LR1Table :
    """
    LR1分析表
    """
    def __init__(self, grammar: Grammar,ambiguity=False,priority=["¬","∧","∨","<->","->","∀","∃","λ",""],associativity={}):
        """
        - grammar: 语法
        - ambiguity: 是否允许ambiguity
        - priority: 优先级，靠前的优先级大
        - associativity: 结合性,l:左结合,r:右结合,默认左结合
        """
        self.grammar = grammar
        self.priority:list[str] = priority
        self.associativity:dict[str,str] = associativity
        S = grammar.S
        S_LR1Item = LR1Item(grammar.rule_L[S][0])
        S_LR1ItemSet = LR1ItemSet({S_LR1Item})
        LR1ItemSets,gotomap,start,ends =  S_LR1ItemSet.get_LR1ItemSets(grammar)#移入状态转移
        action = {}
        for i in LR1ItemSets.keys():
            item_set = LR1ItemSets[i]
            reductions  = list( item_set.reductions ) #规约项目
            for v in grammar.V:
                aiv = action[i,v] = []
                if gotomap.get((i,v)):
                    aiv.append( ("s",gotomap.get((i,v))))
                for reduction in reductions:
                    production:list[str] = reduction.production
                    if v in reduction.follow:#follow
                        aiv.append(("r",production))
                        if not ambiguity and len(aiv) > 1:
                            raise Exception("action[{}][{}] {}  冲突".format(i,v,action[i,v]))
                if ambiguity == False:
                    aiv = aiv[0] if len(aiv) == 1 else None
        self.solve_ambiguity(action)
        self.LR1ItemSets =LR1ItemSets
        self.action = action
        self.gotomap = gotomap
        self.start = start
        self.ends = ends
    def solve_ambiguity(self,action:dict):
        """
        解决ambiguity(粗略的方法)
        - action: action表
        """
        for i,v in action.keys():
            actions = action[i,v]
            if len(actions) == 0:
                action[i,v] = None
            elif len(actions) ==1:
                action[i,v] = actions[0]
            elif len(actions) ==2:
                s , j = actions[0] #第一个必是移入
                r , p = actions[1]
                op = list(set(p).intersection( self.priority))
                if len(op) == 0: #没有算符
                    op = ""
                elif len(op) == 1: #算符只有一个
                    op = op[0]
                else : #算符多个
                    raise Exception("case of multiple operators is beyond my consideration")
                if v not in self.priority:  # 没有算符
                    right_priority = self.priority.index("")
                else :
                    right_priority = self.priority.index(v)
                if self.priority.index(op)<right_priority:#左边优先级大，相等默认左结合
                    action[i,v] = (r,p)
                elif self.priority.index(op)>right_priority:#右边优先级大
                    action[i,v] = (s,j)
                else :#优先级相等看结合性
                    if self.associativity.get(op,"l") == "r":
                        action[i,v] = (s,j)  #右结合则移入
                    else :
                        action[i,v] = (r,p)  #左结合则规约
            else : 
                raise Exception("ambiguity beyond my solution")
    def tograph(self):
        """
        action转成图
        - action {(i,v):i2}}
        """
        vexs = [(i,v) for i,v in self.LR1ItemSets.items()]
        edges = [(i,j,e) for (i,e),j in self.gotomap.items() ]
        graph = DiGraph(vexs=vexs,edges=edges)
        return graph


    def todf(self):
        """
        action转成dataframe
        - action {(i,v):i2}}
        """
        indexs = sorted(self.LR1ItemSets.keys())
        columns = sorted(self.grammar.V)
        data = {v:[self.action[i,v] for i in indexs] for v in columns}
        print("action",self.action)
        print("goto",self.gotomap)
        print("index" ,indexs)
        print("df data" ,data)
        return DataFrame(data,index=indexs,columns=columns)



class LRParser:
    def __init__(self,table:LR1Table) -> None:
        """
        LR1分析器
        - table:lr分析表
        """
        self.table = table
        self.state_stack = [self.table.start]#状态栈
        self.symbol_stack = [] #符号栈
        self.record_columns = ["状态栈","符号栈","动作类","动作参数","面临字符"]
        self.record = DataFrame(columns=self.record_columns) #分析记录
    def add_record(self,action_t,action_p,x,state=None,symbol=None):
        """
        添加分析记录
        - action_t:动作类型
        - action_p:动作参数
        - x:输入
        - state:状态栈
        - symbol:符号栈
        """
        if state is None:
            state = self.state_stack
        if symbol is None:
            symbol =self.symbol_stack
        state = state.copy()
        symbol = symbol.copy()
        row = DataFrame(columns=self.record_columns,data=[[state,symbol,action_t,action_p,x]])
        self.record = pandas.concat([self.record,row])

    def parse(self,input:list[str],meaning = False) :
        """
        分析符号串
        - input:符号串
        - meaning:是否有语义（即input是否为有value的单词）
        # returns
        - abstact tree if accepted,error otherwise
        - parse record
        """
        abt = ABTree()
        self.record = DataFrame(columns=self.record_columns)
        if meaning == False:
            input =[(x,None) for x in input]
        input.append((self.table.grammar.E,None))#终止符号
        self.state_stack=[self.table.start]
        self.symbol_stack = []
        i =0 
        while True:
            if self.state_stack[-1] in self.table.ends:#终态
                abt.accept()
                self.add_record("接受","","")
                return abt
            if i >= len(input): #输入结束
                raise Exception("expected stack: {},actual stack: {}".format([self.table.grammar.S_,self.table.grammar.E],self.symbol_stack))
            x,v = input[i] #输入
            xist = True
            while True:#不断规约
                action = self.table.action.get((self.state_stack[-1],x))
                if action is None:
                    raise Exception("error {} facing {}".format(self.state_stack[-1],x))
                act , index = action
                if act == "s":#移进
                    self.add_record("移入",index,x)
                    self.state_stack.append(index)
                    self.symbol_stack.append(x)
                    if xist:
                        abt.movein(x,v)
                        i+=1
                    break
                elif act == "r":#规约
                    rule = index
                    self.add_record("规约",rule,x)
                    abt.reduce(rule)
                    for k in range(len(rule[1:])):
                        self.state_stack.pop()
                        self.symbol_stack.pop()
                    x = rule[0]
                    xist = False
                else:

                    raise Exception("act error :{} {}".format(act,index))


def test_grammar(path:str,S:str):
    grammar = Grammar(S=S)
    grammar.from_file(path)
    grammar.extend(end=ENDSYMBOL)
    grammar.init(solve=True)
    if False:
        print(grammar.S)
        print(grammar.rules)
        print("folow\n",grammar.FOLLOW)
        print("*"*20)
        print(grammar.FIRST)
    return grammar
def test_table(grammar:Grammar):
    priority  = ["=","∈","¬","∧","∨","<->","->","∀","∃","λ",""]
    associativity = {"¬":"r","∧":"l","∨":"l","<->":"r","->":"r","∀":"r","∃":"r","λ":"r","":"r"}
    print("building ... ")
    table = LR1Table(grammar,ambiguity=True,priority=priority,associativity=associativity)
    g = table.tograph()
    from Structure import VDiGraph
    VDiGraph(g).view()
    return table

def test_parse(table:LR1Table):

    symbols = "<var> <var> ∀ <var> : <var> , ( ¬ <var> , ) -> <term> ∧ <term> ∧ <var> ∨ <var> ∧ <var> -> <var> #"

    parser = LRParser(table)
    print("parsing ... ")
    abt = parser.parse(symbols.split())
    from Structure import VTree
    def viewf(i,data):
        return str(data["symbol"])
    VTree(abt).view(viewf=viewf)
    parser.record.to_excel("parse.xlsx")


if __name__ == "__main__":
   grammar = test_grammar("grammars/line.txt","<term>")
   print(grammar.FIRST)
   table = test_table(grammar)
   print(grammar.FIRST)
   test_parse(table)


"""

事成之后有空写下文档
"""