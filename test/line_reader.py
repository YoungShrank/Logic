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
if __name__ == "__main__":
    reader = LineReader("./sentences/lines.txt")
    for line in reader:
        print(line)
