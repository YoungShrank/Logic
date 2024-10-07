## HEAD
- time : 2024-9-22
- author : young
- abstract : 量词引入约束变元的类型，是给定的还是推断的
## 背景
初期只是从实现量词引入的目标出发设计函数，而且没有完善的环境可以获得自由变元类型，[量词引入函数](../semantic/line.py)
```def introduce(self,t:ABTree,name_var:dict[str, Var],type_: str);``` 约束变元的类型是需要外部提供，但是实际上引入的约束变元类型应该和被替换的自由变元一致。 不过有一点，Converter中的函数是完全独立于环境概念的，。

## 问题
introduce的设计破坏了其固有的独立性,但另一方面Converter是独立于环境的。


## 影响



## 可能的解

### 1.新建环境感知的Converter


### 解法影响
#### 积极影响
### 2.暂不处理，使用已有接口

#### 负面影响
无负面影响

