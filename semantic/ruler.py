class RuleSet():
    def __init__(self, lines: str) -> None:
        """
        规则集
        - lines : 若干规则, 格式为 {p1,p2,..} |- q
        """
        self.rules: list[tuple[list[str], str]] = []
        for line in lines:
            ps , q = line.split("|-")
            ps = ps.strip(" {}").split(",")
            ps = [p.strip() for p in ps if p.strip()]
            self.rules.append((ps,q.strip()))
if __name__ == "__main__":
    pass