## HEAD
- time : 2024-9-22
- author : young
- abstract : 应用规则和环境切换独立
## 背景
由于模块化的要求，规则应用封装在[Converter](../semantic/line.py)中，而环境切换封装在[Switcher](../semantic/line.py)中，不过应用规则（如消去，引入）会伴随者相应的转换，这种转换可以作为独立的模块封装起来。

## 问题



## 影响

两者真的有很大关联吗？

## 可能的解
新建Applyer 类，该类基于 Converter 和 Switcher，实现应用规则对项进行变换，并且进行环境切换。其中每个函数进行一种规则的应用。比如消去规则:
```
def instance(abt, var_abt_dict, env):
    line = Converter.instance(abt, var_abt_dict)
    result = semantic_parse(line)
    Switcher(env, result).switch()
```

### 解法影响
#### 积极影响
实现模块化，结构更清晰，实现更容易

#### 负面影响
无负面影响
