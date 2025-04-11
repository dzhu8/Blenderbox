"""
Standard material definitions for use throughout the Blenderbox project.

This module provides a set of predefined PBR (Physically Based Rendering) materials
that represent common real-world materials with appropriate attribute values.

Each material is defined as a dictionary with standard PBR parameters:
- baseColorFactor: RGBA color values [r, g, b, a] from 0.0-1.0
- metallicFactor: How metallic the material appears (0.0-1.0)
- roughnessFactor: Micro-surface detail affecting light scatter (0.0-1.0)
- emissiveFactor: Self-illumination [r, g, b] (optional)
- alphaMode: How transparency is handled ("OPAQUE", "MASK", or "BLEND")
- doubleSided: Whether the material is visible from both sides
- name: Descriptive name for the material

Usage example:
    from create.materials import MATERIALS
    
    # Create a glass cylinder
    cylinder = Cylinder(
        radius=1.0,
        height=2.0,
        material=MATERIALS["glass"]["clear"]
    )
    
    # Or create a brick building with stone base
    building = Building(
        width=10.0,
        height=20.0,
        wall_material=MATERIALS["brick"]["red"],
        base_material=MATERIALS["stone"]["granite"]
    )
"""

from typing import Dict, Any

# Dictionary to store all material definitions
MATERIALS: Dict[str, Dict[str, Dict[str, Any]]] = {
    # Metal materials
    "metal": {
        "steel": {
            "baseColorFactor": [0.8, 0.8, 0.9, 1.0],
            "metallicFactor": 0.9,
            "roughnessFactor": 0.2,
            "doubleSided": False,
            "name": "Steel"
        },
        "chrome": {
            "baseColorFactor": [0.9, 0.9, 0.9, 1.0],
            "metallicFactor": 1.0,
            "roughnessFactor": 0.05,
            "doubleSided": False,
            "name": "Chrome"
        },
        "gold": {
            "baseColorFactor": [1.0, 0.76, 0.33, 1.0],
            "metallicFactor": 1.0,
            "roughnessFactor": 0.12,
            "doubleSided": False,
            "name": "Gold"
        },
        "copper": {
            "baseColorFactor": [0.95, 0.64, 0.54, 1.0],
            "metallicFactor": 1.0,
            "roughnessFactor": 0.15,
            "doubleSided": False,
            "name": "Copper"
        },
        "brass": {
            "baseColorFactor": [0.88, 0.78, 0.5, 1.0],
            "metallicFactor": 0.9,
            "roughnessFactor": 0.2,
            "doubleSided": False,
            "name": "Brass"
        },
        "aluminum": {
            "baseColorFactor": [0.91, 0.92, 0.93, 1.0],
            "metallicFactor": 0.95,
            "roughnessFactor": 0.15,
            "doubleSided": False,
            "name": "Aluminum"
        },
        "rusted": {
            "baseColorFactor": [0.7, 0.3, 0.2, 1.0],
            "metallicFactor": 0.6,
            "roughnessFactor": 0.8,
            "doubleSided": False,
            "name": "Rusted Metal"
        },
    },
      # Glass materials
    "glass": {
        "clear": {
            "baseColorFactor": [0.9, 0.9, 0.9, 0.3],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.05,
            "alphaMode": "BLEND",
            "doubleSided": True,
            "name": "Clear Glass"
        },
        "tinted": {
            "baseColorFactor": [0.1, 0.3, 0.5, 0.5],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.05,
            "alphaMode": "BLEND",
            "doubleSided": True,
            "name": "Tinted Glass"
        },
        "frosted": {
            "baseColorFactor": [0.9, 0.9, 0.9, 0.7],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.4,
            "alphaMode": "BLEND",
            "doubleSided": True,
            "name": "Frosted Glass"
        },
        "green": {
            "baseColorFactor": [0.3, 0.8, 0.5, 0.4],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.05,
            "alphaMode": "BLEND",
            "doubleSided": True,
            "name": "Green Glass"
        },
        "opaque_blue": {
            "baseColorFactor": [0.7, 0.85, 1.0, 1.0],
            "metallicFactor": 0.2,
            "roughnessFactor": 0.05,
            "doubleSided": False,
            "name": "Opaque Blue Glass"
        },
        "opaque_clear": {
            "baseColorFactor": [0.95, 0.95, 1.0, 1.0],
            "metallicFactor": 0.3,
            "roughnessFactor": 0.05,
            "doubleSided": False,
            "name": "Opaque Clear Glass"
        },
    },
    
    # Stone materials
    "stone": {
        "granite": {
            "baseColorFactor": [0.7, 0.7, 0.7, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,
            "doubleSided": False,
            "name": "Granite"
        },
        "marble": {
            "baseColorFactor": [0.9, 0.9, 0.9, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.3,
            "doubleSided": False,
            "name": "Marble"
        },
        "sandstone": {
            "baseColorFactor": [0.94, 0.86, 0.69, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8,
            "doubleSided": False,
            "name": "Sandstone"
        },
        "limestone": {
            "baseColorFactor": [0.85, 0.82, 0.75, 1.0], 
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,
            "doubleSided": False,
            "name": "Limestone"
        },
        "slate": {
            "baseColorFactor": [0.3, 0.3, 0.35, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.6,
            "doubleSided": False,
            "name": "Slate"
        },
    },
    
    # Brick materials
    "brick": {
        "red": {
            "baseColorFactor": [0.75, 0.3, 0.2, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.85,
            "doubleSided": False,
            "name": "Red Brick"
        },
        "tan": {
            "baseColorFactor": [0.85, 0.75, 0.6, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8,
            "doubleSided": False,
            "name": "Tan Brick"
        },
        "brown": {
            "baseColorFactor": [0.5, 0.35, 0.25, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8,
            "doubleSided": False,
            "name": "Brown Brick"
        },
        "clinker": {
            "baseColorFactor": [0.3, 0.2, 0.2, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,
            "doubleSided": False,
            "name": "Clinker Brick"
        },
    },
    
    # Concrete materials
    "concrete": {
        "smooth": {
            "baseColorFactor": [0.7, 0.7, 0.7, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,
            "doubleSided": False,
            "name": "Smooth Concrete"
        },
        "rough": {
            "baseColorFactor": [0.65, 0.65, 0.65, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,
            "doubleSided": False,
            "name": "Rough Concrete"
        },
        "polished": {
            "baseColorFactor": [0.75, 0.75, 0.75, 1.0],
            "metallicFactor": 0.05,
            "roughnessFactor": 0.3,
            "doubleSided": False,
            "name": "Polished Concrete"
        },
    },
    
    # Stucco materials
    "stucco": {
        "white": {
            "baseColorFactor": [0.9, 0.9, 0.9, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8,
            "doubleSided": False,
            "name": "White Stucco"
        },
        "beige": {
            "baseColorFactor": [0.85, 0.8, 0.7, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8,
            "doubleSided": False,
            "name": "Beige Stucco"
        },
        "pink": {
            "baseColorFactor": [0.95, 0.8, 0.8, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,
            "doubleSided": False,
            "name": "Pink Stucco"
        },
    },
    
    # Wood materials
    "wood": {
        "oak": {
            "baseColorFactor": [0.7, 0.5, 0.3, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.6,
            "doubleSided": False,
            "name": "Oak Wood"
        },
        "pine": {
            "baseColorFactor": [0.85, 0.7, 0.45, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,
            "doubleSided": False,
            "name": "Pine Wood"
        },
        "mahogany": {
            "baseColorFactor": [0.5, 0.25, 0.15, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.5,
            "doubleSided": False,
            "name": "Mahogany Wood"
        },
        "walnut": {
            "baseColorFactor": [0.4, 0.3, 0.2, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.6,
            "doubleSided": False,
            "name": "Walnut Wood"
        },
        "weathered": {
            "baseColorFactor": [0.6, 0.55, 0.5, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,
            "doubleSided": False,
            "name": "Weathered Wood"
        },
    },
    
    # Plastic materials
    "plastic": {
        "smooth": {
            "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.3,
            "doubleSided": False,
            "name": "Smooth Plastic"
        },
        "rough": {
            "baseColorFactor": [0.9, 0.9, 0.9, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,
            "doubleSided": False,
            "name": "Rough Plastic"
        },
        "glossy_red": {
            "baseColorFactor": [0.8, 0.1, 0.1, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.2,
            "doubleSided": False,
            "name": "Glossy Red Plastic"
        },
        "matte_black": {
            "baseColorFactor": [0.05, 0.05, 0.05, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,
            "doubleSided": False,
            "name": "Matte Black Plastic"
        },
    },
    
    # Fabric materials
    "fabric": {
        "cotton": {
            "baseColorFactor": [0.9, 0.9, 0.85, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.95,
            "doubleSided": True,
            "name": "Cotton Fabric"
        },
        "denim": {
            "baseColorFactor": [0.25, 0.35, 0.5, 1.0],
            "metallicFactor": 0.0, 
            "roughnessFactor": 0.9,
            "doubleSided": True,
            "name": "Denim Fabric"
        },
        "leather": {
            "baseColorFactor": [0.4, 0.3, 0.2, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,
            "doubleSided": True,
            "name": "Leather"
        },
        "silk": {
            "baseColorFactor": [0.9, 0.9, 0.9, 1.0],
            "metallicFactor": 0.1,
            "roughnessFactor": 0.3,
            "doubleSided": True,
            "name": "Silk Fabric"
        },
    },
    
    # Terra cotta materials
    "terracotta": {
        "clay": {
            "baseColorFactor": [0.85, 0.5, 0.3, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8,
            "doubleSided": False,
            "name": "Terra Cotta Clay"
        },
        "roof_tile": {
            "baseColorFactor": [0.75, 0.45, 0.3, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.85,
            "doubleSided": False,
            "name": "Terra Cotta Roof Tile"
        },
    },
    
    # Water and liquid materials
    "water": {
        "clear": {
            "baseColorFactor": [0.2, 0.5, 0.8, 0.6],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.05,
            "alphaMode": "BLEND",
            "doubleSided": True,
            "name": "Clear Water"
        },
        "murky": {
            "baseColorFactor": [0.2, 0.4, 0.4, 0.8],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.1,
            "alphaMode": "BLEND",
            "doubleSided": True,
            "name": "Murky Water"
        },
    },
    
    # Asphalt and pavement materials
    "pavement": {
        "asphalt": {
            "baseColorFactor": [0.1, 0.1, 0.1, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,
            "doubleSided": False,
            "name": "Asphalt"
        },
        "concrete_sidewalk": {
            "baseColorFactor": [0.8, 0.8, 0.8, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.85,
            "doubleSided": False,
            "name": "Concrete Sidewalk"
        },
        "cobblestone": {
            "baseColorFactor": [0.5, 0.5, 0.5, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,
            "doubleSided": False,
            "name": "Cobblestone"
        },
    },
    
    # Special materials
    "emissive": {
        "white": {
            "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.4,
            "emissiveFactor": [1.0, 1.0, 1.0],
            "doubleSided": False,
            "name": "White Light"
        },
        "warm": {
            "baseColorFactor": [1.0, 0.9, 0.7, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.4,
            "emissiveFactor": [1.0, 0.9, 0.7],
            "doubleSided": False,
            "name": "Warm Light"
        },
        "cool": {
            "baseColorFactor": [0.7, 0.8, 1.0, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.4,
            "emissiveFactor": [0.7, 0.8, 1.0],
            "doubleSided": False,
            "name": "Cool Light"
        },
        "neon_blue": {
            "baseColorFactor": [0.0, 0.8, 1.0, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.3,
            "emissiveFactor": [0.0, 0.8, 1.0],
            "doubleSided": False,
            "name": "Neon Blue"
        },
        "neon_red": {
            "baseColorFactor": [1.0, 0.1, 0.1, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.3,
            "emissiveFactor": [1.0, 0.1, 0.1],
            "doubleSided": False,
            "name": "Neon Red"
        },
    },
}

# Function to get a copy of a material to avoid modifying the original
def get_material(category: str, material_name: str) -> Dict[str, Any]:
    """
    Get a copy of a material from the materials library.
    
    Args:
        category: The material category (e.g., "metal", "glass", "brick")
        material_name: The specific material name within the category
    
    Returns:
        A dictionary containing the material properties
        
    Raises:
        KeyError: If the specified category or material name doesn't exist
    """
    try:
        # Return a copy to avoid modifying the original
        return dict(MATERIALS[category][material_name])
    except KeyError:
        valid_categories = list(MATERIALS.keys())
        if category in MATERIALS:
            valid_materials = list(MATERIALS[category].keys())
            raise KeyError(f"Material '{material_name}' not found in category '{category}'. "
                         f"Valid materials are: {valid_materials}")
        else:
            raise KeyError(f"Category '{category}' not found. "
                         f"Valid categories are: {valid_categories}")
