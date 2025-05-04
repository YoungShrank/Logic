# 导入磁盘上其他的python文件
# 在模块被导入时，__init__.py文件会被自动执行
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))) # 父目录路径
sys.path.extend(
    [
        "D:/WorkPlace/github"
    ]
)  # 依赖的路径
print(sys.path)  # 打印当前的sys.path列表