from enum import IntEnum
import colorful
from datatypes import material, vec3

class MaterialType(IntEnum):
    DIFFUSE = 0
    SPECULAR = 1
    DIELECT = 2
    LIGHT = 3

class MaterialTable:
    def __init__(self, max_len):
        self._field = material.field(shape=max_len)
        self._id = 0

    def append(self, mat):
        if self._field.shape[0] <= self._id:
            colorful.print_error("material table exceeds max size")
            return

        self._field[self._id] = mat
        self._id += 1

    def cur_id(self):
        return self._id

    def data(self):
        return self._field

class Material:
    '''
    A Material object register itself in global material table,
    and use it's index as id.
    '''
    def __init__(self, mat_type:MaterialType, mat_color:vec3, mat_table:MaterialTable):
        self._type = mat_type
        self._color = mat_color

        self._id = mat_table.cur_id()
        mat_table.append(material(type = mat_type, color = mat_color))

    def id(self):
        return self._id