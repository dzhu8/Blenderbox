import os
import sys

# Set the outermost directory to the system path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from create.components import Cylinder
from create.materials import get_material
from inspect_glb import view_trimesh_object

if __name__ == "__main__":  
    # Create a custom light blue glass material
    light_blue_glass = {
        "baseColorFactor": [0.15, 0.45, 0.88, 1.0],
        "metallicFactor": 0.0,
        "roughnessFactor": 0.5,
        "doubleSided": True,  # Changed to True
        "name": "Opaque Light Blue Glass",
    }
    
    # Get other materials with double-sided enabled
    chrome_top = get_material("metal", "chrome")
    chrome_top["doubleSided"] = True
    
    concrete_base = get_material("concrete", "polished")
    concrete_base["doubleSided"] = True
    
    # Create a cylinder with adjusted materials
    glass_tower = Cylinder(
        radius=1.5,
        height=5.0,
        segments=8,
        caps=True,
        side_material=light_blue_glass,
        top_material=chrome_top,
        bottom_material=concrete_base,
    )

    # Visualize the tower with good lighting for glass
    view_trimesh_object(
        glass_tower.get_scene(),  # Use scene to preserve separate materials
        show_wireframe=False,
        background_color=[0.2, 0.2, 0.3, 1.0],  # Dark blue background
        num_lights=8,  # More lights to show glass reflections
        light_intensities=300.0,
    )
