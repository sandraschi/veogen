"""
Simple Furniture Generator for Blender
=====================================
Quick and easy furniture generation for testing and iteration.
Perfect for Saturday Sofa project experiments!

Usage: Run individual functions or the main() for a complete set
"""

import bpy
import math

def clear_scene():
    """Clear all objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    print("🧹 Scene cleared")

def create_simple_sofa():
    """Create a simple sofa for testing"""
    # Seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    seat = bpy.context.object
    seat.name = "Simple_Sofa_Seat"
    seat.scale = (3, 1.5, 0.3)
    
    # Backrest
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.6, 1.2))
    back = bpy.context.object
    back.name = "Simple_Sofa_Back"
    back.scale = (3, 0.3, 1.2)
    
    # Armrests
    bpy.ops.mesh.primitive_cube_add(size=1, location=(1.6, 0, 1))
    arm1 = bpy.context.object
    arm1.name = "Simple_Sofa_Arm_L"
    arm1.scale = (0.3, 1.5, 0.8)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.6, 0, 1))
    arm2 = bpy.context.object
    arm2.name = "Simple_Sofa_Arm_R"
    arm2.scale = (0.3, 1.5, 0.8)
    
    print("🛋️  Simple sofa created!")
    return [seat, back, arm1, arm2]

def create_simple_chair():
    """Create a simple chair"""
    # Seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.8))
    seat = bpy.context.object
    seat.name = "Simple_Chair_Seat"
    seat.scale = (1, 1, 0.1)
    
    # Back
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.4, 1.5))
    back = bpy.context.object
    back.name = "Simple_Chair_Back"
    back.scale = (1, 0.1, 1)
    
    # Legs
    leg_positions = [(0.4, 0.4, 0.4), (-0.4, 0.4, 0.4), (0.4, -0.4, 0.4), (-0.4, -0.4, 0.4)]
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.8, location=pos)
        leg = bpy.context.object
        leg.name = f"Simple_Chair_Leg_{i+1}"
    
    print("🪑 Simple chair created!")
    return [seat, back]

def create_simple_table():
    """Create a simple table"""
    # Table top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
    top = bpy.context.object
    top.name = "Simple_Table_Top"
    top.scale = (2, 1, 0.1)
    
    # Legs
    leg_positions = [(0.9, 0.4, 0.75), (-0.9, 0.4, 0.75), (0.9, -0.4, 0.75), (-0.9, -0.4, 0.75)]
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.5, location=pos)
        leg = bpy.context.object
        leg.name = f"Simple_Table_Leg_{i+1}"
    
    print("🪑 Simple table created!")
    return [top]

def create_simple_bed():
    """Create a simple bed"""
    # Mattress
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.8))
    mattress = bpy.context.object
    mattress.name = "Simple_Bed_Mattress"
    mattress.scale = (3, 5, 0.4)
    
    # Headboard
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2.3, 1.5))
    headboard = bpy.context.object
    headboard.name = "Simple_Bed_Headboard"
    headboard.scale = (3, 0.2, 1.5)
    
    # Bed frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.3))
    frame = bpy.context.object
    frame.name = "Simple_Bed_Frame"
    frame.scale = (3.2, 5.2, 0.2)
    
    print("🛏️  Simple bed created!")
    return [mattress, headboard, frame]

def test_saturday_sofa():
    """Special test function for Saturday sofa project"""
    print("🎯 SATURDAY SOFA PROJECT TEST")
    print("=" * 40)
    
    clear_scene()
    
    # Create test sofa
    sofa_parts = create_simple_sofa()
    
    # Add basic lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    light = bpy.context.object
    light.name = "Test_Light"
    light.data.energy = 3
    
    # Add simple material
    mat = bpy.data.materials.new(name="Test_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.2, 0.2, 1.0)  # Red
    
    # Apply material to sofa
    for part in sofa_parts:
        part.data.materials.append(mat)
    
    print("✅ Saturday sofa test complete!")
    print("🎮 Ready for VRChat testing!")
    print("🇯🇵 Perfect for your Japanese friend!")

def create_room_layout():
    """Create a simple room with multiple furniture pieces"""
    clear_scene()
    
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "Room_Floor"
    
    # Create furniture at different positions
    # Sofa
    sofa = create_simple_sofa()
    
    # Chair next to sofa
    bpy.ops.object.select_all(action='DESELECT')
    chair = create_simple_chair()
    for obj in bpy.data.objects:
        if "Chair" in obj.name:
            obj.location.x += 3
    
    # Table in front
    table = create_simple_table()
    for obj in bpy.data.objects:
        if "Table" in obj.name:
            obj.location.y += 2
    
    # Bed in back
    bed = create_simple_bed()
    for obj in bpy.data.objects:
        if "Bed" in obj.name:
            obj.location.y -= 5
    
    # Basic lighting
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    light = bpy.context.object
    light.data.energy = 2
    
    print("🏠 Complete room layout created!")
    print("🪑 Furniture: Sofa, Chair, Table, Bed")
    print("💡 Basic lighting added")

def main():
    """Main function - create the simple furniture showcase"""
    print("🛠️  Simple Furniture Generator")
    print("=" * 30)
    
    # Option 1: Just test the Saturday sofa
    test_saturday_sofa()
    
    # Option 2: Create full room (uncomment next line)
    # create_room_layout()
    
    print("\n🎉 Ready to test in Blender!")
    print("Next steps:")
    print("1. Press Z for rendered view")
    print("2. Test camera angles")
    print("3. Export as FBX for VRChat")
    print("4. Saturday sofa project GO! 🚀")

if __name__ == "__main__":
    main() 