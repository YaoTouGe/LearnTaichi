import taichi as ti

vec9 = ti.types.vector(9, float)
vec6 = ti.types.vector(6, float)
vec5 = ti.types.vector(5, float)
vec4 = ti.types.vector(4, float)
vec3 = ti.types.vector(3, float)
vec2 = ti.types.vector(2, float)

ray = ti.types.struct(origin = vec3, dir = vec3)
hit_record = ti.types.struct(hit_pos = vec3, normal = vec3, t = float, material = int, is_front = int)
sphere = ti.types.struct(center = vec3, radius=float, material=int)
aabb = ti.types.struct(min=vec3, max=vec3, material=int)

'''
geometry type layout:
struct
{
    int type; // 0 sphere 1 AABB 2 XYRect 3 XZRect 4 YZRect 5 Triangle
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

'''
material type layout:

struct
{
    int type; // material type: 0 diffuse 1 specular 2 dielect 3 light
    vec3 color;
}
'''
material = ti.types.struct(type = int, color = vec3)

'''
BVH node layout:
struct
{
    // bounding box
    vec3 min;
    vec3 max;

    // child node id in node array
    int leftChild;
    int rightChild;
    // geometry id in geometry array
    int geometryIdx;
    // next bvh node id for back tracing
    int next;
    // parent index
    int parent
}
'''
bvhnode = ti.types.struct(min = vec3, max = vec3, leftChild = int, rightChild = int, geometryIdx = int, next = int, parent = int)
