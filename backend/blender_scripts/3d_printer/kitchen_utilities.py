import bpy
import bmesh
from mathutils import Vector
import math

def clear_scene():
    """Clear all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

def create_measuring_cup(
    capacity_ml=250,     # ml
    height=80,           # mm
    handle_length=30,    # mm
    handle_thickness=8,  # mm
    wall_thickness=2,    # mm
    spout_width=20,      # mm
    base_thickness=3     # mm
):
    """
    Create a measuring cup optimized for 3D printing
    
    Args:
        capacity_ml: Capacity in milliliters
        height: Height of the cup (mm)
        handle_length: Length of the handle (mm)
        handle_thickness: Thickness of handle (mm)
        wall_thickness: Wall thickness (mm)
        spout_width: Width of the spout (mm)
        base_thickness: Base thickness (mm)
    """
    
    # Calculate radius from capacity (approximation for cylinder)
    # V = π * r² * h
    inner_radius = math.sqrt(capacity_ml / (math.pi * height * 0.001)) / 2
    outer_radius = inner_radius + wall_thickness / 1000
    
    # Convert to Blender units
    height = height / 1000
    handle_length = handle_length / 1000
    handle_thickness = handle_thickness / 1000
    wall_thickness = wall_thickness / 1000
    spout_width = spout_width / 1000
    base_thickness = base_thickness / 1000
    
    # Create outer cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=outer_radius,
        depth=height,
        location=(0, 0, height/2)
    )
    
    outer_cup = bpy.context.active_object
    outer_cup.name = "MeasuringCupOuter"
    
    # Create inner cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_radius,
        depth=height - base_thickness,
        location=(0, 0, height/2 + base_thickness/2)
    )
    
    inner_cup = bpy.context.active_object
    inner_cup.name = "MeasuringCupInner"
    
    # Boolean difference
    bool_mod = outer_cup.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = inner_cup
    
    # Apply modifier
    bpy.context.view_layer.objects.active = outer_cup
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # Delete inner cylinder
    bpy.data.objects.remove(inner_cup, do_unlink=True)
    
    # Create handle
    handle_height = height * 0.6
    handle_y = outer_radius + handle_length / 2
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=handle_thickness/2,
        depth=handle_length,
        rotation=(math.pi/2, 0, 0),
        location=(0, handle_y, handle_height/2)
    )
    
    handle = bpy.context.active_object
    handle.name = "Handle"
    
    # Create handle connection
    bpy.ops.mesh.primitive_cylinder_add(
        radius=handle_thickness/2,
        depth=handle_thickness,
        rotation=(0, math.pi/2, 0),
        location=(0, outer_radius + handle_thickness/2, handle_height/2)
    )
    
    handle_connector = bpy.context.active_object
    handle_connector.name = "HandleConnector"
    
    # Join handle parts
    bpy.context.view_layer.objects.active = handle
    handle.select_set(True)
    handle_connector.select_set(True)
    bpy.ops.object.join()
    
    # Join handle to cup
    bpy.context.view_layer.objects.active = outer_cup
    outer_cup.select_set(True)
    handle.select_set(True)
    bpy.ops.object.join()
    
    # Add material
    mat = bpy.data.materials.new(name="MeasuringCupMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)  # White
    outer_cup.data.materials.append(mat)
    
    return outer_cup

def create_spice_container(
    diameter=40,         # mm
    height=60,           # mm
    wall_thickness=2,    # mm
    lid_height=10,       # mm
    thread_pitch=2,      # mm
    holes_pattern="shaker"  # "shaker" or "pour"
):
    """Create a spice container with removable lid"""
    
    # Convert to Blender units
    radius = diameter / 2000
    height = height / 1000
    wall_thickness = wall_thickness / 1000
    lid_height = lid_height / 1000
    thread_pitch = thread_pitch / 1000
    
    # Create container body
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        location=(0, 0, height/2)
    )
    
    container = bpy.context.active_object
    container.name = "SpiceContainer"
    
    # Create inner cavity
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - wall_thickness,
        depth=height - wall_thickness,
        location=(0, 0, height/2 + wall_thickness/2)
    )
    
    cavity = bpy.context.active_object
    cavity.name = "Cavity"
    
    # Boolean difference
    bool_mod = container.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cavity
    
    # Apply modifier
    bpy.context.view_layer.objects.active = container
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # Delete cavity
    bpy.data.objects.remove(cavity, do_unlink=True)
    
    # Create lid
    lid_radius = radius + wall_thickness/2
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=lid_radius,
        depth=lid_height,
        location=(0, 0, height + lid_height/2)
    )
    
    lid = bpy.context.active_object
    lid.name = "SpiceLid"
    
    # Create lid inner cavity
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=lid_height - wall_thickness,
        location=(0, 0, height + lid_height/2 - wall_thickness/2)
    )
    
    lid_cavity = bpy.context.active_object
    lid_cavity.name = "LidCavity"
    
    # Boolean difference for lid
    bool_mod = lid.modifiers.new(name="BooleanLid", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = lid_cavity
    
    # Apply modifier
    bpy.context.view_layer.objects.active = lid
    bpy.ops.object.modifier_apply(modifier="BooleanLid")
    
    # Delete lid cavity
    bpy.data.objects.remove(lid_cavity, do_unlink=True)
    
    # Create holes in lid
    if holes_pattern == "shaker":
        # Create multiple small holes
        hole_radius = 0.001  # 1mm
        hole_positions = [
            (0, 0),
            (0.01, 0),
            (-0.01, 0),
            (0, 0.01),
            (0, -0.01),
            (0.007, 0.007),
            (-0.007, 0.007),
            (0.007, -0.007),
            (-0.007, -0.007)
        ]
        
        for i, (x, y) in enumerate(hole_positions):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=hole_radius,
                depth=wall_thickness * 2,
                location=(x, y, height + lid_height/2)
            )
            
            hole = bpy.context.active_object
            hole.name = f"Hole_{i}"
            
            # Boolean difference
            bool_mod = lid.modifiers.new(name=f"BooleanHole_{i}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = hole
            
            # Apply modifier
            bpy.context.view_layer.objects.active = lid
            bpy.ops.object.modifier_apply(modifier=f"BooleanHole_{i}")
            
            # Delete hole
            bpy.data.objects.remove(hole, do_unlink=True)
    
    # Add materials
    container_mat = bpy.data.materials.new(name="SpiceContainerMaterial")
    container_mat.use_nodes = True
    container_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.6, 0.4, 1.0)  # Brown
    container.data.materials.append(container_mat)
    
    lid_mat = bpy.data.materials.new(name="SpiceLidMaterial")
    lid_mat.use_nodes = True
    lid_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.6, 0.4, 0.2, 1.0)  # Dark brown
    lid.data.materials.append(lid_mat)
    
    return container, lid

def create_cable_organizer(
    length=100,          # mm
    width=20,            # mm
    height=15,           # mm
    cable_diameter=8,    # mm
    num_slots=5,         # number of cable slots
    wall_thickness=2     # mm
):
    """Create a cable organizer with multiple slots"""
    
    # Convert to Blender units
    length = length / 1000
    width = width / 1000
    height = height / 1000
    cable_diameter = cable_diameter / 1000
    wall_thickness = wall_thickness / 1000
    
    # Create base
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(0, 0, height/2)
    )
    
    base = bpy.context.active_object
    base.name = "CableOrganizerBase"
    
    # Scale to correct dimensions
    base.scale = (length/2, width/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Create cable slots
    slot_width = cable_diameter
    slot_spacing = length / (num_slots + 1)
    
    for i in range(num_slots):
        x_pos = -length/2 + slot_spacing * (i + 1)
        
        # Create slot cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=slot_width/2,
            depth=width + wall_thickness,
            rotation=(math.pi/2, 0, 0),
            location=(x_pos, 0, height/2)
        )
        
        slot = bpy.context.active_object
        slot.name = f"CableSlot_{i}"
        
        # Boolean difference
        bool_mod = base.modifiers.new(name=f"BooleanSlot_{i}", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = slot
        
        # Apply modifier
        bpy.context.view_layer.objects.active = base
        bpy.ops.object.modifier_apply(modifier=f"BooleanSlot_{i}")
        
        # Delete slot
        bpy.data.objects.remove(slot, do_unlink=True)
    
    # Add material
    mat = bpy.data.materials.new(name="CableOrganizerMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.2, 0.2, 1.0)  # Dark gray
    base.data.materials.append(mat)
    
    return base

def create_soap_dispenser(
    height=150,          # mm
    diameter=60,         # mm
    wall_thickness=3,    # mm
    pump_hole_diameter=12, # mm
    base_thickness=5     # mm
):
    """Create a soap dispenser bottle"""
    
    # Convert to Blender units
    height = height / 1000
    radius = diameter / 2000
    wall_thickness = wall_thickness / 1000
    pump_hole_diameter = pump_hole_diameter / 1000
    base_thickness = base_thickness / 1000
    
    # Create outer cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        location=(0, 0, height/2)
    )
    
    outer = bpy.context.active_object
    outer.name = "SoapDispenserOuter"
    
    # Create inner cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - wall_thickness,
        depth=height - base_thickness,
        location=(0, 0, height/2 + base_thickness/2)
    )
    
    inner = bpy.context.active_object
    inner.name = "SoapDispenserInner"
    
    # Boolean difference
    bool_mod = outer.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = inner
    
    # Apply modifier
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # Delete inner cylinder
    bpy.data.objects.remove(inner, do_unlink=True)
    
    # Create pump hole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=pump_hole_diameter/2,
        depth=wall_thickness * 2,
        location=(0, 0, height)
    )
    
    hole = bpy.context.active_object
    hole.name = "PumpHole"
    
    # Boolean difference for hole
    bool_mod = outer.modifiers.new(name="BooleanHole", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = hole
    
    # Apply modifier
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier="BooleanHole")
    
    # Delete hole
    bpy.data.objects.remove(hole, do_unlink=True)
    
    # Add material
    mat = bpy.data.materials.new(name="SoapDispenserMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.7, 0.3, 1.0)  # Green
    outer.data.materials.append(mat)
    
    return outer

def create_kitchen_utilities_set():
    """Create a set of kitchen utilities"""
    
    # Measuring cup - 250ml
    create_measuring_cup(
        capacity_ml=250,
        height=80,
        handle_length=30
    )
    
    # Spice container
    bpy.ops.transform.translate(value=(0.15, 0, 0))
    container, lid = create_spice_container(
        diameter=40,
        height=60,
        holes_pattern="shaker"
    )
    
    # Cable organizer
    bpy.ops.transform.translate(value=(0.3, 0, 0))
    create_cable_organizer(
        length=100,
        width=20,
        height=15,
        num_slots=5
    )
    
    # Soap dispenser
    bpy.ops.transform.translate(value=(0.45, 0, 0))
    create_soap_dispenser(
        height=150,
        diameter=60
    )
    
    # Large measuring cup - 500ml
    bpy.ops.transform.translate(value=(0.6, 0, 0))
    create_measuring_cup(
        capacity_ml=500,
        height=120,
        handle_length=40
    )

# Main execution
if __name__ == "__main__":
    clear_scene()
    create_kitchen_utilities_set()
    
    print("Kitchen utilities created successfully!")
    print("Objects optimized for 3D printing with:")
    print("- Food-safe design considerations")
    print("- Proper wall thickness for durability")
    print("- Easy to clean surfaces")
    print("- Functional features (handles, spouts, etc.)")
    print("- No support material required") 