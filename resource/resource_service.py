import os
class ResourceService:
    """
    资源类,用来解决相对路径问题
    """

    @staticmethod
    def get(path: str) -> str:
        """
        获取资源的绝对路径
        - path: 资源的相对路径(相对于resource.py所在目录resource)
        ###  return
        资源的绝对路径
        """
        return os.path.join(os.path.dirname(__file__), path)