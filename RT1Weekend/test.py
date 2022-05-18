from enum import IntEnum
import taichi as ti
import colorful
from datatypes import *

@ti.data_oriented
class test:
    def __init__(self) -> None:
        self.x = 1

    def inc(self):
        self.x += 1

    @ti.func
    def get_x(self):
        return self.x

    @ti.kernel
    def tt(self):
        print(self.x)

t = test()

ti.init(ti.gpu)

t.tt()
t.inc()
t.tt()