import os
import sys

# Set the outermost directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from create.components import Cylinder
from create.materials import get_material
from inspect_glb import view_trimesh_object


if __name__ == "__main__":    # Create a custom light blue glass material
    light_blue_glass = {
        "baseColorFactor": [0.7, 0.85, 1.0, 1.0],  # Light blue - fully opaque (alpha=1.0)
        "metallicFactor": 0.2,  # Slight metallic appearance for reflections
        "roughnessFactor": 0.05,  # Very smooth for glass-like reflections
        "doubleSided": False,  # Single sided for solid appearance
        "name": "Opaque Light Blue Glass"
    }
    
    # Create a cylinder with light blue glass material for the perimeter/sides
    glass_tower = Cylinder(
        radius=1.5,
        height=5.0,
        segments=8,
        caps=True,
        side_material=light_blue_glass,  # Apply glass material to sides only
        top_material=get_material("metal", "chrome"),  # Chrome top cap
        bottom_material=get_material("concrete", "polished")  # Concrete base
    )
    
    # Visualize the tower with good lighting for glass
    view_trimesh_object(
        glass_tower.get_scene(),  # Use scene to preserve separate materials 
        show_wireframe=False,
        background_color=[0.2, 0.2, 0.3, 1.0],  # Dark blue background
        num_lights=5,  # More lights to show glass reflections
        light_intensities=80.0
    )

