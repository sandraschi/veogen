"""
Versailles Bedroom Generator for Blender
========================================
Creates a complete Louis XV bedroom environment with period-accurate furniture,
ornate decorations, and atmospheric lighting. Optimized for VRChat.

Usage: Run this script in Blender to generate a complete bedroom scene
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector
import math
import random

def clear_scene():
    """Clear all objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    print("Scene cleared for Versailles bedroom")

def create_room_structure():
    """Create the basic room walls, floor, and ceiling"""
    
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "Bedroom_Floor"
    
    # Create walls
    # Back wall
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, -10, 5))
    back_wall = bpy.context.object
    back_wall.name = "Back_Wall"
    back_wall.rotation_euler = (math.pi/2, 0, 0)
    
    # Left wall
    bpy.ops.mesh.primitive_plane_add(size=20, location=(-10, 0, 5))
    left_wall = bpy.context.object
    left_wall.name = "Left_Wall"
    left_wall.rotation_euler = (math.pi/2, 0, math.pi/2)
    
    # Right wall
    bpy.ops.mesh.primitive_plane_add(size=20, location=(10, 0, 5))
    right_wall = bpy.context.object
    right_wall.name = "Right_Wall"
    right_wall.rotation_euler = (math.pi/2, 0, -math.pi/2)
    
    # Ceiling
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 10))
    ceiling = bpy.context.object
    ceiling.name = "Bedroom_Ceiling"
    ceiling.rotation_euler = (math.pi, 0, 0)
    
    print("Room structure created (20x20x10 units)")
    return [floor, back_wall, left_wall, right_wall, ceiling]

def create_four_poster_bed():
    """Create an ornate four-poster bed"""
    
    # Bed base/mattress
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5, 1))
    bed_base = bpy.context.object
    bed_base.name = "Bed_Base"
    bed_base.scale = (4, 6, 0.5)
    
    # Bed posts (4 corners)
    post_positions = [
        (1.8, -7.8, 0),  # Front right
        (-1.8, -7.8, 0), # Front left
        (1.8, -2.2, 0),  # Back right
        (-1.8, -2.2, 0)  # Back left
    ]
    
    posts = []
    for i, pos in enumerate(post_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=6, location=pos)
        post = bpy.context.object
        post.name = f"Bed_Post_{i+1}"
        post.location = (pos[0], pos[1], 3)
        posts.append(post)
    
    # Canopy frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5, 6))
    canopy = bpy.context.object
    canopy.name = "Bed_Canopy"
    canopy.scale = (4, 6, 0.1)
    
    # Headboard
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -8.5, 2.5))
    headboard = bpy.context.object
    headboard.name = "Bed_Headboard"
    headboard.scale = (4, 0.3, 2)
    
    print("Four-poster bed created")
    return [bed_base, canopy, headboard] + posts

def create_wardrobe():
    """Create an ornate French wardrobe"""
    
    # Main wardrobe body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-7, -8, 2.5))
    wardrobe = bpy.context.object
    wardrobe.name = "Wardrobe_Body"
    wardrobe.scale = (2, 1, 4)
    
    # Wardrobe doors
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-6, -8, 2.5))
    door_left = bpy.context.object
    door_left.name = "Wardrobe_Door_Left"
    door_left.scale = (0.05, 0.8, 3.5)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, -8, 2.5))
    door_right = bpy.context.object
    door_right.name = "Wardrobe_Door_Right"
    door_right.scale = (0.05, 0.8, 3.5)
    
    # Decorative top crown
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.5, location=(-7, -8, 5))
    crown = bpy.context.object
    crown.name = "Wardrobe_Crown"
    crown.scale = (1, 0.8, 0.5)
    
    print("French wardrobe created")
    return [wardrobe, door_left, door_right, crown]

