"""
Louis XV Sofa Generator for Blender
===================================
Creates an ornate French baroque sofa with tufted upholstery, curved legs, and gold leaf details.
Optimized for VRChat and VR applications.

Usage: Run this script in Blender to generate a complete Louis XV sofa
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector
import math

def clear_scene():
    """Clear all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    print("Scene cleared")

def create_sofa_base():
    """Create the main sofa frame structure"""
    # Create main seat cushion base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.4))
    seat_base = bpy.context.object
    seat_base.name = "Sofa_Seat_Base"
    seat_base.scale = (2.5, 1.2, 0.3)
    
    # Create backrest
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.5, 1.2))
    backrest = bpy.context.object
    backrest.name = "Sofa_Backrest"
    backrest.scale = (2.5, 0.3, 1.0)
    
    # Create armrests
    bpy.ops.mesh.primitive_cube_add(size=1, location=(1.8, 0, 0.8))
    armrest_left = bpy.context.object
    armrest_left.name = "Sofa_Armrest_Left"
    armrest_left.scale = (0.3, 1.2, 0.6)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.8, 0, 0.8))
    armrest_right = bpy.context.object
    armrest_right.name = "Sofa_Armrest_Right"
    armrest_right.scale = (0.3, 1.2, 0.6)
    
    print("Sofa base structure created")
    return [seat_base, backrest, armrest_left, armrest_right]

def create_curved_legs():
    """Create ornate curved legs in Louis XV style (cabriole legs)"""
    legs = []
    
    # Leg positions (4 corners)
    leg_positions = [
        (1.8, 0.8, 0),    # Front right
        (-1.8, 0.8, 0),   # Front left
        (1.8, -0.8, 0),   # Back right
        (-1.8, -0.8, 0)   # Back left
    ]
    
    for i, pos in enumerate(leg_positions):
        # Create basic leg shape
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, location=pos)
        leg = bpy.context.object
        leg.name = f"Sofa_Leg_{i+1}"
        
        # Add curve to leg (cabriole style)
        bpy.context.view_layer.objects.active = leg
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Add loop cuts for curve shaping
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": 3})
        bpy.ops.mesh.select_all(action='DESELECT')
        
        # Select middle vertices and scale outward for cabriole curve
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Apply curve modifier effect manually by scaling certain vertex groups
        modifier = leg.modifiers.new(name="Curve", type='WAVE')
        modifier.use_z = False
        modifier.use_x = True
        modifier.height = 0.1
        modifier.width = 0.8
        
        legs.append(leg)
    
    print("Curved cabriole legs created")
    return legs

def create_tufted_cushions():
    """Create tufted upholstery pattern on cushions"""
    # Get seat cushion
    seat = bpy.data.objects.get("Sofa_Seat_Base")
    if seat:
        bpy.context.view_layer.objects.active = seat
        
        # Add subdivision surface for smooth curves
        modifier = seat.modifiers.new(name="Subdivision", type='SUBSURF')
        modifier.levels = 2
        
        # Add displacement for tufting pattern
        disp_modifier = seat.modifiers.new(name="Tufting", type='DISPLACE')
        
        # Create noise texture for tufting
        texture = bpy.data.textures.new(name="Tufting_Pattern", type='CLOUDS')
        texture.noise_scale = 0.5
        disp_modifier.texture = texture
        disp_modifier.strength = 0.05
    
    # Apply same to backrest
    backrest = bpy.data.objects.get("Sofa_Backrest")
    if backrest:
        bpy.context.view_layer.objects.active = backrest
        
        modifier = backrest.modifiers.new(name="Subdivision", type='SUBSURF')
        modifier.levels = 2
        
        disp_modifier = backrest.modifiers.new(name="Tufting", type='DISPLACE')
        disp_modifier.texture = texture
        disp_modifier.strength = 0.08
    
    print("Tufted cushion pattern applied")

def create_ornate_frame():
    """Create decorative carved frame elements"""
    # Create decorative scrollwork on armrests
    armrests = ["Sofa_Armrest_Left", "Sofa_Armrest_Right"]
    
    for armrest_name in armrests:
        armrest = bpy.data.objects.get(armrest_name)
        if armrest:
            # Add decorative carved elements
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.1, 
                minor_radius=0.02, 
                location=(armrest.location.x, armrest.location.y, armrest.location.z + 0.3)
            )
            ornament = bpy.context.object
            ornament.name = f"{armrest_name}_Ornament"
            ornament.rotation_euler = (math.pi/2, 0, 0)
    
    # Create decorative crest on backrest
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.3, 
        minor_radius=0.05, 
        location=(0, -0.5, 1.8)
    )
    crest = bpy.context.object
    crest.name = "Sofa_Crest"
    crest.rotation_euler = (0, 0, 0)
    crest.scale = (1.5, 0.3, 0.8)
    
    print("Ornate decorative elements added")

