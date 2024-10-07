from typing import Any
def basiccopy(x: Any):
    """
    复合类型的深拷贝（不包括自定义对象，只有基本类型）
    - x: Any, 待拷贝的对象
    # returns
    拷贝后的对象
    """
    if isinstance(x, dict):
        return dict(map(basiccopy, x.items()))
    elif isinstance(x, (list, tuple, set)):
        return type(x)(map(basiccopy, x))
    else:
        return x
def tostr(x: Any):
    """
    递归转换为字符串
    """
    if isinstance(x, dict):
        return "{" + ", ".join(f"{k}: {tostr(v)}" for k, v in x.items()) + "}"
    elif isinstance(x, list):
        return "[" + ", ".join(tostr(v) for v in x) + "]"
    elif isinstance(x, tuple):
        if len(x) == 1:
            return "(" + tostr(x[0]) + ",)"
        return "(" + ", ".join(tostr(v) for v in x) + ")"
    elif isinstance(x, set):
        return "{" + ", ".join(tostr(v) for v in x) + "}"
    else:
        return str(x)

if __name__ == "__main__":
    a = [1,2,3,4,5,6,7,8,9,10]
    d = {1:2,3:4,5:6}
    t = (1,)
    l = [1,10]
    a[0] = d
    a[1] = t
    a[2] = l
    b = basiccopy(a)
    a[0][1] = 30
    a[2].append(20)
    print(a,b)
    print(tostr(a))