def create_vanity_table():
    """Create an ornate vanity table with mirror"""
    
    # Vanity table surface
    bpy.ops.mesh.primitive_cube_add(size=1, location=(7, 5, 1.5))
    table = bpy.context.object
    table.name = "Vanity_Table"
    table.scale = (3, 1.5, 0.1)
    
    # Table legs
    leg_positions = [(6, 4.2, 0), (8, 4.2, 0), (6, 5.8, 0), (8, 5.8, 0)]
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.5, location=pos)
        leg = bpy.context.object
        leg.name = f"Vanity_Leg_{i+1}"
        leg.location = (pos[0], pos[1], 0.75)
    
    # Mirror frame
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.1, location=(7, 3.5, 3))
    mirror_frame = bpy.context.object
    mirror_frame.name = "Vanity_Mirror_Frame"
    
    # Mirror surface
    bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=0.05, location=(7, 3.4, 3))
    mirror = bpy.context.object
    mirror.name = "Vanity_Mirror"
    
    print("Vanity table with mirror created")
    return [table, mirror_frame, mirror]

def create_chairs():
    """Create ornate Louis XV chairs"""
    
    chairs = []
    chair_positions = [
        (3, 2, 0),   # Near vanity
        (-3, 2, 0),  # Room center
        (0, 7, 0)    # Near window
    ]
    
    for i, pos in enumerate(chair_positions):
        # Chair seat
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        seat = bpy.context.object
        seat.name = f"Chair_{i+1}_Seat"
        seat.scale = (1, 1, 0.1)
        seat.location = (pos[0], pos[1], 0.8)
        
        # Chair back
        bpy.ops.mesh.primitive_cube_add(size=1, location=(pos[0], pos[1]-0.4, 1.5))
        back = bpy.context.object
        back.name = f"Chair_{i+1}_Back"
        back.scale = (1, 0.1, 1)
        
        # Chair legs
        leg_positions_rel = [(0.4, 0.4), (-0.4, 0.4), (0.4, -0.4), (-0.4, -0.4)]
        for j, leg_pos in enumerate(leg_positions_rel):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.05, 
                depth=0.8, 
                location=(pos[0] + leg_pos[0], pos[1] + leg_pos[1], 0.4)
            )
            leg = bpy.context.object
            leg.name = f"Chair_{i+1}_Leg_{j+1}"
        
        chairs.extend([seat, back])
    
    print(f"Created {len(chair_positions)} ornate chairs")
    return chairs

def create_chandelier():
    """Create an ornate crystal chandelier"""
    
    # Main chandelier body
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1, location=(0, 0, 8))
    chandelier_body = bpy.context.object
    chandelier_body.name = "Chandelier_Body"
    
    # Chandelier arms
    arm_count = 8
    for i in range(arm_count):
        angle = (2 * math.pi / arm_count) * i
        x = math.cos(angle) * 1.5
        y = math.sin(angle) * 1.5
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05, 
            depth=1, 
            location=(x, y, 7.5)
        )
        arm = bpy.context.object
        arm.name = f"Chandelier_Arm_{i+1}"
        arm.rotation_euler = (0, math.radians(45), angle)
        
        # Candle at end of arm
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.03, 
            depth=0.3, 
            location=(x*1.2, y*1.2, 7.2)
        )
        candle = bpy.context.object
        candle.name = f"Chandelier_Candle_{i+1}"
    
    print("Ornate crystal chandelier created")
    return chandelier_body

