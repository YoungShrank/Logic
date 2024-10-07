import re
def shift(text:str):
    """
    转义
    - text: the given text
    """
    return "".join([f"\\{i}" for i in text])
def union(patterns):
    """
    union the given patterns
    - patterns: the given patterns
    """
    return "|".join([f"({pattern})" for pattern in patterns])
class Word:
    def __init__(self,text,patterns:dict[str,str],vask:set,key2type:dict[str,str]):
        """
        - text: the given text
        - patterns:  patterns of each kind of word [symbol:pattern]
        - vask: keys whose type is value
        - key2type: the type of each key
        """
        self.text = text
        self.pos = 0
        self.vask = vask
        self.key2type = key2type

        pattern = "|".join([f"(?P<{k}>{v})" for k,v in patterns.items()])
        self.pattern = re.compile(pattern)
    def set_text(self, text: str):
        """
        set the text, and initialize the position to 0.
        - text: the given text
        """
        self.text = text
        self.pos = 0
    def filter(self):
        """
        filter the white space at the begin of given text.
        - text: the given text
        """
        text = self.text[self.pos:]
        word = re.match(r"\s*",text)
        if word:
            length = word.end()
            self.pos += length
            return length
        return 0
    def look_one(self,filter=True):
        """
        get the next word of the given text.
        - text: the given text

        # return: (word ,type )
        """
        if filter:
            self.filter()
        text = self.text[self.pos:]
        word = self.pattern.match(text)
        if word:
            for k,v in word.groupdict().items():
                if v:
                    if k in self.vask:
                        k = v
                    else:
                        k = self.key2type[k]
                    return v,k
        return (None,None)
    
    def parse_all(self):
        """
        parse all the words in the given text.
        - text: the given text
        """
        words = []
        while self.pos < len(self.text):
            v, k = self.look_one()
            if k:
                words.append((v,k))
                self.pos += len(v)
            else:
                mid = self.pos
                start = max(0,mid-10)
                end = min(len(self.text),mid+10)
                show = self.text[start:mid]+" ~~~~ "+self.text[mid:end]
                raise Exception(f"error:[{self.pos}] {show}")
        return words
    def parse_one(self):
        """
        parse the first word of the given text.
        - text: the given text
        """
        v, k = self.look_one()
        if k:
            self.pos += len(v)
        return v,k

def common_patterns():
    return {
        "op":union(["=","∈","¬","->","<->","∧","∨","∀","∃",":="]), #运算符
        "del": "[{}]".format(shift("(){}<>[],;:'.*&^%$#@!~|")), #界符
        "key":union(["one","any"]), #关键字
        "var":r"[a-zA-Z_][_a-zA-Z0-9]*", # 变量
        "char" :r"[\+\-⊥]", # 符号
        "num":r"[0-9]+", # 数字
        "space":r"\s+", # 空白
        "other":r"." # 其他
    }
def k2tp():
    vask = {"op","del","key"}
    key2type = {
        "var":"<id>",
        "char":"<id>",
        "num":"<num>",
        "space":"<space>",
        "other":"other"
    }
    
    return vask,key2type



if __name__ == "__main__":
    txt = "one + :=  ∀x,(p->p)∨q->∃y,(¬p<->r)∨{p,q,r}"
    patterns = common_patterns()
    vask,key2type = k2tp()
    w = Word(txt,patterns,vask,key2type)
    ress = w.parse_all()
    w.set_text("one ⊥ : int :=0")
    ress = w.parse_all()
    print(ress)