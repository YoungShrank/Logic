
from Structure import Tree,VTree
class ABTree(Tree):
    def __init__(self,tree:Tree=None):
        super().__init__(True)#有序树
        self.input:list[int] = []
        if tree is not None:
            self.from_tree(tree)
    def totext(self,join:str =None):
        """
        语法树转单词序列
        - join: 连接符号,如果没有不连接
        """
        text =  [data["value"] for i,data in self.iter_leafs()]
        if join is not None:
            return join.join([str(x) for x in text])
        else:
            return text
    def tosymbols(self,join:str =None):
        """
        语法树转符号序列
        - join: 连接符号,如果没有不连接
        """
        symbols = [data["symbol"] for i,data in self.iter_leafs()]
        if join is not None:
            return join.join([str(x) for x in symbols])
        else:
            return symbols
    def make_data(self,symbol,production=None,value:str=None):
        """
        语法树节点数据
        - symbol:符号
        - production:产生式
        - value:值
        """
        if production is not None:
            return {"symbol":symbol,"production":production}
        else:
            return {"symbol":symbol,"value":value}
    def deduce(self,production:list[str],pos:int) -> None:
        """
        推导，自顶向下构建语法树
        - production:产生式
        - pos:当前推导到的位置
        """
        i = self.input[pos]
        if len(production[1:])==0: #空产生式
            j = self.add_vex('')
            self.add_edge(i,j)
            self.input[pos:pos+1] = []
        else:#非空产生式
            js = self.add_nameless_vexs(production[1:])
            self.add_edges([(i,j) for j in js])
            self.input[pos:pos+1]=js
    def copy_subtree(self, i, data_copy = lambda x:x) :
        """
        复制子树
        - i:节点
        - data_copy:数据复制函数
        """
        return ABTree(super().copy_subtree(i, data_copy))
    def clear(self):
        """
        清除语义信息
        """
        for i, data in self.iter():
            for k in list(data.keys()):
                if k not in {"symbol","production","value"}: #保留基本信息
                    del data[k]
    def copy(self, data_copy = lambda x:x):
        """
        复制自身
        """
        return self.copy_subtree(self.root, data_copy)
    def accept(self):
        """
        接受
        S' -> S #
        """
        S = self.input[0]
        self.set_root(S)

    def reduce(self,production:list[str],pos:int=None):
        """
        规约，自底向上构建语法树
        - production:产生式
        - pos:规约的起始位置
        """
        if pos is None:
            start = len(self.input)-len(production[1:])
        else:
            start = pos
        end = start+len(production[1:])
        i = self.add_nameless_vex(self.make_data(production[0],production))
        if start == end:#空串规约
            j = self.add_nameless_vex(self.make_data(''))
            self.add_edge(i,j)
        else:#非空串规约
            for j in self.input[start:end]:
                self.add_edge(i,j)
        self.input[start:end] = [i]
    def movein(self,x:str,v:str ):
        """
        移入，添加叶子
        - x : token
        - v : 值
        """
        i = self.add_nameless_vex(self.make_data(x,value=v))
        self.input.append(i)
    def view(self,*items,see_vaule = False,path="abtree.html", see_id = False) -> None:
        """
        查看语法树
        - see_vaule:是否显示值
        - items:要显示的项
        - see_id : 是否显示id,debug用
        """
        show_items = ["symbol"]
        if see_vaule: #显示值
            show_items.append("value")
        show_items.extend(items)
        def viewf(i,data):
            text =  " \n ".join(["{}".format(data[x]) for x in show_items if x in data])
            return "{} \n {}".format(i, text) if see_id else text
        vtree = VTree(self)
        vtree.view(viewf,path=path)
    @staticmethod
    def equal(abt1,abt2):
        """
        判断语法上的相等
        """
        abt1 : ABTree = abt1
        abt2 : ABTree = abt2
        def _equal(i1,i2):
            node1 = abt1.get_vex(i1)
            node2 = abt2.get_vex(i2)
            current_ok = False
            if node1["symbol"] == node2["symbol"]: #符号相同
                if "value" in node1 and "value" in node2: #值相同
                    current_ok =  node1["value"] == node2["value"]
                elif "production" in node1 and "production" in node2: #产生式相同
                    current_ok =  node1["production"] == node2["production"]
            if current_ok :
                return all([_equal(j1,j2) for (j1,_),(j2,_) in zip(abt1.get_childs(i1),abt2.get_childs(i2))])
            else:
                return False
        return _equal(abt1.root,abt2.root)




if __name__ == "__main__":
    from typing import Any
    def basiccopy(x: Any):
        """
        复合类型的深拷贝（不包括自定义对象，只有基本类型）
        - x: Any, 待拷贝的对象
        # returns
        拷贝后的对象
        """
        if isinstance(x, dict):
            return dict(map(basiccopy, x.items()))
        elif isinstance(x, (list, tuple, set)):
            return type(x)(map(basiccopy, x))
        else:
            return x
    abt = ABTree()
    abt.movein("a",[1])
    abt.movein("b",[2])
    abt.reduce(["S","a","b"])
    abt.accept()
    abt.init_parents()
    abt2 = abt.copy(basiccopy)
    print("----- abt ----")
    print(list(abt.vexs))
    print("----- abt2 ----")
    print(list(abt2.vexs))
    list(abt.iter_leafs())[-1][-1]["value"].append(3)
    abt.show()
    abt2.show()
    abt2.view(see_vaule=True)
    print(abt2.totext(join=" "),"|",abt.totext(join=" "))
    print(ABTree.equal(abt2, abt))
    
    