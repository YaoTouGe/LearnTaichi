import taichi as ti
from datatypes import *
from material import MaterialType

@ti.func
def reflect(input_dir, normal):
    out = input_dir.dot(normal) * 2 * normal - input_dir
    return out.normalized()

@ti.func
def test_AABB(ray, min, max, t_min:float, t_max:float):
    dir_inv = 1 / ray.dir
    t0s = (min - ray.origin) * dir_inv
    t1s = (max - ray.origin) * dir_inv

    min_ts = ti.min(t0s, t1s)
    max_ts = ti.max(t0s, t1s)

    return ti.max(min_ts.max(),t_min) < ti.min(max_ts.min(), t_max)

@ti.func
def intersect_AABB(ray, aabb, t_min:float, t_max:float, rec: ti.template()):
    pass

@ti.func
def intersect_sphere(r, sphere, t_min:float, t_max:float, rec: ti.template()):
    oc = r.origin - sphere.center
    a = r.dir.dot(r.dir)
    half_b = r.dir.dot(oc)
    c = oc.dot(oc) - sphere.radius * sphere.radius

    discriminant = half_b * half_b - a * c
    ret = True
    if discriminant < 0:
        ret = False
    else:
        discrimSqrt = ti.sqrt(discriminant)
        t = (-half_b - discrimSqrt) / a
        if t < t_min or t > t_max:
            t = (-half_b + discrimSqrt) / a
            if t < t_min or t > t_max:
                ret = False
        if ret:
            rec.hit_pos = r.origin + r.dir * t
            rec.normal = (rec.hit_pos - sphere.center) / sphere.radius
            rec.is_front = rec.normal.dot(-r.dir) > 0
            if not rec.is_front:
                rec.normal = -rec.normal
            rec.material = sphere.material
            rec.t = t
    return ret

@ti.func
def extract_sphere(geom):
    return sphere(center=geom.data[0:3], radius=geom.data[3], material=geom.material)

@ti.func
def intersect_geom(r, geom, t_min:float, t_max:float, rec: ti.template()):
    # TODO: switch geometry type
    return intersect_sphere(r, extract_sphere(geom),t_min, t_max, rec)

@ti.func
def random_float(min, max):
    return min + ti.random(float) * (max - min + 0.000001)

@ti.func
def random_vec3(min, max):
    return vec3(random_float(min, max), random_float(min, max), random_float(min, max))

@ti.func
def random_in_unit_sphere():
    dir = random_vec3(-1, 1)
    while dir.dot(dir) > 1:
        dir = random_vec3(-1, 1)
    return dir

@ti.func
def random_on_unit_sphere():
    return random_in_unit_sphere().normalized()

@ti.func
def approximate_zero(v, epsilon=0.0001):
    return (ti.abs(v) <= epsilon).any()

# TODO: use template to pass argument by reference not working!! why?
@ti.func
def refract(dir, n, refractionRatio):
    cosTheta = ti.min(dir.dot(n), 1)
    outPerp = refractionRatio * (-dir + cosTheta * n)
    outParallel = -ti.sqrt(ti.abs(1 - outPerp.dot(outPerp))) * n
    return outPerp + outParallel

@ti.func
def FresnelSchlick(cosine, refIdx):
    F0 = (1 - refIdx) / (1 + refIdx)
    F0 *= F0
    return F0 + (1 - F0) * ti.pow(1 - cosine, 5)

@ti.func
def material_scatter(r, rec, material_field, scatter_dir:ti.template(), attenuation:ti.template()):
    mat = material_field[rec.material]
    scatter_dir = vec3(0)
    attenuation = mat.color

    ret = True
    if mat.type == MaterialType.DIFFUSE:
        scatter_dir = rec.normal + random_on_unit_sphere()
    elif mat.type == MaterialType.SPECULAR:
        scatter_dir = reflect(-r.dir.normalized(), rec.normal)
    elif mat.type == MaterialType.LIGHT:
        ret = False
    elif mat.type == MaterialType.DIELECT:
        ir = mat.color.x
        refractionRatio = (1 / ir) if rec.is_front else ir
        attenuation = vec3(1, 1, 1)
        unitDirection = -r.dir.normalized()
        cosTheta = ti.min(unitDirection.dot(rec.normal), 1)
        sinTheta = ti.sqrt(1 - cosTheta * cosTheta)

        # if full reflection or fresnel reflection
        if sinTheta * refractionRatio > 1 or FresnelSchlick(cosTheta, refractionRatio) > ti.random(float):
            scatter_dir = reflect(unitDirection, rec.normal)
        else:
            scatter_dir = refract(unitDirection, rec.normal, refractionRatio)

    # if (approximate_zero(scatter_dir)):
    #     scatter_dir = rec.normal
    return ret

@ti.func
def ray_color(r, bvh_field, geom_field, material_field, max_depth, bg_color):
    ret = vec3(1, 1, 1)
    rec = hit_record(0)
    depth = 0

    while depth < max_depth:
        # intersect bvh
        if bvh_intersect(r, bvh_field, geom_field, 0.001, 99999.9, rec):
            # material response
            scatter_dir = vec3(0)
            att = vec3(0)
            scatter_continue = material_scatter(r, rec, material_field, scatter_dir, att)
            #print(scatter)

            # color accumulate
            ret = ret * att
            if not scatter_continue:
                break
            r = ray(origin = rec.hit_pos, dir = scatter_dir)
            depth += 1
        else:
            ret = ret * bg_color
            break
        
    if depth >= max_depth:
        ret = vec3(0, 0, 0)
    
    return vec4(ret, 1)

@ti.func
def bvh_intersect(r, bvh_field, geom_field, t_min: float, t_max: float, rec: ti.template()):
    # start from root node
    ret = False
    cur_node = 0
    while cur_node >= 0:
        node = bvh_field[cur_node]

        if not test_AABB(r, node.min, node.max, t_min, t_max):
            cur_node = node.next
            continue

        # leaf node, intersect with geometry
        if node.geometryIdx != -1:
            local_rec = hit_record(0)
            if intersect_geom(r, geom_field[node.geometryIdx], t_min, t_max, local_rec):
                ret = True
                if local_rec.t < t_max:
                    rec = local_rec
                    t_max = local_rec.t

            cur_node = node.next
        else:
            cur_node = node.leftChild

    return ret