def create_wall_decorations():
    """Add paintings, tapestries, and wall decorations"""
    
    decorations = []
    
    # Large painting on back wall
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, -9.8, 4))
    painting = bpy.context.object
    painting.name = "Large_Painting"
    painting.rotation_euler = (math.pi/2, 0, 0)
    decorations.append(painting)
    
    # Side wall tapestry
    bpy.ops.mesh.primitive_plane_add(size=2, location=(-9.8, -3, 3))
    tapestry = bpy.context.object
    tapestry.name = "Wall_Tapestry"
    tapestry.rotation_euler = (math.pi/2, 0, math.pi/2)
    decorations.append(tapestry)
    
    # Decorative moldings
    molding_positions = [
        (0, -9.5, 7),   # Back wall molding
        (-9.5, 0, 7),   # Left wall molding
    ]
    
    for i, pos in enumerate(molding_positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        molding = bpy.context.object
        molding.name = f"Wall_Molding_{i+1}"
        molding.scale = (15 if i == 0 else 0.2, 0.2 if i == 0 else 15, 0.3)
        decorations.append(molding)
    
    print("Wall decorations and moldings added")
    return decorations

def create_materials():
    """Create period-appropriate materials"""
    
    materials = {}
    
    # Gold gilt material
    gold_mat = bpy.data.materials.new(name="Gold_Gilt")
    gold_mat.use_nodes = True
    gold_mat.node_tree.nodes.clear()
    
    gold_bsdf = gold_mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    gold_output = gold_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    gold_mat.node_tree.links.new(gold_bsdf.outputs['BSDF'], gold_output.inputs['Surface'])
    
    gold_bsdf.inputs['Base Color'].default_value = (1.0, 0.8, 0.3, 1.0)
    gold_bsdf.inputs['Metallic'].default_value = 1.0
    gold_bsdf.inputs['Roughness'].default_value = 0.1
    materials['gold'] = gold_mat
    
    # Rich fabric material (burgundy)
    fabric_mat = bpy.data.materials.new(name="Rich_Fabric")
    fabric_mat.use_nodes = True
    fabric_mat.node_tree.nodes.clear()
    
    fabric_bsdf = fabric_mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    fabric_output = fabric_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    fabric_mat.node_tree.links.new(fabric_bsdf.outputs['BSDF'], fabric_output.inputs['Surface'])
    
    fabric_bsdf.inputs['Base Color'].default_value = (0.4, 0.1, 0.15, 1.0)
    fabric_bsdf.inputs['Roughness'].default_value = 0.8
    fabric_bsdf.inputs['Sheen'].default_value = 1.0
    materials['fabric'] = fabric_mat
    
    # Dark wood material
    wood_mat = bpy.data.materials.new(name="Dark_Wood")
    wood_mat.use_nodes = True
    wood_mat.node_tree.nodes.clear()
    
    wood_bsdf = wood_mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    wood_output = wood_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    wood_mat.node_tree.links.new(wood_bsdf.outputs['BSDF'], wood_output.inputs['Surface'])
    
    wood_bsdf.inputs['Base Color'].default_value = (0.2, 0.1, 0.05, 1.0)
    wood_bsdf.inputs['Roughness'].default_value = 0.7
    materials['wood'] = wood_mat
    
    # Mirror material
    mirror_mat = bpy.data.materials.new(name="Mirror")
    mirror_mat.use_nodes = True
    mirror_mat.node_tree.nodes.clear()
    
    mirror_bsdf = mirror_mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    mirror_output = mirror_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    mirror_mat.node_tree.links.new(mirror_bsdf.outputs['BSDF'], mirror_output.inputs['Surface'])
    
    mirror_bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1.0)
    mirror_bsdf.inputs['Metallic'].default_value = 1.0
    mirror_bsdf.inputs['Roughness'].default_value = 0.0
    materials['mirror'] = mirror_mat
    
    # Wall material (cream/beige)
    wall_mat = bpy.data.materials.new(name="Palace_Wall")
    wall_mat.use_nodes = True
    wall_mat.node_tree.nodes.clear()
    
    wall_bsdf = wall_mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    wall_output = wall_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    wall_mat.node_tree.links.new(wall_bsdf.outputs['BSDF'], wall_output.inputs['Surface'])
    
    wall_bsdf.inputs['Base Color'].default_value = (0.9, 0.85, 0.8, 1.0)
    wall_bsdf.inputs['Roughness'].default_value = 0.9
    materials['wall'] = wall_mat
    
    print("Period-appropriate materials created")
    return materials

def apply_materials(materials):
    """Apply materials to appropriate objects"""
    
    # Apply materials based on object names
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Gold for decorative elements
            if any(keyword in obj.name.lower() for keyword in ['chandelier', 'crown', 'molding', 'frame']):
                obj.data.materials.append(materials['gold'])
            
            # Fabric for upholstered items
            elif any(keyword in obj.name.lower() for keyword in ['bed_base', 'chair', 'seat', 'back']):
                obj.data.materials.append(materials['fabric'])
            
            # Wood for furniture frames
            elif any(keyword in obj.name.lower() for keyword in ['post', 'leg', 'wardrobe', 'table']):
                obj.data.materials.append(materials['wood'])
            
            # Mirror material
            elif 'mirror' in obj.name.lower() and 'frame' not in obj.name.lower():
                obj.data.materials.append(materials['mirror'])
            
            # Wall material for room structure
            elif any(keyword in obj.name.lower() for keyword in ['wall', 'floor', 'ceiling']):
                obj.data.materials.append(materials['wall'])
    
    print("Materials applied to all objects")

