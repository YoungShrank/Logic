# 命令解析
import re
class Commander:
    def __init__(self) -> None:
        # cmd pos_params  key_params   | remainder
        self.pattern = re.compile(r"(?P<cmd>\w+)\s*(?P<pos_params>[^\-|]*)(?P<key_params>(\-\w*\s+\w*\s*)*)(\|(?P<remainder>.*))?")
    def parse(self, command: str):
        """
        解析命令
        - command: 命令字符串
        # return
        (cmd, pos_params, key_params, remainder)
        """
        result = self.pattern.match(command)
        if result:
            return (result.group("cmd"), 
                    result.group("pos_params").split(), 
                    dict([k_v.split() for k_v in result.group("key_params").split('-') if k_v.strip()]),
                    result.group("remainder")
                    )
        else:
            return None

if __name__ == "__main__":
    cmder = Commander()
    print(cmder.parse("add  -k2 2 | "))
    print(cmder.parse("add   | "))
    print(cmder.parse("add "))