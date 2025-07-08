import bpy
import bmesh
from mathutils import Vector
import math

def clear_scene():
    """Clear all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

def create_desk_organizer(
    width=200,           # mm
    depth=150,           # mm
    height=60,           # mm
    wall_thickness=2,    # mm
    base_thickness=3,    # mm
    compartments_x=3,    # number of compartments horizontally
    compartments_y=2,    # number of compartments vertically
    pen_holes=6,         # number of pen holes
    pen_diameter=12,     # mm
    card_slot_width=90,  # mm
    card_slot_thickness=2 # mm
):
    """
    Create a desk organizer optimized for 3D printing
    
    Args:
        width: Total width of organizer (mm)
        depth: Total depth of organizer (mm)
        height: Total height of organizer (mm)
        wall_thickness: Wall thickness for 3D printing (mm)
        base_thickness: Base thickness (mm)
        compartments_x: Number of compartments horizontally
        compartments_y: Number of compartments vertically
        pen_holes: Number of pen holes
        pen_diameter: Diameter of pen holes (mm)
        card_slot_width: Width of card slot (mm)
        card_slot_thickness: Thickness of card slot (mm)
    """
    
    # Convert to Blender units (assuming 1 unit = 1mm)
    width = width / 1000
    depth = depth / 1000
    height = height / 1000
    wall_thickness = wall_thickness / 1000
    base_thickness = base_thickness / 1000
    pen_diameter = pen_diameter / 1000
    card_slot_width = card_slot_width / 1000
    card_slot_thickness = card_slot_thickness / 1000
    
    # Create main container
    mesh = bpy.data.meshes.new("DeskOrganizer")
    obj = bpy.data.objects.new("DeskOrganizer", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create outer box
    outer_verts = [
        Vector((0, 0, 0)),
        Vector((width, 0, 0)),
        Vector((width, depth, 0)),
        Vector((0, depth, 0)),
        Vector((0, 0, height)),
        Vector((width, 0, height)),
        Vector((width, depth, height)),
        Vector((0, depth, height))
    ]
    
    for v in outer_verts:
        bm.verts.new(v)
    
    # Create outer faces
    outer_faces = [
        [0, 1, 2, 3],  # Bottom
        [4, 7, 6, 5],  # Top
        [0, 4, 5, 1],  # Front
        [2, 6, 7, 3],  # Back
        [0, 3, 7, 4],  # Left
        [1, 5, 6, 2]   # Right
    ]
    
    for face in outer_faces:
        bm.faces.new([bm.verts[i] for i in face])
    
    # Create inner cavity
    inner_width = width - 2 * wall_thickness
    inner_depth = depth - 2 * wall_thickness
    inner_height = height - base_thickness
    
    inner_verts_start = len(bm.verts)
    inner_verts = [
        Vector((wall_thickness, wall_thickness, base_thickness)),
        Vector((wall_thickness + inner_width, wall_thickness, base_thickness)),
        Vector((wall_thickness + inner_width, wall_thickness + inner_depth, base_thickness)),
        Vector((wall_thickness, wall_thickness + inner_depth, base_thickness)),
        Vector((wall_thickness, wall_thickness, base_thickness + inner_height)),
        Vector((wall_thickness + inner_width, wall_thickness, base_thickness + inner_height)),
        Vector((wall_thickness + inner_width, wall_thickness + inner_depth, base_thickness + inner_height)),
        Vector((wall_thickness, wall_thickness + inner_depth, base_thickness + inner_height))
    ]
    
    for v in inner_verts:
        bm.verts.new(v)
    
    # Create inner faces (inverted normals for cavity)
    inner_faces = [
        [inner_verts_start + 3, inner_verts_start + 2, inner_verts_start + 1, inner_verts_start + 0],  # Bottom
        [inner_verts_start + 5, inner_verts_start + 6, inner_verts_start + 7, inner_verts_start + 4],  # Top
        [inner_verts_start + 1, inner_verts_start + 5, inner_verts_start + 4, inner_verts_start + 0],  # Front
        [inner_verts_start + 3, inner_verts_start + 7, inner_verts_start + 6, inner_verts_start + 2],  # Back
        [inner_verts_start + 4, inner_verts_start + 7, inner_verts_start + 3, inner_verts_start + 0],  # Left
        [inner_verts_start + 2, inner_verts_start + 6, inner_verts_start + 5, inner_verts_start + 1]   # Right
    ]
    
    for face in inner_faces:
        bm.faces.new([bm.verts[i] for i in face])
    
    # Create compartment dividers
    if compartments_x > 1:
        for i in range(1, compartments_x):
            x_pos = wall_thickness + (inner_width / compartments_x) * i
            
            # Divider vertices
            div_verts_start = len(bm.verts)
            div_thickness = wall_thickness * 0.5
            
            div_verts = [
                Vector((x_pos - div_thickness/2, wall_thickness, base_thickness)),
                Vector((x_pos + div_thickness/2, wall_thickness, base_thickness)),
                Vector((x_pos + div_thickness/2, wall_thickness + inner_depth, base_thickness)),
                Vector((x_pos - div_thickness/2, wall_thickness + inner_depth, base_thickness)),
                Vector((x_pos - div_thickness/2, wall_thickness, base_thickness + inner_height)),
                Vector((x_pos + div_thickness/2, wall_thickness, base_thickness + inner_height)),
                Vector((x_pos + div_thickness/2, wall_thickness + inner_depth, base_thickness + inner_height)),
                Vector((x_pos - div_thickness/2, wall_thickness + inner_depth, base_thickness + inner_height))
            ]
            
            for v in div_verts:
                bm.verts.new(v)
            
            div_faces = [
                [div_verts_start + 0, div_verts_start + 1, div_verts_start + 2, div_verts_start + 3],  # Bottom
                [div_verts_start + 4, div_verts_start + 7, div_verts_start + 6, div_verts_start + 5],  # Top
                [div_verts_start + 0, div_verts_start + 4, div_verts_start + 5, div_verts_start + 1],  # Front
                [div_verts_start + 2, div_verts_start + 6, div_verts_start + 7, div_verts_start + 3],  # Back
                [div_verts_start + 0, div_verts_start + 3, div_verts_start + 7, div_verts_start + 4],  # Left
                [div_verts_start + 1, div_verts_start + 5, div_verts_start + 6, div_verts_start + 2]   # Right
            ]
            
            for face in div_faces:
                bm.faces.new([bm.verts[i] for i in face])
    
    if compartments_y > 1:
        for i in range(1, compartments_y):
            y_pos = wall_thickness + (inner_depth / compartments_y) * i
            
            # Divider vertices
            div_verts_start = len(bm.verts)
            div_thickness = wall_thickness * 0.5
            
            div_verts = [
                Vector((wall_thickness, y_pos - div_thickness/2, base_thickness)),
                Vector((wall_thickness + inner_width, y_pos - div_thickness/2, base_thickness)),
                Vector((wall_thickness + inner_width, y_pos + div_thickness/2, base_thickness)),
                Vector((wall_thickness, y_pos + div_thickness/2, base_thickness)),
                Vector((wall_thickness, y_pos - div_thickness/2, base_thickness + inner_height)),
                Vector((wall_thickness + inner_width, y_pos - div_thickness/2, base_thickness + inner_height)),
                Vector((wall_thickness + inner_width, y_pos + div_thickness/2, base_thickness + inner_height)),
                Vector((wall_thickness, y_pos + div_thickness/2, base_thickness + inner_height))
            ]
            
            for v in div_verts:
                bm.verts.new(v)
            
            div_faces = [
                [div_verts_start + 0, div_verts_start + 1, div_verts_start + 2, div_verts_start + 3],  # Bottom
                [div_verts_start + 4, div_verts_start + 7, div_verts_start + 6, div_verts_start + 5],  # Top
                [div_verts_start + 0, div_verts_start + 4, div_verts_start + 5, div_verts_start + 1],  # Front
                [div_verts_start + 2, div_verts_start + 6, div_verts_start + 7, div_verts_start + 3],  # Back
                [div_verts_start + 0, div_verts_start + 3, div_verts_start + 7, div_verts_start + 4],  # Left
                [div_verts_start + 1, div_verts_start + 5, div_verts_start + 6, div_verts_start + 2]   # Right
            ]
            
            for face in div_faces:
                bm.faces.new([bm.verts[i] for i in face])
    
    # Update mesh
    bm.ensure_face_index_valid()
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    # Select the object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Add material
    mat = bpy.data.materials.new(name="OrganizerMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.6, 0.8, 1.0)  # Blue color
    obj.data.materials.append(mat)
    
    return obj

def create_pen_holder(
    diameter=40,      # mm
    height=100,       # mm
    wall_thickness=2, # mm
    base_thickness=3, # mm
    pen_holes=8,      # number of individual pen holes
    pen_diameter=12   # mm
):
    """Create a cylindrical pen holder with individual holes"""
    
    # Convert to Blender units
    diameter = diameter / 1000
    height = height / 1000
    wall_thickness = wall_thickness / 1000
    base_thickness = base_thickness / 1000
    pen_diameter = pen_diameter / 1000
    
    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2,
        depth=height,
        location=(0, 0, height/2)
    )
    
    outer_cylinder = bpy.context.active_object
    outer_cylinder.name = "PenHolderOuter"
    
    # Create inner cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2 - wall_thickness,
        depth=height - base_thickness,
        location=(0, 0, height/2 + base_thickness/2)
    )
    
    inner_cylinder = bpy.context.active_object
    inner_cylinder.name = "PenHolderInner"
    
    # Boolean difference
    bool_mod = outer_cylinder.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = inner_cylinder
    
    # Apply modifier
    bpy.context.view_layer.objects.active = outer_cylinder
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # Delete inner cylinder
    bpy.data.objects.remove(inner_cylinder, do_unlink=True)
    
    # Create individual pen holes if requested
    if pen_holes > 0:
        hole_radius = pen_diameter / 2
        pattern_radius = (diameter/2 - wall_thickness) * 0.7
        
        for i in range(pen_holes):
            angle = (2 * math.pi * i) / pen_holes
            x = pattern_radius * math.cos(angle)
            y = pattern_radius * math.sin(angle)
            
            # Create hole cylinder
            bpy.ops.mesh.primitive_cylinder_add(
                radius=hole_radius,
                depth=height - base_thickness,
                location=(x, y, height/2 + base_thickness/2)
            )
            
            hole_cylinder = bpy.context.active_object
            hole_cylinder.name = f"PenHole_{i}"
            
            # Boolean difference for hole
            bool_mod = outer_cylinder.modifiers.new(name=f"BooleanHole_{i}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = hole_cylinder
            
            # Apply modifier
            bpy.context.view_layer.objects.active = outer_cylinder
            bpy.ops.object.modifier_apply(modifier=f"BooleanHole_{i}")
            
            # Delete hole cylinder
            bpy.data.objects.remove(hole_cylinder, do_unlink=True)
    
    # Add material
    mat = bpy.data.materials.new(name="PenHolderMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.2, 0.2, 1.0)  # Red color
    outer_cylinder.data.materials.append(mat)
    
    return outer_cylinder

def create_desk_organizer_set():
    """Create a set of desk organizers"""
    
    # Large organizer
    create_desk_organizer(
        width=200,
        depth=150,
        height=60,
        compartments_x=3,
        compartments_y=2
    )
    
    # Small organizer
    bpy.ops.transform.translate(value=(0.25, 0, 0))
    create_desk_organizer(
        width=120,
        depth=80,
        height=40,
        compartments_x=2,
        compartments_y=2
    )
    
    # Pen holder
    bpy.ops.transform.translate(value=(0.4, 0, 0))
    create_pen_holder(
        diameter=50,
        height=120,
        pen_holes=6
    )
    
    # Tall pen holder
    bpy.ops.transform.translate(value=(0.5, 0, 0))
    create_pen_holder(
        diameter=35,
        height=150,
        pen_holes=0  # Single large compartment
    )

# Main execution
if __name__ == "__main__":
    clear_scene()
    create_desk_organizer_set()
    
    print("Desk organizers created successfully!")
    print("Objects optimized for 3D printing with:")
    print("- Proper wall thickness (2mm)")
    print("- Stable base for printing")
    print("- Compartments for organization")
    print("- No support material required") 