import taichi as ti

vec9 = ti.types.vector(9, float)
vec5 = ti.types.vector(5, float)
vec4 = ti.types.vector(4, float)
vec3 = ti.types.vector(3, float)
vec2 = ti.types.vector(2, float)

'''
geometry type layout:
struct
{
    int type; // 0 sphere 1 AABB 2 XYRect 3 XZRect 4 YZRect
    int material; // material id in material table

    union
    {
        // sphere
        vec4; // vec3 center float radius 

        // AABB
        vec6; // vec3 min vec3 max

        // XY/XZ/YZ Rect
        vec5; // vec2 min vec2 max float axis 

        // triangle in future
        vec9; // three vertices
    };
};
''' 
geometry = ti.types.struct(type = int, material = int, data = vec9)
sphere = ti.types.struct(center = vec3, radius=float)

'''
material type layout:

struct
{
    int type; // material type: 0 diffuse 1 specular 2 dielect 3 light
    vec3 color;
}
'''
material = ti.types.struct(type = int, color = vec3)