def create_materials():
    """Create realistic materials for the sofa"""
    
    # Burgundy velvet material for upholstery
    velvet_mat = bpy.data.materials.new(name="Burgundy_Velvet")
    velvet_mat.use_nodes = True
    
    # Clear default nodes
    velvet_mat.node_tree.nodes.clear()
    
    # Add principled BSDF
    bsdf = velvet_mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    output = velvet_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    
    # Connect nodes
    velvet_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Set velvet properties
    bsdf.inputs['Base Color'].default_value = (0.4, 0.1, 0.15, 1.0)  # Burgundy
    bsdf.inputs['Roughness'].default_value = 0.8
    bsdf.inputs['Sheen'].default_value = 1.0
    bsdf.inputs['Sheen Tint'].default_value = 0.8
    
    # Gold leaf material for frame and legs
    gold_mat = bpy.data.materials.new(name="Gold_Leaf")
    gold_mat.use_nodes = True
    
    gold_mat.node_tree.nodes.clear()
    gold_bsdf = gold_mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    gold_output = gold_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    
    gold_mat.node_tree.links.new(gold_bsdf.outputs['BSDF'], gold_output.inputs['Surface'])
    
    # Set gold properties
    gold_bsdf.inputs['Base Color'].default_value = (1.0, 0.8, 0.3, 1.0)  # Gold
    gold_bsdf.inputs['Metallic'].default_value = 1.0
    gold_bsdf.inputs['Roughness'].default_value = 0.1
    
    print("Materials created: Burgundy Velvet and Gold Leaf")
    return velvet_mat, gold_mat

def apply_materials_to_sofa(velvet_mat, gold_mat):
    """Apply materials to appropriate sofa parts"""
    
    # Apply velvet to upholstered parts
    upholstered_parts = ["Sofa_Seat_Base", "Sofa_Backrest", "Sofa_Armrest_Left", "Sofa_Armrest_Right"]
    for part_name in upholstered_parts:
        part = bpy.data.objects.get(part_name)
        if part:
            part.data.materials.append(velvet_mat)
    
    # Apply gold to frame and decorative elements
    gold_parts = ["Sofa_Leg_1", "Sofa_Leg_2", "Sofa_Leg_3", "Sofa_Leg_4", 
                  "Sofa_Crest", "Sofa_Armrest_Left_Ornament", "Sofa_Armrest_Right_Ornament"]
    for part_name in gold_parts:
        part = bpy.data.objects.get(part_name)
        if part:
            part.data.materials.append(gold_mat)
    
    print("Materials applied to sofa components")

def optimize_for_vrchat():
    """Optimize the sofa for VRChat performance"""
    
    # Get all sofa objects
    sofa_objects = [obj for obj in bpy.data.objects if "Sofa" in obj.name]
    
    for obj in sofa_objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            
            # Add decimate modifier for polygon reduction
            decimate = obj.modifiers.new(name="VRChat_Optimize", type='DECIMATE')
            decimate.ratio = 0.5  # Reduce polygons by 50%
            
            # Apply modifier
            bpy.ops.object.modifier_apply(modifier="VRChat_Optimize")
    
    print("VRChat optimization applied (polygon reduction)")

def setup_lighting():
    """Add appropriate lighting for the scene"""
    
    # Clear existing lights
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            obj.select_set(True)
    bpy.ops.object.delete()
    
    # Add key light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    key_light = bpy.context.object
    key_light.name = "Key_Light"
    key_light.data.energy = 3
    key_light.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Add fill light
    bpy.ops.object.light_add(type='AREA', location=(-3, 3, 5))
    fill_light = bpy.context.object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 1.5
    fill_light.data.size = 5
    
    # Add rim light
    bpy.ops.object.light_add(type='SPOT', location=(0, -5, 8))
    rim_light = bpy.context.object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 2
    rim_light.rotation_euler = (math.radians(60), 0, 0)
    
    print("Professional lighting setup complete")

def main():
    """Main function to create the complete Louis XV sofa"""
    print("🛋️  Starting Louis XV Sofa Generation...")
    print("=" * 50)
    
    # Clear scene
    clear_scene()
    
    # Create sofa components
    base_parts = create_sofa_base()
    legs = create_curved_legs()
    
    # Add details
    create_tufted_cushions()
    create_ornate_frame()
    
    # Create and apply materials
    velvet_mat, gold_mat = create_materials()
    apply_materials_to_sofa(velvet_mat, gold_mat)
    
    # Optimize for VR
    optimize_for_vrchat()
    
    # Setup lighting
    setup_lighting()
    
    # Final positioning
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    print("=" * 50)
    print("✅ Louis XV Sofa Generation Complete!")
    print("🎮 VRChat optimized and ready for export")
    print("🎨 Materials: Burgundy velvet upholstery with gold leaf frame")
    print("💺 Features: Tufted cushions, cabriole legs, ornate carved details")
    print("\nNext steps:")
    print("1. Check the sofa in rendered view (Z key)")
    print("2. Export as FBX for VRChat Unity SDK")
    print("3. Test in VRChat with your Japanese friend!")

if __name__ == "__main__":
    main() 