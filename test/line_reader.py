import os
# 切换工作目录到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class LineReader():
    def __init__(self, path:str) -> None:
        """
        构造文本行读取迭代器
        - path: 文件路径
        """
        self.path = path
        self.file = open(self.path, "r", encoding="utf-8")
    def __iter__(self):
        """
        迭代器
        """
        while True:
            line = self.file.readline()
            if not line:
                break
            line = line.strip()
            if line:
                yield line

def test():
    """
    测试LineReader
    """
    from resource_service import ResourceService
    reader = LineReader(ResourceService.get("test/sentences/lines.txt"))
    for line in reader:
        print(line)
if __name__ == "__main__":
    test()
