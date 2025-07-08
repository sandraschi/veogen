# 3D Printer Blender Scripts Collection

This directory contains a comprehensive collection of Blender Python scripts designed specifically for creating 3D printable objects. All scripts are optimized for 3D printing with proper wall thickness, minimal support requirements, and practical functionality.

## Scripts Overview

### 1. **phone_stand.py** - Phone & Tablet Stands
Generate customizable phone and tablet stands with various configurations.

**Features:**
- Adjustable viewing angles (65-75°)
- Multiple sizes (phone, tablet, compact)
- Customizable slot dimensions
- Support-free printing design
- Proper wall thickness (3mm)

**Usage:**
```python
# Standard phone stand
create_phone_stand(
    phone_width=80,        # mm
    phone_thickness=10,    # mm
    stand_height=120,      # mm
    viewing_angle=70       # degrees
)
```

### 2. **desk_organizer.py** - Desk Organization
Create modular desk organizers with compartments and pen holders.

**Features:**
- Customizable compartment grids
- Individual pen hole patterns
- Multiple sizes and configurations
- Stackable design
- Clean, professional appearance

**Usage:**
```python
# Large organizer with 3x2 compartments
create_desk_organizer(
    width=200,            # mm
    depth=150,            # mm
    height=60,            # mm
    compartments_x=3,     # horizontal compartments
    compartments_y=2      # vertical compartments
)
```

### 3. **mechanical_parts.py** - Gears, Bolts & Brackets
Generate functional mechanical components for projects and repairs.

**Features:**
- Parametric gears with customizable teeth
- Hex and round bolt heads
- L-brackets and corner brackets
- Standard mounting hole patterns
- Proper tolerances for moving parts

**Usage:**
```python
# 24-tooth gear
create_gear(
    num_teeth=24,
    outer_radius=30,      # mm
    thickness=6,          # mm
    center_hole=8         # mm
)

# Mounting bracket
create_bracket(
    width=50,             # mm
    height=30,            # mm
    thickness=3,          # mm
    num_holes=2
)
```

### 4. **kitchen_utilities.py** - Household Items
Create practical kitchen and household utility items.

**Features:**
- Measuring cups with handles
- Spice containers with lids
- Cable organizers
- Soap dispensers
- Food-safe design considerations

**Usage:**
```python
# 250ml measuring cup
create_measuring_cup(
    capacity_ml=250,
    height=80,            # mm
    handle_length=30      # mm
)

# Spice container with shaker holes
create_spice_container(
    diameter=40,          # mm
    height=60,            # mm
    holes_pattern="shaker"
)
```

### 5. **miniatures.py** - Collectibles & Decoratives
Generate miniature figurines, chess pieces, and decorative objects.

**Features:**
- Simple humanoid figurines
- Chess pieces (pawn, rook, bishop)
- Decorative vases
- Keychain tags
- Appropriate detail for miniature printing

**Usage:**
```python
# Simple figurine
create_simple_figurine(
    height=50,            # mm
    head_size=8,          # mm
    base_diameter=20      # mm
)

# Chess piece
create_chess_piece(
    piece_type="pawn",    # pawn, rook, bishop
    height=40,            # mm
    color="white"         # white or black
)
```

### 6. **mathematical_objects.py** - Weird & Impossible Objects
Create mathematical constructs and pseudo-Escher illusions.

**Features:**
- Möbius strips (one-sided surfaces)
- Klein bottles (non-orientable surfaces)
- Penrose triangles (impossible triangles)
- Impossible cubes (optical illusions)
- Trefoil knots (mathematical knots)
- Torus knots (complex knot variations)
- Educational and conversation pieces

**Usage:**
```python
# Classic Möbius strip
create_mobius_strip(
    radius=40,            # mm
    width=20,             # mm
    thickness=2,          # mm
    twists=1              # half-twists
)

# Klein bottle
create_klein_bottle(
    radius=30,            # mm
    height=60,            # mm
    thickness=2           # mm
)

# Penrose triangle (impossible triangle)
create_penrose_triangle(
    size=50,              # mm
    thickness=8,          # mm
    beam_width=12         # mm
)

# Trefoil knot
create_trefoil_knot(
    radius=25,            # mm
    tube_radius=8         # mm
)
```

