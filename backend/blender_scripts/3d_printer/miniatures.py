import bpy
import bmesh
from mathutils import Vector
import math
import random

def clear_scene():
    """Clear all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

def create_simple_figurine(
    height=50,           # mm
    head_size=8,         # mm
    body_width=12,       # mm
    body_height=20,      # mm
    arm_length=15,       # mm
    leg_length=20,       # mm
    base_diameter=20,    # mm
    base_height=3        # mm
):
    """
    Create a simple figurine optimized for 3D printing
    
    Args:
        height: Total height of figurine (mm)
        head_size: Diameter of head (mm)
        body_width: Width of body (mm)
        body_height: Height of body (mm)
        arm_length: Length of arms (mm)
        leg_length: Length of legs (mm)
        base_diameter: Diameter of base (mm)
        base_height: Height of base (mm)
    """
    
    # Convert to Blender units
    height = height / 1000
    head_size = head_size / 1000
    body_width = body_width / 1000
    body_height = body_height / 1000
    arm_length = arm_length / 1000
    leg_length = leg_length / 1000
    base_diameter = base_diameter / 1000
    base_height = base_height / 1000
    
    # Create base
    bpy.ops.mesh.primitive_cylinder_add(
        radius=base_diameter/2,
        depth=base_height,
        location=(0, 0, base_height/2)
    )
    
    base = bpy.context.active_object
    base.name = "FigurineBase"
    
    # Create legs
    leg_width = body_width * 0.3
    leg_separation = body_width * 0.6
    
    # Left leg
    bpy.ops.mesh.primitive_cylinder_add(
        radius=leg_width/2,
        depth=leg_length,
        location=(-leg_separation/2, 0, base_height + leg_length/2)
    )
    
    left_leg = bpy.context.active_object
    left_leg.name = "LeftLeg"
    
    # Right leg
    bpy.ops.mesh.primitive_cylinder_add(
        radius=leg_width/2,
        depth=leg_length,
        location=(leg_separation/2, 0, base_height + leg_length/2)
    )
    
    right_leg = bpy.context.active_object
    right_leg.name = "RightLeg"
    
    # Create body
    body_z = base_height + leg_length + body_height/2
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=body_width/2,
        depth=body_height,
        location=(0, 0, body_z)
    )
    
    body = bpy.context.active_object
    body.name = "FigurineBody"
    
    # Create arms
    arm_width = body_width * 0.25
    arm_z = body_z + body_height * 0.3
    arm_separation = body_width * 0.9
    
    # Left arm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=arm_width/2,
        depth=arm_length,
        rotation=(0, math.pi/2, 0),
        location=(-arm_separation/2, 0, arm_z)
    )
    
    left_arm = bpy.context.active_object
    left_arm.name = "LeftArm"
    
    # Right arm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=arm_width/2,
        depth=arm_length,
        rotation=(0, math.pi/2, 0),
        location=(arm_separation/2, 0, arm_z)
    )
    
    right_arm = bpy.context.active_object
    right_arm.name = "RightArm"
    
    # Create head
    head_z = body_z + body_height/2 + head_size/2
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=head_size/2,
        location=(0, 0, head_z)
    )
    
    head = bpy.context.active_object
    head.name = "FigurineHead"
    
    # Join all parts
    bpy.context.view_layer.objects.active = base
    objects_to_join = [base, left_leg, right_leg, body, left_arm, right_arm, head]
    
    for obj in objects_to_join:
        obj.select_set(True)
    
    bpy.ops.object.join()
    
    # Add material
    mat = bpy.data.materials.new(name="FigurineMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.6, 0.4, 1.0)  # Skin tone
    base.data.materials.append(mat)
    
    return base

def create_decorative_vase(
    height=60,           # mm
    bottom_diameter=25,  # mm
    top_diameter=35,     # mm
    wall_thickness=2,    # mm
    base_thickness=3,    # mm
    pattern="smooth"     # "smooth", "ribbed", "textured"
):
    """Create a decorative vase optimized for 3D printing"""
    
    # Convert to Blender units
    height = height / 1000
    bottom_radius = bottom_diameter / 2000
    top_radius = top_diameter / 2000
    wall_thickness = wall_thickness / 1000
    base_thickness = base_thickness / 1000
    
    # Create outer shape using bezier curve
    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
    curve = bpy.context.active_object
    curve.name = "VaseProfile"
    
    # Modify curve points to create vase profile
    curve.data.splines[0].bezier_points[0].co = (0, 0, 0)
    curve.data.splines[0].bezier_points[1].co = (bottom_radius, 0, height/3)
    
    # Add more points for vase shape
    curve.data.splines[0].bezier_points.add(2)
    curve.data.splines[0].bezier_points[2].co = (top_radius, 0, height*2/3)
    curve.data.splines[0].bezier_points[3].co = (top_radius * 0.9, 0, height)
    
    # Convert curve to mesh and rotate
    bpy.ops.object.convert(target='MESH')
    
    # Add screw modifier for rotation
    screw_mod = curve.modifiers.new(name="Screw", type='SCREW')
    screw_mod.axis = 'Z'
    screw_mod.angle = math.pi * 2
    screw_mod.steps = 32
    screw_mod.render_steps = 32
    
    # Apply modifier
    bpy.ops.object.modifier_apply(modifier="Screw")
    
    # Create inner cavity
    bpy.ops.mesh.primitive_cylinder_add(
        radius=bottom_radius - wall_thickness,
        depth=height - base_thickness,
        location=(0, 0, height/2 + base_thickness/2)
    )
    
    inner_cavity = bpy.context.active_object
    inner_cavity.name = "VaseCavity"
    
    # Scale top to match vase profile
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(top_radius/bottom_radius, top_radius/bottom_radius, 1))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Boolean difference
    bool_mod = curve.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = inner_cavity
    
    # Apply modifier
    bpy.context.view_layer.objects.active = curve
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # Delete cavity
    bpy.data.objects.remove(inner_cavity, do_unlink=True)
    
    # Add pattern if requested
    if pattern == "ribbed":
        # Add array modifier for ribs
        array_mod = curve.modifiers.new(name="ArrayRibs", type='ARRAY')
        array_mod.fit_type = 'FIXED_COUNT'
        array_mod.count = 12
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace[2] = height / 12
        
        # Add wave modifier for ribbing effect
        wave_mod = curve.modifiers.new(name="Wave", type='WAVE')
        wave_mod.use_z = False
        wave_mod.use_x = True
        wave_mod.height = 0.002
        wave_mod.width = 0.5
        wave_mod.speed = 0
    
    # Add material
    mat = bpy.data.materials.new(name="VaseMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.5, 0.8, 1.0)  # Blue ceramic
    curve.data.materials.append(mat)
    
    return curve

def create_chess_piece(
    piece_type="pawn",   # "pawn", "rook", "knight", "bishop", "queen", "king"
    height=40,           # mm
    base_diameter=20,    # mm
    color="white"        # "white" or "black"
):
    """Create a chess piece optimized for 3D printing"""
    
    # Convert to Blender units
    height = height / 1000
    base_radius = base_diameter / 2000
    
    # Create base
    bpy.ops.mesh.primitive_cylinder_add(
        radius=base_radius,
        depth=height * 0.1,
        location=(0, 0, height * 0.05)
    )
    
    base = bpy.context.active_object
    base.name = f"ChessPiece_{piece_type}_Base"
    
    # Create piece body based on type
    if piece_type == "pawn":
        # Simple pawn shape
        bpy.ops.mesh.primitive_cylinder_add(
            radius=base_radius * 0.6,
            depth=height * 0.6,
            location=(0, 0, height * 0.4)
        )
        
        body = bpy.context.active_object
        body.name = "PawnBody"
        
        # Add head
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=base_radius * 0.4,
            location=(0, 0, height * 0.8)
        )
        
        head = bpy.context.active_object
        head.name = "PawnHead"
        
        # Join parts
        bpy.context.view_layer.objects.active = base
        base.select_set(True)
        body.select_set(True)
        head.select_set(True)
        bpy.ops.object.join()
        
    elif piece_type == "rook":
        # Castle-like rook
        bpy.ops.mesh.primitive_cylinder_add(
            radius=base_radius * 0.8,
            depth=height * 0.8,
            location=(0, 0, height * 0.5)
        )
        
        body = bpy.context.active_object
        body.name = "RookBody"
        
        # Add crenellations
        for i in range(4):
            angle = i * math.pi / 2
            x = base_radius * 0.6 * math.cos(angle)
            y = base_radius * 0.6 * math.sin(angle)
            
            bpy.ops.mesh.primitive_cube_add(
                size=base_radius * 0.3,
                location=(x, y, height * 0.95)
            )
            
            crenellation = bpy.context.active_object
            crenellation.name = f"Crenellation_{i}"
            
            # Join to body
            bpy.context.view_layer.objects.active = body
            body.select_set(True)
            crenellation.select_set(True)
            bpy.ops.object.join()
        
        # Join base and body
        bpy.context.view_layer.objects.active = base
        base.select_set(True)
        body.select_set(True)
        bpy.ops.object.join()
        
    elif piece_type == "bishop":
        # Bishop with pointed top
        bpy.ops.mesh.primitive_cylinder_add(
            radius=base_radius * 0.7,
            depth=height * 0.7,
            location=(0, 0, height * 0.45)
        )
        
        body = bpy.context.active_object
        body.name = "BishopBody"
        
        # Add pointed top
        bpy.ops.mesh.primitive_cone_add(
            radius1=base_radius * 0.4,
            radius2=0,
            depth=height * 0.3,
            location=(0, 0, height * 0.85)
        )
        
        top = bpy.context.active_object
        top.name = "BishopTop"
        
        # Join parts
        bpy.context.view_layer.objects.active = base
        base.select_set(True)
        body.select_set(True)
        top.select_set(True)
        bpy.ops.object.join()
    
    # Add material based on color
    if color == "white":
        mat = bpy.data.materials.new(name="WhiteChessMaterial")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
    else:
        mat = bpy.data.materials.new(name="BlackChessMaterial")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.1, 0.1, 1.0)
    
    base.data.materials.append(mat)
    
    return base

def create_keychain_tag(
    width=30,            # mm
    height=20,           # mm
    thickness=3,         # mm
    hole_diameter=4,     # mm
    text="VeoGen",       # text to emboss
    text_depth=0.5       # mm
):
    """Create a keychain tag with embossed text"""
    
    # Convert to Blender units
    width = width / 1000
    height = height / 1000
    thickness = thickness / 1000
    hole_diameter = hole_diameter / 1000
    text_depth = text_depth / 1000
    
    # Create base shape
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(0, 0, thickness/2)
    )
    
    tag = bpy.context.active_object
    tag.name = "KeychainTag"
    tag.scale = (width/2, height/2, thickness/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Create keychain hole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=hole_diameter/2,
        depth=thickness * 2,
        location=(0, height/2 - hole_diameter, thickness/2)
    )
    
    hole = bpy.context.active_object
    hole.name = "KeychainHole"
    
    # Boolean difference for hole
    bool_mod = tag.modifiers.new(name="BooleanHole", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = hole
    
    # Apply modifier
    bpy.context.view_layer.objects.active = tag
    bpy.ops.object.modifier_apply(modifier="BooleanHole")
    
    # Delete hole
    bpy.data.objects.remove(hole, do_unlink=True)
    
    # Add text (simplified - in real use, would use text objects)
    # For now, create a simple embossed rectangle
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(0, -height/4, thickness/2 + text_depth/2)
    )
    
    text_emboss = bpy.context.active_object
    text_emboss.name = "TextEmboss"
    text_emboss.scale = (width * 0.6 / 2, height * 0.3 / 2, text_depth/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Boolean union for embossed text
    bool_mod = tag.modifiers.new(name="BooleanText", type='BOOLEAN')
    bool_mod.operation = 'UNION'
    bool_mod.object = text_emboss
    
    # Apply modifier
    bpy.context.view_layer.objects.active = tag
    bpy.ops.object.modifier_apply(modifier="BooleanText")
    
    # Delete text object
    bpy.data.objects.remove(text_emboss, do_unlink=True)
    
    # Add material
    mat = bpy.data.materials.new(name="KeychainMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.2, 0.2, 1.0)  # Red
    tag.data.materials.append(mat)
    
    return tag

def create_miniatures_collection():
    """Create a collection of miniatures and decorative objects"""
    
    # Simple figurine
    create_simple_figurine(
        height=40,
        head_size=6,
        base_diameter=15
    )
    
    # Decorative vase
    bpy.ops.transform.translate(value=(0.08, 0, 0))
    create_decorative_vase(
        height=50,
        bottom_diameter=20,
        top_diameter=25,
        pattern="smooth"
    )
    
    # Chess pawn (white)
    bpy.ops.transform.translate(value=(0.16, 0, 0))
    create_chess_piece(
        piece_type="pawn",
        height=35,
        base_diameter=18,
        color="white"
    )
    
    # Chess rook (black)
    bpy.ops.transform.translate(value=(0.24, 0, 0))
    create_chess_piece(
        piece_type="rook",
        height=40,
        base_diameter=20,
        color="black"
    )
    
    # Chess bishop (white)
    bpy.ops.transform.translate(value=(0.32, 0, 0))
    create_chess_piece(
        piece_type="bishop",
        height=45,
        base_diameter=20,
        color="white"
    )
    
    # Keychain tag
    bpy.ops.transform.translate(value=(0.4, 0, 0))
    create_keychain_tag(
        width=25,
        height=15,
        thickness=2,
        text="VeoGen"
    )
    
    # Larger figurine
    bpy.ops.transform.translate(value=(0.48, 0, 0))
    create_simple_figurine(
        height=60,
        head_size=10,
        body_width=15,
        base_diameter=25
    )

# Main execution
if __name__ == "__main__":
    clear_scene()
    create_miniatures_collection()
    
    print("Miniatures and decorative objects created successfully!")
    print("Objects optimized for 3D printing with:")
    print("- Appropriate detail level for miniature printing")
    print("- Stable bases for support-free printing")
    print("- Proper wall thickness for small objects")
    print("- Clean geometry suitable for resin or FDM printing")
    print("- Collectible and decorative purposes") 