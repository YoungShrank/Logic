YXK_LEFT_PARENTHESE = "（" # (
YXK_RIGHT_PARENTHESE = "）"#)
YXK_LEFT_BRACKET = "【" #[
YXK_RIGHT_BRACKET = "】" #]
YXK_COMMA = "，"

class toString:
    @staticmethod
    def tuple2str(*items,seperator=YXK_COMMA) -> str:
        return YXK_LEFT_PARENTHESE + YXK_COMMA.join(map(lambda x: str(x), items)) + YXK_RIGHT_PARENTHESE
    @staticmethod
    def list2str(items:list,seperator=YXK_COMMA) -> str:
        return YXK_LEFT_BRACKET + seperator.join(map(lambda x: str(x), items)) + YXK_RIGHT_BRACKET
    @staticmethod
    def set2str(items:set,seperator=YXK_COMMA) -> str:
        items = [str(i) for i in items]
        sorted_items = sorted(items)
        return toString.list2str(sorted_items,seperator)
if __name__ == "__main__":
    print(toString.tuple2str(1,2,3))
    print(toString.list2str([1,2,3]))
    print(toString.set2str({1,2,3}))

    print(toString.set2str({1,2,3}, seperator="\n"))