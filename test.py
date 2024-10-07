solution = {1:{5},2:{4}}
import pandas
from pandas import DataFrame
C= ["x","b","v"]
df = DataFrame(columns=C)

df = pandas.concat([df,DataFrame(columns=C,data=[[1,2,3]])])
print(df)

a ={1}
b={2}
c = a|b
print(c)
a.add(4)
print(c)
print(a)

def f():
    return
    for i in range(10):
        yield i
g = f()
for i in g:
    print(i)
print(g)
vs =[1,2,3]
for v in range(len(vs)-1,-1,-1):
    print(v)
vs[1:1+1]=[9,2]
print(vs)


class Base:
    def __init__(self) -> None:
        self.a = 1
    def f(self):
        print(self.a)
    def f2(self, x = 1):
        print(x)
class Derived(Base):
    def __init__(self) -> None:
        super().__init__()
    def f(self, a:int = 2):
        self.a = a
        print(self.a)
        super().f()
    def f2(self, x = ...):
        print(x)
        super().f2(x)
def f(a = ...):
    print(a)
    pass

if __name__ == "__main__":
    d = Derived()
    d.f2()
    d = Base()
    d.f()
    f()
    print(...==...)
    set().union(*[{i} for i in range(10)])
    dc = {1:[],2:"",3:{} }
    for i in list(dc.keys()):
        del dc[i]
    print(dc)
    l = [[0],[3],[10],[3],[2],[1],[8],[6],[7],[3],[6],[7],[4],[3],[3],[7],[3],[6],[10],[8],[8],[5],[7],[7],[3],[4],[0],[5],[0],[4],[7]]
    print([x[0] for x in l])
