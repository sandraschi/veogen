# 3D Printer Scripts Examples

This directory contains example scripts that demonstrate how to use the VeoGen 3D printer Blender scripts collection.

## Example Scripts

### **weird_objects_sampler.py**
A comprehensive example that generates multiple mathematical and impossible objects in organized layouts.

**Features:**
- Educational set (Möbius strip, Klein bottle, trefoil knot)
- Optical illusion set (Penrose triangle, impossible cube, double Möbius)
- Advanced knots collection (various torus knot configurations)
- Single showcase object option
- Print setting recommendations

**Usage:**
1. Open Blender
2. Open this script in the Text Editor
3. Run with Alt+P
4. Check console for progress and recommendations

**Customization:**
Edit the `if __name__ == "__main__":` section to choose which collection to generate:
```python
# Full collection (recommended)
create_weird_sampler_collection()

# Single impressive object
# create_single_showcase_object()

# Educational set only
# create_educational_set()
```

## How to Use Examples

1. **Load Script**: Open Blender, go to Scripting workspace
2. **Open File**: Click "Open" and select the example script
3. **Run Script**: Press Alt+P or click the "Play" button
4. **Check Console**: View progress and recommendations in the console
5. **Export Objects**: Select objects and export as STL for 3D printing

## Creating Your Own Examples

When creating new example scripts:

1. Import the required modules from the parent directory
2. Use descriptive function names
3. Include print setting recommendations
4. Add progress messages for user feedback
5. Organize objects spatially for easy viewing

## Print Recommendations

**Mathematical Objects:**
- Layer Height: 0.1-0.2mm for smooth curves
- Infill: 15-20% (decorative pieces)
- Support: Usually not needed
- Material: PLA for display, PETG for durability

**Complex Surfaces:**
- Higher resolution settings recommended
- Check for manifold geometry before printing
- Consider orientation for best surface finish 