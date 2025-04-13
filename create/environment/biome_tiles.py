"""
This module provides tile implementations for different biome types.

These tiles can be used to create terrain grids, maps, and landscapes.
Each tile is a 4x4 square with a material that represents its biome type.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import trimesh

from create.components import Rectangle
from create.materials import MATERIALS, get_material

# Base dimensions for all biome tiles
DEFAULT_TILE_WIDTH = 4.0
DEFAULT_TILE_LENGTH = 4.0
DEFAULT_TILE_THICKNESS = 0.5


# -----------------------------------------------------------------------------
# Base Biome Tile class
# -----------------------------------------------------------------------------
class BiomeTile:
    """
    Base class for all biome tiles.

    This class creates a simple flat rectangular tile with a specified material
    that represents a particular biome type.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
        material: Optional[Dict[str, Any]] = None,
        name: str = "biome_tile",
    ):
        """
        Initialize a biome tile.

        Args:
            width: Width of the tile along X axis (default: 4.0)
            length: Length of the tile along Z axis (default: 4.0)
            thickness: Thickness/height of the tile (default: 0.5)
            position: [x, y, z] position of the center of the tile (default: [0, 0, 0])
            material: Dictionary of material properties (default: None, uses a default material)
            name: Name identifier for the tile (default: "biome_tile")
        """
        self.width = max(0.01, width)
        self.length = max(0.01, length)
        self.thickness = max(0.01, thickness)
        self.position = position if position else [0.0, 0.0, 0.0]
        self.material = (
            material
            if material
            else {
                "baseColorFactor": [0.8, 0.8, 0.8, 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.9,
                "doubleSided": False,
                "name": "Default Tile Material",
            }
        )
        self.name = name

        # Create the tile mesh
        self.mesh = self._create_tile_mesh()

    def _create_tile_mesh(self) -> trimesh.Trimesh:
        """
        Create the tile mesh.

        Returns:
            A trimesh.Trimesh object representing the tile
        """
        # Use the Rectangle component to create the tile
        # The Rectangle will be facing upward (normal = [0,1,0])
        rect = Rectangle(
            width=self.width,
            length=self.length,
            facing="up",
            position=self.position,
            material=self.material,
            name=self.name,
            thickness=self.thickness,
        )

        return rect.get_mesh()

    def get_mesh(self) -> trimesh.Trimesh:
        """
        Get the tile mesh.

        Returns:
            The tile as a trimesh.Trimesh object
        """
        return self.mesh

    def get_scene(self) -> trimesh.Scene:
        """
        Get the tile as a scene object.

        Returns:
            The tile as a trimesh.Scene object
        """
        scene = trimesh.Scene()
        scene.add_geometry(self.mesh, node_name=self.name)
        return scene

    def update_material(self, material: Dict[str, Any]) -> None:
        """
        Update the material of the tile.

        Args:
            material: Dictionary of material properties
        """
        self.material = material

        # Create and apply new material
        pbr_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=material.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0]),
            metallicFactor=material.get("metallicFactor", 0.0),
            roughnessFactor=material.get("roughnessFactor", 0.0),
            emissiveFactor=material.get("emissiveFactor", [0.0, 0.0, 0.0]),
            doubleSided=material.get("doubleSided", False),
        )

        # Apply to mesh
        self.mesh.visual.material = pbr_material


# -----------------------------------------------------------------------------
# Specific Biome Tile implementations
# -----------------------------------------------------------------------------
class GrassTile(BiomeTile):
    """
    A tile representing a grass biome.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
    ):
        # Create a custom grass material
        grass_material = {
            "baseColorFactor": [0.2, 0.8, 0.2, 1.0],  # Green color for grass
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,  # Grass is quite rough
            "doubleSided": False,
            "name": "Grass Material",
        }

        super().__init__(
            width=width,
            length=length,
            thickness=thickness,
            position=position,
            material=grass_material,
            name="grass_tile",
        )


class DesertTile(BiomeTile):
    """
    A tile representing a desert biome.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
    ):
        # Create a custom desert material
        desert_material = {
            "baseColorFactor": [0.94, 0.87, 0.6, 1.0],  # Sandy color for desert
            "metallicFactor": 0.0,
            "roughnessFactor": 0.85,  # Sand is somewhat rough
            "doubleSided": False,
            "name": "Desert Material",
        }

        super().__init__(
            width=width,
            length=length,
            thickness=thickness,
            position=position,
            material=desert_material,
            name="desert_tile",
        )


class RockTile(BiomeTile):
    """
    A tile representing a rock biome.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
    ):
        # Create a custom rock material
        rock_material = {
            "baseColorFactor": [0.6, 0.6, 0.6, 1.0],  # Gray color for rock
            "metallicFactor": 0.1,
            "roughnessFactor": 0.95,
            "doubleSided": False,
            "name": "Rock Material",
        }

        super().__init__(
            width=width,
            length=length,
            thickness=thickness,
            position=position,
            material=rock_material,
            name="rock_tile",
        )


class SnowTile(BiomeTile):
    """
    A tile representing a snow biome.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
    ):
        # Create a custom snow material
        snow_material = {
            "baseColorFactor": [1.0, 1.0, 1.0, 1.0],  # White color for snow
            "metallicFactor": 0.0,
            "roughnessFactor": 0.3,  # Snow is relatively smooth
            "doubleSided": False,
            "name": "Snow Material",
        }

        super().__init__(
            width=width,
            length=length,
            thickness=thickness,
            position=position,
            material=snow_material,
            name="snow_tile",
        )


class ForestTile(BiomeTile):
    """
    A tile representing a forest biome.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
    ):
        forest_material = {
            "baseColorFactor": [0.15, 0.5, 0.15, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.9,  # Forest ground is rough
            "doubleSided": False,
            "name": "Forest Material",
        }

        super().__init__(
            width=width,
            length=length,
            thickness=thickness,
            position=position,
            material=forest_material,
            name="forest_tile",
        )


class RainforestTile(BiomeTile):
    """
    A tile representing a rainforest biome.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
    ):
        # Create a custom rainforest material
        rainforest_material = {
            "baseColorFactor": [
                0.05,
                0.3,
                0.1,
                1.0,
            ],  # Even darker green color for rainforest
            "metallicFactor": 0.0,
            "roughnessFactor": 0.85,
            "doubleSided": False,
            "name": "Rainforest Material",
        }

        super().__init__(
            width=width,
            length=length,
            thickness=thickness,
            position=position,
            material=rainforest_material,
            name="rainforest_tile",
        )


class PlainsTile(BiomeTile):
    """
    A tile representing a plains biome.
    """

    def __init__(
        self,
        width: float = DEFAULT_TILE_WIDTH,
        length: float = DEFAULT_TILE_LENGTH,
        thickness: float = DEFAULT_TILE_THICKNESS,
        position: Optional[List[float]] = None,
    ):
        # Create a custom plains material
        plains_material = {
            "baseColorFactor": [0.9, 0.85, 0.4, 1.0],  # Wheat-yellow color for plains
            "metallicFactor": 0.0,
            "roughnessFactor": 0.7,  # Plains grass
            "doubleSided": False,
            "name": "Plains Material",
        }

        super().__init__(
            width=width,
            length=length,
            thickness=thickness,
            position=position,
            material=plains_material,
            name="plains_tile",
        )
