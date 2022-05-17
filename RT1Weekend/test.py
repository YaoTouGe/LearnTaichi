from enum import IntEnum
import taichi as ti
import colorful
from datatypes import *

# colorful tests
colorful.print_bold("bold")
colorful.print_error("error")
colorful.print_header("header")
colorful.print_warning("warning")
colorful.print_ok("ok")
colorful.print_underline("underline")

# while test
idx = 0
while idx < 10:
    if idx > 8:
        break
    idx+=1
else:
    print("while else")

ti.init(arch=ti.gpu)
data = ti.field(ti.float32, shape=10)

@ti.func
def b(d, i):
    d[i] = i*2 - 10

@ti.kernel
def f():
    for i in ti.static(range(10)):
        b(data, i)
    for i in data:
        if data[i] > 0:
            continue
        print(data[i])
    x = vec4([1,2,3,4])
    a = x[0:3]
    b = x[1:4]
    print(a.dot(b))
    print(ti.min(a,b))
# f()
