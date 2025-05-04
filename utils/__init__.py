import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))) # 父目录路径
from .comcopy import basiccopy, tostr
from .printer import Printer
from .line_reader import LineReader
from .serialize import JsonSerializer
from .list_algorithm import ListAlgorithms
from .tostring import toString