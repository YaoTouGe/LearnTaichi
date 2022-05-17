from enum import IntEnum
import taichi as ti
import colorful

@ti.kernel
def f():
    idx = 0
    a = ti.Vector([1,2,3,4])
    for i in ti.static(range(a.n)):
        print(a[i])

class Test(IntEnum):
    X = 0
    Y = 1

# ti.init(arch=ti.gpu)
# f()

# a = Test.X
# print(type(Test.Y))

colorful.print_bold("hhhh")
colorful.print_error("hhhh")
colorful.print_header("hhhh")
colorful.print_warning("hhhh")
colorful.print_ok("hhhh")
colorful.print_underline("hhhh")