# 以易于查看的形式打印

class Printer():
    @staticmethod
    def print_head(head_name: str = "END", width = 32):
        """
        以##--head_name--##形式输出头
        - head_name: 头名
        - width: 输出长度 不包括 ‘#’
        """
        assert width > 5
        head_name = Printer.align(head_name, width, fill="-")
        print("##{}##".format(head_name))
    @staticmethod
    def align(s:str ,width: int, fill:str = " "):
        """
        居中对齐(中文实际上会比预期长)
        - fill : 填充字符
        - s : 文本
        - width : 输出宽度
        """
        # 太长省略
        s = str(s)
        if len(s) > width:
            s = s[:width-3] + "..."
        # 居中
        left_fill = (width - len(s)) // 2
        right_fill = (width - len(s)) - left_fill
        return fill*left_fill + s + fill*right_fill

    @staticmethod
    def print_attr(name, value, mapper = str):
        """
        输出属性, value为基本类型(复合类型只一层) 或者实现了 __str__
        - name: 属性名
        - value: 属性值
        - mapper: 映射函数
        """
        if isinstance(value, (int, float, str, None.__class__)):
            print("{}: {}".format(name, value))
        elif isinstance(value, (list, tuple)):
            print("{} :".format(name))
            colums = ["index", "value"]
            data = [[i, mapper(item)] for i, item in enumerate(value)]
            Printer.print_table(colums, data)
        elif isinstance(value, dict):
            print("{} :".format(name))
            colums = ["name", "value"]
            data = [[k, mapper(v)] for k, v in value.items()]
            Printer.print_table(colums, data)
        else:
            print("{}: {}".format(name, value.__str__()))
    def print_table(columns: list[str], data: list[list[str]], limit: int = 64):
        """
        输出表格
        |col1|col2|col3|
        |----|----|----|
        |data1|data2|data3|
        |data1|data2|data3|
        - columns: 表头
        - data: 数据
        - limit: 限制cell宽度
        """
        # 每列宽度最大值
        max_widths = [ max([ len(str(row[i])) for row in data  ] + [len(columns[i])]) for i in range(len(columns))]
        max_widths = [min(limit, width) for width in max_widths]
        horizontal_lines = [ "-"*width for width in max_widths]
        for row in [columns, horizontal_lines] + data:
            print("|", end="")
            for i, cell in enumerate(row):
                print(Printer.align(cell, max_widths[i]), end="|")
            print()
        
        

if __name__ == "__main__":

    Printer.print_head("ffffffffffffffffffffffff")
    Printer.print_head()
    colums = ["name", "age", "sex"]
    data = [["zhangsan", 18, "man"], ["lisi", 19, "women"]]
    Printer.print_table(colums, data)

    dict_value = {"name": "jfjlkajflsajdflkasjdfl", "age": 18, "sex": "man"}
    Printer.print_attr("dict_value", dict_value)
    list_value = [1, 2, 3]
    Printer.print_attr("list_value", list_value)
    Printer.print_attr("none_value", None)
        

