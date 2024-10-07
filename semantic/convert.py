import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from abtree import ABTree
from utils import basiccopy
from context import Var

class TermConverter:
    """
    不涉及附加语义的语义转换器，符号级/语法级的语义转换（也就是只要语法树结构/符号序列相同）
    """
    def __init__(self):
        pass
    
    @staticmethod
    def regular_instance(abt: ABTree ,name_t:dict[str, ABTree], copy_abt = True, copy_name_t = True):
        """
        规范化的量词消去/或者函数应用，采用regular_replace
        - abt : 要被代入的项 (term := xxx), 已分析语义
        - name_t: {name:term}
        - copy_abt : 是否拷贝abt
        - copy_name_t : 是否拷贝name_t
        """
        abt = abt.copy(basiccopy) if copy_abt else abt
        root_data = abt.get_vex(abt.root)
        production = " ".join(root_data["production"])
        match production:
            case "<term> ∀ <varT_list> <term>" :
                j, term = abt.get_child(abt.root, 3)
            case "<term> ∃ <varT_list> <term>":
                j, term = abt.get_child(abt.root, 3)
            case "<term> λ <varT_list> . <term>":
                j, term = abt.get_child(abt.root, 4)
        for x, t in name_t.items():
            appears = root_data["appear"][x] #出现位置
            for i in appears:
                TermConverter.regular_replace(abt, i, t.copy(basiccopy) if copy_name_t else t)
        return abt.copy_subtree(j).totext(" ")
    
    @staticmethod
    def rename(abt: ABTree, old:str, new:str, copy_abt = True):
        """
        变量重命名
        - abt: 项
        - old:原名
        - new:新名
        - copy_abt = True 
        """
        abt = abt.copy(basiccopy) if copy_abt else abt
        root_data = abt.get_vex(abt.root)
        production = " ".join(root_data["production"])
        match production:
            case "<term> ∀ <varT_list> <term>" :
                j, term = abt.get_child(abt.root, 3)
            case "<term> ∃ <varT_list> <term>":
                j, term = abt.get_child(abt.root, 3)
            case "<term> λ <varT_list> . <term>":
                j, term = abt.get_child(abt.root, 4)
        for i, node in abt.iter(order="post"):
            if node.get("symbol") == "<var>" and node["value"] == old:
                node["value"] = new
        return abt.totext(" ")
    
    @staticmethod
    def select(abt: ABTree, leafs:list[int]):
        """
        选择项,选择规则是，叶子的最近公共<term>祖先
        - leafs: 叶子的id
        # returns
        - ancestor: 祖先节点id
        """
        ancestors = abt.common_ancestors(leafs)
        for ancestor in ancestors:
            node = abt.get_vex(ancestor)
            if node.get("symbol") == "<term>":
                return ancestor
    @staticmethod
    def select_by_pos(abt: ABTree, poses:list[int]):
        """
        选择项，但是poses是叶子的序号(0,1,..)
        - poses: 叶子的序号
        # returns
        - ancestor: 祖先节点id
        """
        all_leafs = [i for i,_ in abt.iter_leafs()]
        leafs = [all_leafs[i] for i in poses]
        return TermConverter.select(abt, leafs)
    @staticmethod
    def into_able(abt: ABTree):
        """
        判断是否可直接代入，即(t)或者 var
        - abt : 待判断的 <term>
        """
        t_production = abt.get_vex(abt.root).get("production")
        return " ".join(t_production) in ["<term> ( <term> )", "<term> <var>"]

    @staticmethod
    def equal_replace( equal_t:ABTree, abt:ABTree, oldi:int, old_side:str = "left", copy_abt = True):
        """
        等值替换, t((old)→(new))
        - equal_t: 等式 (old) = (new) 或者(new) = (old)
        - abt : 待替换的项
        - oldi: old的id
        - old_side: old所在的侧
        - copy_abt : 是否复制abt
        """
        abt = abt.copy(basiccopy) if copy_abt else abt 
        equal_root:dict = equal_t.get_vex(equal_t.root)
        production = equal_root.get("production")
        po, pn = (1, 3) if old_side == "left" else (3, 1)
        # 获得 to,tn,并验证
        assert production == ["<term>", "<term>", "=", "<term>"]
        jo, to = equal_t.get_child(equal_t.root, po)
        assert to.get("production") == ["<term>", "(", "<term>", ")"]
        jn, tn = equal_t.get_child(equal_t.root, pn)
        assert tn.get("production") == ["<term>", "(", "<term>", ")"]
        # 判断 等式中的old和abt 中old相等
        to_in_e = equal_t.copy_subtree(jo)
        to_in_t = abt.copy_subtree(oldi)
        print(to_in_e.totext(" "), to_in_t.totext(" "))
        assert ABTree.equal(to_in_e, to_in_t)
        # 替换
        abt.substitute(oldi,equal_t.copy_subtree(jn, basiccopy))
        return abt.totext(" ")
    
    @staticmethod
    def regular_replace(abt: ABTree, desi: int, srct: ABTree):
        """
        规范替换项，即替换前加括号, 不会共用srct，因为totext了,一般不copy，因为i与abt实现有关,于是会改变abt。
        - abt : 操作项
        - desi: 被替换的项的id
        - srct: 待替入的项
        """
        holder = {"value": "( " + srct.totext(" ") + " )"}
        temp = ABTree()
        root = temp.add_nameless_vex(holder)
        temp.set_root(root)
        abt.substitute(desi, temp)
        return abt.totext(" ")
    @staticmethod
    def regular_fillin(template: ABTree, name_t: dict[str, ABTree],
                       copy_template = True):
        """
        规范的模板填充, name_t不会被共用
        - template: 模板（如 p->q）,无需计算语义
        - name_t: {name:t}
        - copy_template : 是否拷贝template
        """
        template = template.copy(basiccopy) if copy_template else template
        ivars = [(i, node) for i, node in template.iter(order="post") 
                 if node.get("production") == ["<term>", "<var>"]]
        for i, node in ivars:
            j, var = template.get_child(i, 1)
            name = var["value"]
            assert name in name_t # 完全替换
            t = name_t[name]
            TermConverter.regular_replace(template, i, t)
        return template.totext(" ")
    @staticmethod
    def regular_deduce(presumptions:list[ABTree], templates:list[ABTree],
                       name_t:dict[str,ABTree], conclusion:ABTree):
        """
        规范化的演绎，会复制templates，conclusion； presumptions,name_t不受影响
        - presumptions: 前提
        - templates: 前提模板
        - name_t: {name:t} 实例
        - conclusion: 结论模板
        # returns
        filled_conclusion | None
        """
        filled_templates = [TermConverter.regular_fillin(tmp, name_t) 
                            for tmp in templates ]
        presumption_strs = [abt.totext(" ") for abt in presumptions]
        if presumption_strs == filled_templates:
            print([t.totext(" ") for t in templates],
                  "|-",
                  conclusion.totext(""))
            return TermConverter.regular_fillin(conclusion, name_t)
        else:
            return None
    @staticmethod
    def introduce(abt: ABTree, name_var: dict[str, Var], type_: str, copy_abt = True):
        """
        量词引入
        - abt: 待引入的项
        - name_var: {name:var}, 待引入的变量
        - type_: "∀"(all) or "∃"(exist) 
        -  copy_abt : 是否复制 abt
        """
        if type_ == "exist":
            type_ = "∃"
        elif type_ == "all":
            type_ = "∀"
        assert type_ in ["∀","∃"]
        abt = abt.copy(basiccopy) if copy_abt else abt
        # 换名
        term = abt.get_vex(abt.root)
        free_dict = term["free"]
        for name in name_var.keys():
            free_ids = free_dict[name]
            new_name = name_var[name].name
            for i in free_ids:
                abt.get_vex(i)["value"] = new_name
        term_str = abt.totext(" ")
        varTs = " ".join([f"{var.name} : {var.sort.to_words()}," 
                          for name, var in name_var.items()])
        return f"{type_} {varTs} {term_str}"
    
    @staticmethod
    def apply(abt: ABTree, f: Var, name_t: dict[str, ABTree], copy_abt = True, copy_name_t = True):
        """
        函数应用:  f (t1, t2,) = t (a -> (t1) , b -> (t2))
        - abt : lambda x:N, t(x)
        - f : var: Func
        - name_t: {name:t}
        - copy_abt = True
        - copy_name_t = True
        # returns
        f (t1, t2,) = t (a -> (t1) , b -> (t2))
        """
        root_data:dict = abt.get_vex(abt.root)
        assert root_data.get("production") == ["<term>", "λ", "<varT_list> ", ".", "<term>"]
        i, t = abt.get_child(abt.root, 4)
        abt = abt.copy_subtree(i)
        instance = TermConverter.regular_instance(abt, name_t, copy_abt, copy_name_t)  #t (a->t1,b->t2)
        if len(name_t) == 1:#一个参数
            param = list(name_t.values())[0].totext(" ")
            return f"( {f.name} ( {param} ) ) = ( {instance} )"
        params = ""
        for x, t in name_t.items():
            params += f"{t.totext(' ')},"
        return f"( {f.name} ({params}) ) = ( {instance} )"
    
    @staticmethod
    def off_bracket(abt: ABTree, i:int = None, copy_abt = True):
        """
        去掉括号
        - i: term := ( term ) 的节点id，默认为 root
        # returns
        - text: 替换后的文本
        - abt: 预期的语法结构
        - copy_abt = True
        """
        abt = abt.copy(basiccopy) if copy_abt else abt
        i = i if i is not None else abt.root
        assert abt.get_vex(i).get("production") == ["<term>", "(", "<term>", ")"]
        j, _ = abt.get_child(i, 2)
        subt = abt.copy_subtree(j, basiccopy)
        abt.substitute(i, subt)
        return abt.totext(" "), abt
    @staticmethod
    def on_bracket(abt: ABTree, i: int = None, copy_abt = True):
        """
        加上括号
        - i: term := ... 的节点id, 默认 root
        - copy_abt = True
        """
        abt = abt.copy(basiccopy) if copy_abt else abt
        i = i if i is not None else abt.root
        term = abt.copy_subtree(i)
        holder = {"value": "( " + term.totext(" ") + " )"}
        temp = ABTree()
        root = abt.add_nameless_vex(holder)
        temp.set_root(root)
        abt.substitute(i, temp)
        return abt.totext(" ")
    @staticmethod
    def conclude(assumptions: list[ABTree], conclusion: ABTree):
        """
        假设归结,不修改assumptions和conclusion
        - assumptions: 假设
        - conclusion: 结论
        """
        assumptions_strs = [abt.totext(" ") for abt in assumptions]
        assumptions_str = " ∧ ".join([f"( {assumption} )" for assumption in assumptions_strs])
        return f"( {assumptions_str} ) -> ( {conclusion.totext(' ')} )"
    @staticmethod
    def line2term(abt: ABTree, copy_abt = True):
        """
        将line转换为term
        - copy_abt = True
        """
        line = abt.copy(basiccopy) if copy_abt else abt
        assert line.get_vex(line.root).get("production") == ["<line>","<term>"]
        i, _ = line.get_child(line.root, 1)
        term = line.copy_subtree(i)
        return term

if __name__ == "__main__":
    print("test")