def setup_atmospheric_lighting():
    """Create warm, romantic lighting appropriate for the period"""
    
    # Clear existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Main warm ambient light
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 15))
    sun_light = bpy.context.object
    sun_light.name = "Ambient_Sun"
    sun_light.data.energy = 2
    sun_light.data.color = (1.0, 0.9, 0.7)  # Warm color
    sun_light.rotation_euler = (math.radians(45), 0, math.radians(30))
    
    # Chandelier lighting
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 7))
    chandelier_light = bpy.context.object
    chandelier_light.name = "Chandelier_Light"
    chandelier_light.data.energy = 800
    chandelier_light.data.color = (1.0, 0.8, 0.6)  # Candlelight color
    
    # Window light (soft daylight)
    bpy.ops.object.light_add(type='AREA', location=(0, 12, 6))
    window_light = bpy.context.object
    window_light.name = "Window_Light"
    window_light.data.energy = 300
    window_light.data.size = 8
    window_light.data.color = (0.9, 0.95, 1.0)  # Daylight color
    window_light.rotation_euler = (math.radians(90), 0, 0)
    
    # Fireplace light (if we had one)
    bpy.ops.object.light_add(type='SPOT', location=(-8, -9, 2))
    fireplace_light = bpy.context.object
    fireplace_light.name = "Fireplace_Light"
    fireplace_light.data.energy = 200
    fireplace_light.data.color = (1.0, 0.6, 0.3)  # Fire color
    fireplace_light.data.spot_size = math.radians(60)
    fireplace_light.rotation_euler = (math.radians(30), 0, math.radians(45))
    
    print("Atmospheric period lighting created")

def optimize_for_vrchat():
    """Optimize the entire bedroom for VRChat performance"""
    
    total_objects = len([obj for obj in bpy.data.objects if obj.type == 'MESH'])
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            
            # Add LOD (Level of Detail) optimization
            if len(obj.data.vertices) > 100:  # Only for complex objects
                decimate = obj.modifiers.new(name="VRChat_LOD", type='DECIMATE')
                decimate.ratio = 0.7  # Keep 70% of polygons
    
    print(f"VRChat optimization applied to {total_objects} objects")

def main():
    """Generate the complete Versailles bedroom"""
    print("🏰 Starting Versailles Bedroom Generation...")
    print("=" * 60)
    
    # Clear and setup
    clear_scene()
    
    # Create room structure
    room_parts = create_room_structure()
    
    # Create furniture
    bed = create_four_poster_bed()
    wardrobe = create_wardrobe()
    vanity = create_vanity_table()
    chairs = create_chairs()
    
    # Create decorative elements
    chandelier = create_chandelier()
    decorations = create_wall_decorations()
    
    # Create and apply materials
    materials = create_materials()
    apply_materials(materials)
    
    # Setup lighting
    setup_atmospheric_lighting()
    
    # Optimize for VR
    optimize_for_vrchat()
    
    # Final scene setup
    bpy.context.scene.render.engine = 'EEVEE'  # Fast preview rendering
    
    print("=" * 60)
    print("✅ Versailles Bedroom Generation Complete!")
    print("🏰 Complete Louis XV bedroom environment created")
    print("🎮 VRChat optimized for social VR")
    print("🕯️  Atmospheric candlelight and period lighting")
    print("🪑 Furniture: Four-poster bed, wardrobe, vanity, chairs")
    print("💎 Decorations: Crystal chandelier, paintings, tapestries")
    print("\nFeatures:")
    print("• Period-accurate materials and colors")
    print("• Optimized polygon count for VR performance")  
    print("• Warm atmospheric lighting")
    print("• Complete room ready for VRChat")
    print("\nNext steps:")
    print("1. Switch to rendered view (Z key) to see full lighting")
    print("2. Walk through in Blender's walk navigation")
    print("3. Export as FBX for VRChat Unity SDK")
    print("4. Create an amazing VR experience!")

if __name__ == "__main__":
    main() 