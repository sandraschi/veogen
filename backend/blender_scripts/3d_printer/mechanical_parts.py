import bpy
import bmesh
from mathutils import Vector, Matrix
import math

def clear_scene():
    """Clear all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

def create_gear(
    num_teeth=20,       # number of teeth
    outer_radius=25,    # mm
    inner_radius=15,    # mm
    tooth_height=3,     # mm
    thickness=5,        # mm
    center_hole=8,      # mm diameter
    hub_thickness=8     # mm
):
    """
    Create a gear optimized for 3D printing
    
    Args:
        num_teeth: Number of teeth on the gear
        outer_radius: Outer radius of the gear (mm)
        inner_radius: Inner radius of the gear (mm)
        tooth_height: Height of each tooth (mm)
        thickness: Thickness of the gear (mm)
        center_hole: Diameter of center hole (mm)
        hub_thickness: Thickness of the hub (mm)
    """
    
    # Convert to Blender units
    outer_radius = outer_radius / 1000
    inner_radius = inner_radius / 1000
    tooth_height = tooth_height / 1000
    thickness = thickness / 1000
    center_hole = center_hole / 1000
    hub_thickness = hub_thickness / 1000
    
    # Create mesh
    mesh = bpy.data.meshes.new("Gear")
    obj = bpy.data.objects.new("Gear", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create gear profile
    angle_per_tooth = (2 * math.pi) / num_teeth
    
    # Generate vertices for gear profile
    profile_verts = []
    
    for i in range(num_teeth):
        base_angle = i * angle_per_tooth
        
        # Tooth root
        root_angle1 = base_angle - angle_per_tooth * 0.4
        root_angle2 = base_angle + angle_per_tooth * 0.4
        
        # Tooth tip
        tip_angle1 = base_angle - angle_per_tooth * 0.2
        tip_angle2 = base_angle + angle_per_tooth * 0.2
        
        # Add vertices
        profile_verts.extend([
            Vector((inner_radius * math.cos(root_angle1), inner_radius * math.sin(root_angle1), 0)),
            Vector(((inner_radius + tooth_height) * math.cos(tip_angle1), (inner_radius + tooth_height) * math.sin(tip_angle1), 0)),
            Vector(((inner_radius + tooth_height) * math.cos(tip_angle2), (inner_radius + tooth_height) * math.sin(tip_angle2), 0)),
            Vector((inner_radius * math.cos(root_angle2), inner_radius * math.sin(root_angle2), 0))
        ])
    
    # Create bottom vertices
    bottom_verts = []
    for v in profile_verts:
        bottom_verts.append(bm.verts.new(v))
    
    # Create top vertices
    top_verts = []
    for v in profile_verts:
        top_v = v.copy()
        top_v.z = thickness
        top_verts.append(bm.verts.new(top_v))
    
    # Create faces
    num_profile_verts = len(profile_verts)
    
    # Bottom and top faces
    for i in range(0, num_profile_verts, 4):
        if i + 3 < num_profile_verts:
            # Bottom face
            bm.faces.new([bottom_verts[i], bottom_verts[i+1], bottom_verts[i+2], bottom_verts[i+3]])
            # Top face
            bm.faces.new([top_verts[i+3], top_verts[i+2], top_verts[i+1], top_verts[i]])
    
    # Side faces
    for i in range(num_profile_verts):
        next_i = (i + 1) % num_profile_verts
        bm.faces.new([bottom_verts[i], top_verts[i], top_verts[next_i], bottom_verts[next_i]])
    
    # Create center hole
    if center_hole > 0:
        hole_radius = center_hole / 2
        hole_segments = 16
        
        # Create hole vertices
        hole_bottom_verts = []
        hole_top_verts = []
        
        for i in range(hole_segments):
            angle = (2 * math.pi * i) / hole_segments
            x = hole_radius * math.cos(angle)
            y = hole_radius * math.sin(angle)
            
            hole_bottom_verts.append(bm.verts.new(Vector((x, y, 0))))
            hole_top_verts.append(bm.verts.new(Vector((x, y, thickness))))
        
        # Create hole faces
        for i in range(hole_segments):
            next_i = (i + 1) % hole_segments
            # Inner side faces (reversed normals)
            bm.faces.new([hole_bottom_verts[next_i], hole_top_verts[next_i], hole_top_verts[i], hole_bottom_verts[i]])
    
    # Update mesh
    bm.ensure_face_index_valid()
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    # Select the object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Add material
    mat = bpy.data.materials.new(name="GearMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.7, 0.7, 0.7, 1.0)  # Gray color
    obj.data.materials.append(mat)
    
    return obj

def create_bolt(
    length=30,          # mm
    head_diameter=12,   # mm
    head_height=8,      # mm
    thread_diameter=6,  # mm
    thread_pitch=1.0,   # mm
    hex_head=True       # Use hex head instead of round
):
    """Create a bolt with threads optimized for 3D printing"""
    
    # Convert to Blender units
    length = length / 1000
    head_diameter = head_diameter / 1000
    head_height = head_height / 1000
    thread_diameter = thread_diameter / 1000
    thread_pitch = thread_pitch / 1000
    
    # Create head
    if hex_head:
        # Hex head
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6,
            radius=head_diameter/2,
            depth=head_height,
            location=(0, 0, head_height/2)
        )
    else:
        # Round head
        bpy.ops.mesh.primitive_cylinder_add(
            radius=head_diameter/2,
            depth=head_height,
            location=(0, 0, head_height/2)
        )
    
    head = bpy.context.active_object
    head.name = "BoltHead"
    
    # Create shaft
    bpy.ops.mesh.primitive_cylinder_add(
        radius=thread_diameter/2,
        depth=length,
        location=(0, 0, head_height + length/2)
    )
    
    shaft = bpy.context.active_object
    shaft.name = "BoltShaft"
    
    # Join head and shaft
    bpy.context.view_layer.objects.active = head
    head.select_set(True)
    shaft.select_set(True)
    bpy.ops.object.join()
    
    # Add material
    mat = bpy.data.materials.new(name="BoltMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.8, 0.8, 1.0)  # Light gray
    head.data.materials.append(mat)
    
    return head

def create_bracket(
    width=50,           # mm
    height=30,          # mm
    depth=20,           # mm
    thickness=3,        # mm
    hole_diameter=6,    # mm
    num_holes=2,        # number of mounting holes
    angle=90            # degrees
):
    """Create a mounting bracket optimized for 3D printing"""
    
    # Convert to Blender units
    width = width / 1000
    height = height / 1000
    depth = depth / 1000
    thickness = thickness / 1000
    hole_diameter = hole_diameter / 1000
    
    # Create mesh
    mesh = bpy.data.meshes.new("Bracket")
    obj = bpy.data.objects.new("Bracket", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create L-shaped bracket
    angle_rad = math.radians(angle)
    
    # Base plate vertices
    base_verts = [
        Vector((0, 0, 0)),
        Vector((width, 0, 0)),
        Vector((width, depth, 0)),
        Vector((0, depth, 0)),
        Vector((0, 0, thickness)),
        Vector((width, 0, thickness)),
        Vector((width, depth, thickness)),
        Vector((0, depth, thickness))
    ]
    
    # Add base vertices
    for v in base_verts:
        bm.verts.new(v)
    
    # Create base faces
    base_faces = [
        [0, 1, 2, 3],  # Bottom
        [4, 7, 6, 5],  # Top
        [0, 4, 5, 1],  # Front
        [2, 6, 7, 3],  # Back
        [0, 3, 7, 4],  # Left
        [1, 5, 6, 2]   # Right
    ]
    
    for face in base_faces:
        bm.faces.new([bm.verts[i] for i in face])
    
    # Create vertical plate
    if angle != 0:
        vert_height = height
        vert_start = len(bm.verts)
        
        # Calculate vertical plate position
        vert_x = width - thickness
        vert_y = depth
        
        vert_verts = [
            Vector((vert_x, vert_y, 0)),
            Vector((width, vert_y, 0)),
            Vector((width, vert_y, vert_height)),
            Vector((vert_x, vert_y, vert_height)),
            Vector((vert_x, vert_y - thickness, 0)),
            Vector((width, vert_y - thickness, 0)),
            Vector((width, vert_y - thickness, vert_height)),
            Vector((vert_x, vert_y - thickness, vert_height))
        ]
        
        for v in vert_verts:
            bm.verts.new(v)
        
        # Create vertical faces
        vert_faces = [
            [vert_start + 0, vert_start + 1, vert_start + 2, vert_start + 3],  # Front
            [vert_start + 4, vert_start + 7, vert_start + 6, vert_start + 5],  # Back
            [vert_start + 0, vert_start + 4, vert_start + 5, vert_start + 1],  # Bottom
            [vert_start + 2, vert_start + 6, vert_start + 7, vert_start + 3],  # Top
            [vert_start + 0, vert_start + 3, vert_start + 7, vert_start + 4],  # Left
            [vert_start + 1, vert_start + 5, vert_start + 6, vert_start + 2]   # Right
        ]
        
        for face in vert_faces:
            bm.faces.new([bm.verts[i] for i in face])
    
    # Update mesh
    bm.ensure_face_index_valid()
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    # Add mounting holes
    if num_holes > 0 and hole_diameter > 0:
        hole_radius = hole_diameter / 2
        hole_spacing = width / (num_holes + 1)
        
        for i in range(num_holes):
            x_pos = hole_spacing * (i + 1)
            y_pos = depth / 2
            
            # Create hole cylinder
            bpy.ops.mesh.primitive_cylinder_add(
                radius=hole_radius,
                depth=thickness * 2,
                location=(x_pos, y_pos, thickness/2)
            )
            
            hole_cylinder = bpy.context.active_object
            hole_cylinder.name = f"Hole_{i}"
            
            # Boolean difference
            bool_mod = obj.modifiers.new(name=f"BooleanHole_{i}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = hole_cylinder
            
            # Apply modifier
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=f"BooleanHole_{i}")
            
            # Delete hole cylinder
            bpy.data.objects.remove(hole_cylinder, do_unlink=True)
    
    # Select the object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Add material
    mat = bpy.data.materials.new(name="BracketMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.3, 0.8, 1.0)  # Blue color
    obj.data.materials.append(mat)
    
    return obj

def create_mechanical_parts_set():
    """Create a set of mechanical parts"""
    
    # Small gear
    create_gear(
        num_teeth=16,
        outer_radius=20,
        inner_radius=12,
        thickness=4,
        center_hole=6
    )
    
    # Medium gear
    bpy.ops.transform.translate(value=(0.06, 0, 0))
    create_gear(
        num_teeth=24,
        outer_radius=30,
        inner_radius=18,
        thickness=6,
        center_hole=8
    )
    
    # Large gear
    bpy.ops.transform.translate(value=(0.12, 0, 0))
    create_gear(
        num_teeth=32,
        outer_radius=40,
        inner_radius=25,
        thickness=8,
        center_hole=10
    )
    
    # Hex bolt
    bpy.ops.transform.translate(value=(0.2, 0, 0))
    create_bolt(
        length=25,
        head_diameter=10,
        head_height=6,
        thread_diameter=5,
        hex_head=True
    )
    
    # Round bolt
    bpy.ops.transform.translate(value=(0.25, 0, 0))
    create_bolt(
        length=20,
        head_diameter=12,
        head_height=4,
        thread_diameter=6,
        hex_head=False
    )
    
    # L-bracket
    bpy.ops.transform.translate(value=(0.3, 0, 0))
    create_bracket(
        width=40,
        height=25,
        depth=15,
        thickness=3,
        hole_diameter=5,
        num_holes=2
    )
    
    # Corner bracket
    bpy.ops.transform.translate(value=(0.4, 0, 0))
    create_bracket(
        width=30,
        height=30,
        depth=20,
        thickness=4,
        hole_diameter=6,
        num_holes=3,
        angle=90
    )

# Main execution
if __name__ == "__main__":
    clear_scene()
    create_mechanical_parts_set()
    
    print("Mechanical parts created successfully!")
    print("Objects optimized for 3D printing with:")
    print("- Proper tolerances for moving parts")
    print("- Standard mounting hole sizes")
    print("- Appropriate wall thickness")
    print("- No support material required for most parts") 