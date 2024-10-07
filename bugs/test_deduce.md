## 现象描述
在执行测试脚本[test_deduce](../test/test_deduce.py)时，报错

```Traceback (most recent call last):
  File "d:\WorkPlace\Pathon_WorkPlace\compile\test\test_deduce.py", line 33, in <module>
    test()
  File "d:\WorkPlace\Pathon_WorkPlace\compile\test\test_deduce.py", line 25, in test
    TermAnalyzer(p,env).solve()
  File "d:\WorkPlace\Pathon_WorkPlace\compile\semantic\line.py", line 108, in solve
    self.solve_var()
  File "d:\WorkPlace\Pathon_WorkPlace\compile\semantic\line.py", line 171, in solve_var
    parent_sort = node["bound"][sort.name]
KeyError: 'M'
```
## 原因分析
很简单
`( ( ∀ x : M , ( Q x ) ) ∨ ( ∀ x : M , ( P x ) ) )`中的M
既没有作为预定义类，也没有作为自定义类(集合)。

### 代码解读
`parent_sort = node["bound"][sort.name]` 中的bound为{name:sort}，该行代码出现在sort不是预定义类的条件下，sort.name此时应该是集合变量名，不过两者都没有满足。

### 解决
在Context的Sort中加入‘M’;

### 教训

可能出现的错误要考虑到并捕获，并报告出错原因。