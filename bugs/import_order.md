```
# logicY0.py
from semantic import LineParser, Switcher, Context, TermAnalyzer, TermConverter, Sort, Var
```

正确
```
# semmantic/__init__.py
from .convert import TermConverter
from .logicY0 import CMDLogicY0
```
错误
```
from .logicY0 import CMDLogicY0
from .convert import TermConverter

ImportError: cannot import name 'TermConverter' from partially initialized module 'semantic' (most likely due to a circular import) (d:\WorkPlace\Pathon_WorkPlace\compile\semantic\__init__.py)
```
