#!/usr/bin/env python3
"""
Weird Objects Sampler - VeoGen 3D Printer Scripts
=================================================

This example script demonstrates how to generate a collection of
mathematical and pseudo-impossible objects perfect for:

- Educational demonstrations
- Conversation pieces  
- Testing 3D printer capabilities
- Mathematical visualization
- Mind-bending desk decorations

Run this script in Blender to generate a complete set of weird objects.
"""

import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import our mathematical objects module
from mathematical_objects import *

def create_educational_set():
    """Create a set optimized for educational purposes"""
    
    print("Creating Educational Mathematical Objects Set...")
    
    # Classic Möbius strip - demonstrates one-sided surface
    create_mobius_strip(
        radius=35,
        width=18,
        thickness=2.5,
        subdivisions=64,
        twists=1
    )
    
    # Klein bottle - non-orientable surface
    bpy.ops.transform.translate(value=(0.12, 0, 0))
    create_klein_bottle(
        radius=28,
        height=55,
        thickness=2.5,
        subdivisions=48
    )
    
    # Trefoil knot - simplest non-trivial knot
    bpy.ops.transform.translate(value=(0.24, 0, 0))
    create_trefoil_knot(
        radius=22,
        tube_radius=7,
        subdivisions=128
    )
    
    print("Educational set complete!")

def create_illusion_set():
    """Create a set of optical illusion objects"""
    
    print("Creating Optical Illusion Objects Set...")
    
    # Move to new row
    bpy.ops.transform.translate(value=(-0.24, 0.15, 0))
    
    # Penrose triangle - impossible triangle
    create_penrose_triangle(
        size=45,
        thickness=7,
        beam_width=11
    )
    
    # Impossible cube wireframe
    bpy.ops.transform.translate(value=(0.12, 0, 0))
    create_impossible_cube(
        size=38,
        beam_thickness=6
    )
    
    # Double Möbius strip - even weirder
    bpy.ops.transform.translate(value=(0.24, 0, 0))
    create_mobius_strip(
        radius=30,
        width=14,
        thickness=2,
        subdivisions=64,
        twists=2  # Double twist!
    )
    
    print("Illusion set complete!")

def create_advanced_knots():
    """Create advanced mathematical knots"""
    
    print("Creating Advanced Mathematical Knots...")
    
    # Move to new row
    bpy.ops.transform.translate(value=(-0.36, 0.3, 0))
    
    # Torus knot (3,4) - moderate complexity
    create_torus_knot(
        p=3,
        q=4,
        radius=25,
        tube_radius=5,
        subdivisions=192
    )
    
    # Torus knot (3,5) - classic configuration
    bpy.ops.transform.translate(value=(0.12, 0, 0))
    create_torus_knot(
        p=3,
        q=5,
        radius=22,
        tube_radius=4,
        subdivisions=256
    )
    
    # Torus knot (5,7) - more complex
    bpy.ops.transform.translate(value=(0.24, 0, 0))
    create_torus_knot(
        p=5,
        q=7,
        radius=20,
        tube_radius=3,
        subdivisions=320
    )
    
    print("Advanced knots complete!")

def create_weird_sampler_collection():
    """Create the complete weird objects sampler"""
    
    print("="*50)
    print("VeoGen Weird Objects Sampler")
    print("="*50)
    
    # Clear the scene first
    clear_scene()
    
    # Create three rows of objects
    create_educational_set()
    create_illusion_set() 
    create_advanced_knots()
    
    print("\n" + "="*50)
    print("Weird Objects Sampler Complete!")
    print("="*50)
    print("\nGenerated objects:")
    print("• Möbius Strip (classic & double twist)")
    print("• Klein Bottle")
    print("• Penrose Triangle")
    print("• Impossible Cube")
    print("• Trefoil Knot")
    print("• Torus Knots (3,4), (3,5), (5,7)")
    print("\nPerfect for:")
    print("• Mathematical education")
    print("• Topology demonstrations") 
    print("• 3D printing showcases")
    print("• Conversation starters")
    print("• Mind-bending desk art")
    
    print("\nPrint Settings Recommendations:")
    print("• Layer Height: 0.1-0.2mm for best detail")
    print("• Infill: 15-20% (these are decorative)")
    print("• Support: Usually not needed")
    print("• Material: PLA recommended for display pieces")

def create_single_showcase_object():
    """Create one impressive showcase object"""
    
    print("Creating Single Showcase Object...")
    
    clear_scene()
    
    # Create a large, high-resolution Klein bottle as centerpiece
    create_klein_bottle(
        radius=40,
        height=80,
        thickness=3,
        subdivisions=96  # High resolution
    )
    
    print("Showcase Klein Bottle created!")
    print("This is perfect as a single impressive print.")

# Main execution options
if __name__ == "__main__":
    # Uncomment the version you want to run:
    
    # Full collection (recommended)
    create_weird_sampler_collection()
    
    # Single impressive object
    # create_single_showcase_object()
    
    # Educational set only
    # create_educational_set()
    
    # Illusion objects only
    # create_illusion_set()
    
    # Advanced knots only
    # create_advanced_knots() 