## 3D Printing Optimization Features

All scripts include these optimization features:

### **Structural Design**
- **Wall Thickness**: 2-3mm minimum for durability
- **Base Thickness**: 3-5mm for stability
- **Support-Free**: Designed to print without supports when possible
- **Overhangs**: Limited to 45° or less where possible

### **Tolerances**
- **Clearances**: 0.1-0.2mm for tight fits
- **Clearances**: 0.5-1mm for loose fits
- **Hole Sizes**: Slightly undersized for post-processing

### **Print Settings Compatibility**
- **FDM Printers**: 0.2-0.4mm layer height
- **Resin Printers**: 0.05-0.1mm layer height
- **Nozzle Sizes**: Optimized for 0.4mm nozzles

## Material Considerations

### **Recommended Materials**
- **PLA**: General household items, prototypes
- **PETG**: Kitchen items, mechanical parts
- **ABS**: Automotive parts, tools
- **TPU**: Flexible components, gaskets

### **Post-Processing**
- **Hole Drilling**: Many holes designed for post-drill cleanup
- **Sanding**: Smooth contact surfaces
- **Painting**: Models include material assignments for color guidance

## Usage Instructions

### **Basic Usage**
1. Open Blender
2. Load script in Text Editor
3. Run script with Alt+P
4. Objects will be generated in the scene

### **Customization**
Each script allows parameter customization:
```python
# Example: Custom phone stand
create_phone_stand(
    phone_width=85,       # Your phone width
    phone_thickness=12,   # Your phone thickness
    viewing_angle=65,     # Preferred angle
    wall_thickness=4      # Stronger walls
)
```

### **Batch Generation**
Run the main functions to generate multiple variants:
```python
# Generate complete sets
create_phone_stand_variants()
create_desk_organizer_set()
create_mechanical_parts_set()
```

## File Export for 3D Printing

After generating objects:

1. **Select Object**: Click on the object to select it
2. **Export STL**: File → Export → STL
3. **Export Settings**:
   - Apply Modifiers: ✓
   - Selection Only: ✓
   - Scale: 1.0 (scripts use mm units)

## Design Philosophy

These scripts follow key 3D printing design principles:

### **Functionality First**
- Every object serves a practical purpose
- Dimensions based on real-world measurements
- Ergonomic considerations included

### **Printability**
- Minimize support material requirements
- Optimize orientation for strength
- Consider layer adhesion in design

### **Customization**
- Parametric design for easy modification
- Modular components where applicable
- Scalable designs for different needs

### **Educational Value**
- Mathematical objects demonstrate topology and geometry concepts
- Impossible objects showcase optical illusions in physical form
- Knot theory visualization through trefoil and torus knots
- Non-orientable surfaces like Klein bottles challenge spatial understanding

## Contributing

When adding new scripts to this collection:

1. **Follow naming convention**: `category_name.py`
2. **Include documentation**: Function docstrings with parameter descriptions
3. **Add material assignments**: For visual feedback and print planning
4. **Test printability**: Ensure designs can actually be 3D printed
5. **Update this README**: Add your script to the overview section
6. **Mathematical objects**: For complex surfaces, ensure manifold geometry for 3D printing
7. **Parametric design**: Make dimensions easily customizable

## Troubleshooting

### **Common Issues**
- **Mesh Errors**: Run "Mesh → Clean Up → Fill Holes" in Blender
- **Scale Issues**: Scripts use mm units, ensure proper STL export scale
- **Support Needs**: Some complex geometries may still require supports
- **Mathematical Objects**: Klein bottles and Möbius strips may need higher resolution for smooth curves
- **Non-Manifold Geometry**: Mathematical surfaces sometimes create complex intersections - use "3D Print Toolbox" addon for validation

### **Performance**
- **Boolean Operations**: May slow down on complex geometries
- **High Polygon Count**: Reduce subdivision levels for faster generation
- **Memory Usage**: Clear scene between different script runs

## License

These scripts are provided for educational and personal use. Commercial use should consider licensing requirements for any embedded libraries or assets.

---

*Generated by VeoGen's 3D Printer Script Collection*
*Optimized for practical 3D printing applications* 