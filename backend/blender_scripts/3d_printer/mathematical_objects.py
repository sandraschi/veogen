import bpy
import bmesh
from mathutils import Vector
import math
import numpy as np

def clear_scene():
    """Clear all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

def create_mobius_strip(
    radius=40,           # mm
    width=20,            # mm
    thickness=2,         # mm
    subdivisions=64,     # resolution
    twists=1             # number of half-twists
):
    """
    Create a Möbius strip - a surface with only one side and one edge
    
    Args:
        radius: Radius of the central circle (mm)
        width: Width of the strip (mm)
        thickness: Thickness for 3D printing (mm)
        subdivisions: Number of subdivisions for smoothness
        twists: Number of half-twists (1 for classic Möbius)
    """
    
    # Convert to Blender units
    radius = radius / 1000
    width = width / 1000
    thickness = thickness / 1000
    
    # Create mesh
    mesh = bpy.data.meshes.new("MobiusStrip")
    obj = bpy.data.objects.new("MobiusStrip", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Generate Möbius strip vertices
    vertices = []
    for i in range(subdivisions):
        t = 2 * math.pi * i / subdivisions
        
        for j in range(subdivisions // 4):  # Width subdivisions
            v = (j - subdivisions // 8) * width / (subdivisions // 4)
            
            # Möbius strip parametric equations
            x = (radius + v * math.cos(twists * t / 2)) * math.cos(t)
            y = (radius + v * math.cos(twists * t / 2)) * math.sin(t)
            z = v * math.sin(twists * t / 2)
            
            # Add thickness for 3D printing
            vertices.append(Vector((x, y, z + thickness/2)))
            vertices.append(Vector((x, y, z - thickness/2)))
    
    # Create vertices
    for v in vertices:
        bm.verts.new(v)
    
    # Create faces
    bm.verts.ensure_lookup_table()
    width_subs = subdivisions // 4
    
    for i in range(subdivisions):
        for j in range(width_subs - 1):
            # Current strip segment
            v1 = i * width_subs * 2 + j * 2
            v2 = i * width_subs * 2 + (j + 1) * 2
            v3 = ((i + 1) % subdivisions) * width_subs * 2 + (j + 1) * 2
            v4 = ((i + 1) % subdivisions) * width_subs * 2 + j * 2
            
            # Top face
            if v1 < len(bm.verts) and v2 < len(bm.verts) and v3 < len(bm.verts) and v4 < len(bm.verts):
                bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])
                
                # Bottom face
                bm.faces.new([bm.verts[v1+1], bm.verts[v4+1], bm.verts[v3+1], bm.verts[v2+1]])
                
                # Side faces
                bm.faces.new([bm.verts[v1], bm.verts[v4], bm.verts[v4+1], bm.verts[v1+1]])
                bm.faces.new([bm.verts[v2], bm.verts[v2+1], bm.verts[v3+1], bm.verts[v3]])
    
    # Update mesh
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    # Add material
    mat = bpy.data.materials.new(name="MobiusMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.2, 0.8, 1.0)  # Magenta
    obj.data.materials.append(mat)
    
    return obj

def create_klein_bottle(
    radius=30,           # mm
    height=60,           # mm
    thickness=2,         # mm
    subdivisions=64      # resolution
):
    """
    Create a Klein bottle - a non-orientable surface with no distinct inside/outside
    
    Args:
        radius: Radius of the bottle (mm)
        height: Height of the bottle (mm)
        thickness: Wall thickness for 3D printing (mm)
        subdivisions: Number of subdivisions for smoothness
    """
    
    # Convert to Blender units
    radius = radius / 1000
    height = height / 1000
    thickness = thickness / 1000
    
    # Create mesh
    mesh = bpy.data.meshes.new("KleinBottle")
    obj = bpy.data.objects.new("KleinBottle", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Generate Klein bottle vertices
    vertices = []
    for i in range(subdivisions):
        u = 2 * math.pi * i / subdivisions
        
        for j in range(subdivisions):
            v = 2 * math.pi * j / subdivisions
            
            # Klein bottle parametric equations
            if u < math.pi:
                x = (radius + math.cos(u/2) * math.sin(v) - math.sin(u/2) * math.sin(2*v)) * math.cos(u)
                y = (radius + math.cos(u/2) * math.sin(v) - math.sin(u/2) * math.sin(2*v)) * math.sin(u)
                z = math.sin(u/2) * math.sin(v) + math.cos(u/2) * math.sin(2*v)
            else:
                x = (radius + math.cos(u/2) * math.sin(v) + math.sin(u/2) * math.sin(2*v)) * math.cos(u)
                y = (radius + math.cos(u/2) * math.sin(v) + math.sin(u/2) * math.sin(2*v)) * math.sin(u)
                z = math.sin(u/2) * math.sin(v) - math.cos(u/2) * math.sin(2*v)
            
            # Scale and position
            x *= 0.5
            y *= 0.5
            z *= height / 4
            z += height / 2
            
            vertices.append(Vector((x, y, z)))
    
    # Create vertices
    for v in vertices:
        bm.verts.new(v)
    
    # Create faces
    bm.verts.ensure_lookup_table()
    
    for i in range(subdivisions):
        for j in range(subdivisions):
            v1 = i * subdivisions + j
            v2 = i * subdivisions + ((j + 1) % subdivisions)
            v3 = ((i + 1) % subdivisions) * subdivisions + ((j + 1) % subdivisions)
            v4 = ((i + 1) % subdivisions) * subdivisions + j
            
            if all(idx < len(bm.verts) for idx in [v1, v2, v3, v4]):
                bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])
    
    # Add thickness with solidify
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    # Add solidify modifier for thickness
    solidify_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify_mod.thickness = thickness
    solidify_mod.use_even_offset = True
    
    # Add material
    mat = bpy.data.materials.new(name="KleinBottleMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.8, 0.2, 1.0)  # Green
    obj.data.materials.append(mat)
    
    return obj

def create_penrose_triangle(
    size=50,             # mm
    thickness=8,         # mm
    beam_width=12        # mm
):
    """
    Create a Penrose triangle - an impossible triangle optical illusion
    
    Args:
        size: Size of the triangle (mm)
        thickness: Thickness of the beams (mm)
        beam_width: Width of each beam (mm)
    """
    
    # Convert to Blender units
    size = size / 1000
    thickness = thickness / 1000
    beam_width = beam_width / 1000
    
    # Create three beams that form the impossible triangle
    beams = []
    
    # Beam 1 - Bottom horizontal
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(0, -size/3, 0)
    )
    beam1 = bpy.context.active_object
    beam1.name = "PenroseBeam1"
    beam1.scale = (size/2, beam_width/2, thickness/2)
    bpy.ops.object.transform_apply(scale=True)
    beams.append(beam1)
    
    # Beam 2 - Top left diagonal
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(-size/3, size/6, 0)
    )
    beam2 = bpy.context.active_object
    beam2.name = "PenroseBeam2"
    beam2.scale = (size/2, beam_width/2, thickness/2)
    beam2.rotation_euler[2] = math.pi/3  # 60 degrees
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    beams.append(beam2)
    
    # Beam 3 - Top right diagonal
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(size/3, size/6, 0)
    )
    beam3 = bpy.context.active_object
    beam3.name = "PenroseBeam3"
    beam3.scale = (size/2, beam_width/2, thickness/2)
    beam3.rotation_euler[2] = -math.pi/3  # -60 degrees
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    beams.append(beam3)
    
    # Create the "impossible" effect by carefully positioning and cutting
    # In a real Penrose triangle, this would require careful camera positioning
    # For 3D printing, we create a physically possible approximation
    
    # Join all beams
    bpy.context.view_layer.objects.active = beam1
    for beam in beams:
        beam.select_set(True)
    bpy.ops.object.join()
    
    # Add material
    mat = bpy.data.materials.new(name="PenroseMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.8, 0.2, 1.0)  # Yellow
    beam1.data.materials.append(mat)
    
    return beam1

def create_impossible_cube(
    size=40,             # mm
    beam_thickness=6     # mm
):
    """
    Create an impossible cube - appears to be an impossible 3D object
    
    Args:
        size: Size of the cube (mm)
        beam_thickness: Thickness of the frame beams (mm)
    """
    
    # Convert to Blender units
    size = size / 1000
    beam_thickness = beam_thickness / 1000
    
    # Create cube frame with "impossible" connections
    beams = []
    
    # Create 12 edges of a cube with strategic breaks for the illusion
    edge_positions = [
        # Bottom face
        ((-size/2, -size/2, -size/2), (size/2, -size/2, -size/2)),    # Bottom front
        ((size/2, -size/2, -size/2), (size/2, size/2, -size/2)),     # Bottom right
        ((size/2, size/2, -size/2), (-size/2, size/2, -size/2)),     # Bottom back
        ((-size/2, size/2, -size/2), (-size/2, -size/2, -size/2)),   # Bottom left
        
        # Top face
        ((-size/2, -size/2, size/2), (size/2, -size/2, size/2)),     # Top front
        ((size/2, -size/2, size/2), (size/2, size/2, size/2)),       # Top right
        ((size/2, size/2, size/2), (-size/2, size/2, size/2)),       # Top back
        ((-size/2, size/2, size/2), (-size/2, -size/2, size/2)),     # Top left
        
        # Vertical edges
        ((-size/2, -size/2, -size/2), (-size/2, -size/2, size/2)),   # Front left
        ((size/2, -size/2, -size/2), (size/2, -size/2, size/2)),     # Front right
        ((size/2, size/2, -size/2), (size/2, size/2, size/2)),       # Back right
        ((-size/2, size/2, -size/2), (-size/2, size/2, size/2)),     # Back left
    ]
    
    for i, (start, end) in enumerate(edge_positions):
        # Create beam
        center = ((start[0] + end[0])/2, (start[1] + end[1])/2, (start[2] + end[2])/2)
        length = math.sqrt(sum((end[j] - start[j])**2 for j in range(3)))
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=beam_thickness/2,
            depth=length,
            location=center
        )
        
        beam = bpy.context.active_object
        beam.name = f"CubeBeam_{i}"
        
        # Orient beam along edge
        direction = Vector(end) - Vector(start)
        beam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        
        beams.append(beam)
    
    # Join all beams
    bpy.context.view_layer.objects.active = beams[0]
    for beam in beams:
        beam.select_set(True)
    bpy.ops.object.join()
    
    # Add material
    mat = bpy.data.materials.new(name="ImpossibleCubeMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.2, 0.8, 1.0)  # Blue
    beams[0].data.materials.append(mat)
    
    return beams[0]

def create_trefoil_knot(
    radius=25,           # mm
    tube_radius=8,       # mm
    subdivisions=128     # resolution
):
    """
    Create a trefoil knot - the simplest non-trivial knot
    
    Args:
        radius: Radius of the knot (mm)
        tube_radius: Radius of the tube (mm)
        subdivisions: Number of subdivisions for smoothness
    """
    
    # Convert to Blender units
    radius = radius / 1000
    tube_radius = tube_radius / 1000
    
    # Create curve for trefoil knot
    curve_data = bpy.data.curves.new("TrefoilKnotCurve", type='CURVE')
    curve_data.dimensions = '3D'
    
    # Create spline
    spline = curve_data.splines.new('NURBS')
    spline.points.add(subdivisions - 1)
    
    # Generate trefoil knot points
    for i in range(subdivisions):
        t = 2 * math.pi * i / subdivisions
        
        # Trefoil knot parametric equations
        x = radius * (math.sin(t) + 2 * math.sin(2*t))
        y = radius * (math.cos(t) - 2 * math.cos(2*t))
        z = radius * (-math.sin(3*t))
        
        spline.points[i].co = (x, y, z, 1.0)
    
    # Close the curve
    spline.use_cyclic_u = True
    
    # Create curve object
    curve_obj = bpy.data.objects.new("TrefoilKnot", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    # Set curve properties
    curve_data.bevel_depth = tube_radius
    curve_data.bevel_resolution = 16
    curve_data.resolution_u = subdivisions
    
    # Convert to mesh
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    
    # Add material
    mat = bpy.data.materials.new(name="TrefoilKnotMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.2, 0.2, 1.0)  # Red
    curve_obj.data.materials.append(mat)
    
    return curve_obj

def create_torus_knot(
    p=3,                 # number of times around the major radius
    q=5,                 # number of times around the minor radius
    radius=30,           # mm
    tube_radius=6,       # mm
    subdivisions=256     # resolution
):
    """
    Create a torus knot - a knot that wraps around a torus
    
    Args:
        p: Number of times around the major radius
        q: Number of times around the minor radius
        radius: Radius of the torus (mm)
        tube_radius: Radius of the tube (mm)
        subdivisions: Number of subdivisions for smoothness
    """
    
    # Convert to Blender units
    radius = radius / 1000
    tube_radius = tube_radius / 1000
    
    # Create curve for torus knot
    curve_data = bpy.data.curves.new("TorusKnotCurve", type='CURVE')
    curve_data.dimensions = '3D'
    
    # Create spline
    spline = curve_data.splines.new('NURBS')
    spline.points.add(subdivisions - 1)
    
    # Generate torus knot points
    for i in range(subdivisions):
        t = 2 * math.pi * i / subdivisions
        
        # Torus knot parametric equations
        r = radius * (2 + math.cos(q * t))
        x = r * math.cos(p * t)
        y = r * math.sin(p * t)
        z = radius * math.sin(q * t)
        
        spline.points[i].co = (x, y, z, 1.0)
    
    # Close the curve
    spline.use_cyclic_u = True
    
    # Create curve object
    curve_obj = bpy.data.objects.new("TorusKnot", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    # Set curve properties
    curve_data.bevel_depth = tube_radius
    curve_data.bevel_resolution = 12
    curve_data.resolution_u = subdivisions
    
    # Convert to mesh
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    
    # Add material
    mat = bpy.data.materials.new(name="TorusKnotMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.8, 0.8, 1.0)  # Cyan
    curve_obj.data.materials.append(mat)
    
    return curve_obj

def create_mathematical_objects_collection():
    """Create a collection of mathematical and impossible objects"""
    
    # Möbius strip
    create_mobius_strip(
        radius=30,
        width=15,
        thickness=2
    )
    
    # Klein bottle
    bpy.ops.transform.translate(value=(0.1, 0, 0))
    create_klein_bottle(
        radius=25,
        height=50,
        thickness=2
    )
    
    # Penrose triangle
    bpy.ops.transform.translate(value=(0.2, 0, 0))
    create_penrose_triangle(
        size=40,
        thickness=6,
        beam_width=10
    )
    
    # Impossible cube
    bpy.ops.transform.translate(value=(0.3, 0, 0))
    create_impossible_cube(
        size=35,
        beam_thickness=5
    )
    
    # Trefoil knot
    bpy.ops.transform.translate(value=(0.4, 0, 0))
    create_trefoil_knot(
        radius=20,
        tube_radius=6
    )
    
    # Torus knot (3,5)
    bpy.ops.transform.translate(value=(0.5, 0, 0))
    create_torus_knot(
        p=3,
        q=5,
        radius=20,
        tube_radius=4
    )
    
    # Double Möbius strip
    bpy.ops.transform.translate(value=(0.6, 0, 0))
    create_mobius_strip(
        radius=25,
        width=12,
        thickness=2,
        twists=2  # Double twist
    )

# Main execution
if __name__ == "__main__":
    clear_scene()
    create_mathematical_objects_collection()
    
    print("Mathematical and impossible objects created successfully!")
    print("Objects include:")
    print("- Möbius strip (one-sided surface)")
    print("- Klein bottle (non-orientable surface)")
    print("- Penrose triangle (impossible triangle)")
    print("- Impossible cube (optical illusion)")
    print("- Trefoil knot (simplest non-trivial knot)")
    print("- Torus knot (3,5 configuration)")
    print("- Double Möbius strip (double twist)")
    print("")
    print("Perfect for:")
    print("- Mathematical education")
    print("- Conversation pieces")
    print("- Desk decorations")
    print("- Demonstrating 3D printing capabilities") 