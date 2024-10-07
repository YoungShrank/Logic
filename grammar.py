from mathtools import SetEquation
import random
NOTHING = ''
class Grammar:
    """
    上下文无关文法，包含起始符、终结符、非终结符、产生式
    """

    def __init__(self,rules:list[list]=[],S:str =None) -> None:
        """
        - rules:产生式 [left,*right]
        - V:字母表
        - NV:非终结符
        - TV:终结符
        - S:起始符
        """
        #基本属性
        if rules is None:
            rules=[] 
        self.rules=rules
        self.V=set()
        self.NV=set()
        self.TV=set()
        self.S=S

        #索引
        self.rule_L = {} # 左部索引 rule_L[A]={A->..}
        self.rule_R = {} # 右部索引 rule_L[v]={B->..v..}

        #分析出的属性
        self.NONE = set() # {A|A=*=>''},推出符号为空的非终结符
        self.HEAD = {} # HEAD[A]={v|A=+=>v...},优先分析法使用,正推出串的头
        self.LAST = {} # LAST[A]={v|A=+=>...v},优先分析法使用,正推出串的尾
        self.FIRST = {} # FIRST[A]={v|A=+=>v...}∪{''|A=*=>''}, FIRST[A]为A的推导串的第一个符号或者空串
        self.FOLLOW = {} # FOLLOW[A]={v|S=*=>..Av..}, FOLLOW[A]为A可能的后续符号
        self.LC:Grammar = None # regular nt的文法，RN = {αB|∃γ∈T*,S=r*=>αBγ} , LC = {αβ|∃B∈RN,B→β} 
    def show(self):
        """
        打印文法
        """
        #打印推导式
        print("产生式：")
        for rule in self.rules:
            print("{}->{}".format(rule[0],rule[1:]))
        #打印开始符
        print("开始符：{}".format(self.S))
        # 打印终结符
        print("终结符：{}".format(self.TV))
        # 打印非终结符
        print("非终结符：{}".format(self.NV))

    def extend(self,start="<S>",end:str=None):
        """
        增广文法
        - start:起始符
        - end:句子的结束符号,也可以为None，表示没有
        """
        self.rules.insert(0,[start,self.S]+([end]if end else []))
        self.S_ = self.S
        self.S=start
        self.E = end
        
    def parseV(self):
        """
        从产生式中解析出符号
        # returns
        V,NV,TV
        """
        V = set() # 符号
        NV = set() # 非终结符
        TV = set() # 终结符
        for rule in self.rules:
            nv = rule[0]
            vs = rule[1:]
            NV.add(nv)
            V.update(vs)
        TV = V - NV  # 除了终结符，其余为非终结符
        return V,NV,TV
    def from_file(self,path:str):
        """
        从文件读取规则，产生式左边为非终结符，其余为非终结符
        """
        with open(path,mode="r",encoding="utf-8") as file:
            table=[line.split() for line in file]
            return self.from_list(table)
    def from_list(self,table:list[list]):
        """
        从列表读取规则，产生式左边为非终结符，其余为非终结符
        """
        for words in table:
            if(len(words)==0):continue
            self.rules.append(words)
    def solve_NONE(self):
        """
        A->''  A∈NONE
        A->BC  B,C∈NONE-->A∈NONE
        求NONE
        """
        equation = []
        solution = {nv:set() for nv in self.NV}
        for rule in self.rules:
            nv = rule[0]
            vs = rule[1:]
            if(len(vs)==0):
                solution[nv] = {''}
                continue
            if self.TV.intersection(vs)==set(): # A->BC
                equation.append([nv,*vs])
        print("NONONONO",equation)
        SetEquation(equation,solution,"&")
        NONE = {nv for nv in solution if '' in solution[nv]}
        return NONE

    def solve_FIRST(self):
        """
        求FIRST
        A->a...  a ∈ FIRST(A)
        A->''    '' ∈ FIRST(A)
        A->BC..Da..  
        """
        equation = []
        solution = {nv:{'',nv} if nv in self.NONE else {nv}  for nv in self.NV}
        for rule in self.rules:
            nv = rule[0]
            vs = rule[1:]
            for v in vs:
                if v in self.NV: # 
                    equation.append([nv,v])
                    if v not in self.NONE: #非连续空
                        break
                else:
                    solution[nv].add(v)
                    break
        SetEquation(equation,solution)
        FIRST = solution
        FIRST.update({tv:{tv} for tv in self.TV})# 终结符
        return FIRST
    def get_first(self,tokens:list):
        """
        获得串推到的首符号，{a|α=*=>a..}

        """
        if len(tokens)==0:return {''} # []
        elif len(tokens)==1:# [a] or [A]
            return self.FIRST[tokens[0]].copy()#防止修改
        else : # [v,v',..]
            first1 = self.FIRST[tokens[0]]
            if '' in first1: 
                return (first1-{''})|(self.get_first(tokens[1:]))
            else : return first1
    def solve_FOLLOW(self):
        """
        求FOLLOW，不包括空
        """
        equation = []
        solution = {nv:set() for nv in self.NV}
        for rule in self.rules:
            nv = rule[0]
            vs = rule[1:]
            for i in range(len(vs)):
                v = vs[i]
                if v in self.NV:
                    first_after = self.get_first(vs[i+1:])
                    solution[v].update(first_after-{''})
                    if '' in first_after :
                        equation.append([v,nv]) # B-> ..A..  FOLLOW(B)
        SetEquation(equation,solution)
        FOLLOW = solution
        return FOLLOW
    def solve_LC(self):
        """
        RN = {αB|∃γ∈T*,S=r*=>αBγ}
        S∈RN0
        δA∈RN_n,∃γ∈T*,A→αBγ==> δαB∈RN_(n+1)

        <S>
        <S>→..<A>
        <A>→..<B>
        """
        lc = []
        S = "<{}>".format(self.S)
        mapper = {}
        mapper[self.S]=S
        queue = [self.S]
        visited = {self.S}
        while queue:
            nv = queue.pop(0)
            NV = mapper[nv]
            rules = self.rule_L.get(nv,[])
            print("\n",nv,rules)
            for rule in rules:
                #获得最右端非终结符
                vs = rule[1:]
                lc.append([NV,*vs]) # 终结
                v = None
                for i in range(len(vs)-1,-1,-1):#最右
                    if vs[i] in self.NV:
                        v = vs[i]
                        vs = vs[:i]#α
                        break
                if v is not None :
                    V = "<{}>".format(v)
                    mapper[v] = V
                    lc.append([NV,*vs,V]) #非终结
                    if v  not in visited:
                        queue.append(v)
                        visited.add(v)
        LC = Grammar()
        LC.from_list(lc)
        LC.S = S
        LC.init(solve=False)
        return LC
    def random_deduce(self,n:int):
        """
        随机推导
        - n :推导长度 n≥0
        # returns
        - sentence :推导串
        - length :推导长度
        """
        sentence = [self.S]
        for i in range(n):
            nv_index = [i for i,v in enumerate(sentence) if v in self.NV]
            if len(nv_index)==0:
                return sentence,i
            random_index = random.choice(nv_index)
            nv = sentence[random_index]
            productions = self.rule_L[nv]
            production = random.choice(productions)
            sentence[random_index:random_index+1]=production[1:]#推导
        return sentence,n

    
    def init(self,solve=True):
        """
        初始化
        """
        self.V,self.NV,self.TV=self.parseV()
        if self.S is None:
            self.S=self.rules[0][0]
        self.rule_L,self.rule_R =  self.init_index()

        # 求解
        if solve:
            self.NONE = self.solve_NONE()
            self.FIRST = self.solve_FIRST()
            self.FOLLOW = self.solve_FOLLOW()
            self.LC = self.solve_LC()
            print("NONE",self.NONE)
            print("first",self.FIRST)
            print("follow",self.FOLLOW)
            print("LC",self.LC.random_deduce(10))
    
    def init_index(self):
        """
        初始化索引
        """
        rule_L = {nv:[] for nv in self.NV}
        rule_R = {v:[] for v in self.V}
        for rule in self.rules:
            nv = rule[0]
            vs = rule[1:]
            rule_L[nv].append(rule)#左
            for v in vs:#右
                rule_R[v].append(rule)
        return rule_L,rule_R


if __name__ == '__main__':
    g=Grammar(S="ID")
    g.from_file('grammars/identifier.txt')
    g.init(True)
    g.show()

   


