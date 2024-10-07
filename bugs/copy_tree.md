## 现象描述
在执行测试脚本[test_term_converter.py](../test/test_term_converter.py)时，报错

```Traceback (most recent call last):
  File "d:\WorkPlace\Pathon_WorkPlace\compile\test\test_term_converter.py", line 82, in <module>
    test()
  File "d:\WorkPlace\Pathon_WorkPlace\compile\test\test_term_converter.py", line 35, in test
    line = TermConverter.regular_fillin(brace, {"t": tabt})
  File "d:\WorkPlace\Pathon_WorkPlace\compile\semantic\convert.py", line 164, in regular_fillin
    TermConverter.regular_replace(template, i, t)
  File "d:\WorkPlace\Pathon_WorkPlace\compile\semantic\convert.py", line 140, in regular_replace
    abt.substitute(desi, temp)
  File "d:\WorkPlace\Pathon_WorkPlace\compile\Structure\tree.py", line 227, in substitute
    self.insert_edge(p,mapper[j],n)
KeyError: 136
```
## 问题定位
### 多出的节点
进入 `regular_fillin`, 添加打印语句
```
print(list(template.vexs))
print(template.root)
template.view(path = "before.html", see_id= True)
template = template.copy(basiccopy) if copy_template else template
template.view(path = "after.html", see_id= True)
print(list(template.vexs.keys()))
```
输出
```
[121, 122, 123, 124, 125, 126, 127]
126
[126, 125, 121, 123, 122, 124]
```
而奇怪的是前后两树的图中均没有127节点，可能是因为127节点在vexs中但是不在tree中.为什么会多一个不在树中的节点呢？
回过头看，树是[test_term_converter.py](../test/test_term_converter.py) 中下面一句生成的
```
brace = line_parser.build_tree(line_parser.lexical("(t)"))
```
打印brace的顶点信息发现，原来只是结束符"#",这倒是问题不大，看来另有原因。
```
127 : {'symbol': '#', 'value': None}
```
### temp写成abt 
直接 进 `regular_replace`,打印`abt.vexs,desi`,发现 desi在vexs中，那就只有可能是 `substitute`的问题了，确实奇怪，一直好好的。 进一步分析发现 temp写成abt，导致temp是空的，set_root也是设置了不存在的root，后面就跟着错了。


## 原因分析


### 代码解读


### 解决


### 教训

set_root前检查一下,也就是提前暴露问题。
