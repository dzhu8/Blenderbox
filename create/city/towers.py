import os
import sys

# Set the outermost directory to the system path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from create.components import Cylinder, RectangularPrism
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
        radius=2.5,
        height=5.0,
        segments=16,
        caps=True,
        side_material=light_blue_glass,
        top_material=chrome_top,
        bottom_material=concrete_base,
    )

    # Define materials for the rectangular tower
    dark_green_glass = {
        "baseColorFactor": [0.05, 0.35, 0.15, 1.0],
        "metallicFactor": 0.1,
        "roughnessFactor": 0.3,
        "doubleSided": True,
        "name": "Dark Green Glass",
    }

    copper_top = get_material("metal", "copper")
    copper_top["doubleSided"] = True

    granite_base = get_material("stone", "granite")
    granite_base["doubleSided"] = True

    # Create a rectangular prism tower
    rectangular_tower = RectangularPrism(
        width=4.0,
        height=7.0,
        depth=3.0,
        caps=True,
        side_material=dark_green_glass,
        top_material=copper_top,
        bottom_material=granite_base,
        wall_thickness=0.2,  # Create thicker walls
    )

    # Visualize the cylindrical tower with good lighting for glass
    print("Visualizing cylindrical tower...")
    view_trimesh_object(
        glass_tower.get_scene(),  # Use scene to preserve separate materials
        show_wireframe=False,
        background_color=[0.2, 0.2, 0.3, 1.0],  # Dark blue background
        num_lights=8,  # More lights to show glass reflections
        light_intensities=300.0,
        use_raymond_lighting=True,
    )

    # Visualize the rectangular tower
    print("Visualizing rectangular tower...")
    view_trimesh_object(
        rectangular_tower.get_scene(),  # Use scene to preserve separate materials
        show_wireframe=False,
        background_color=[0.1, 0.1, 0.15, 1.0],  # Darker background for contrast
        num_lights=10,  # More lights to show glass and copper reflections
        light_intensities=350.0,
        use_raymond_lighting=True,
    )
