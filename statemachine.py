
from grammar import Grammar
from pandas import DataFrame
import pandas
from Structure import DiGraph

class NFA :
    """
    不确定有穷自动机
    """
    def __init__(self, state, accept):
        self.state = state
        self.accept = accept
class DFA :
    """
    确定有穷自动机
    """
    def __init__(self, state, accept, transition):
        self.state = state
        self.accept = accept
        self.transition = transition