# PBRMaterial (Physically Based Rendering Material) Attributes Reference
# -----------------------------------------------------------------------------
#
# === Core PBR Parameters ===
#
# baseColorFactor: RGBA[float]
#   - The base color of the material, defined as an RGBA array: [red, green, blue, alpha]
#   - Values range from 0.0-1.0 (can be converted from 0-255 scale by dividing by 255)
#   - Alpha (4th value) controls opacity when alphaMode is set to "BLEND"
#
# metallicFactor: float
#   - How metallic the material appears (0.0 = non-metallic, 1.0 = fully metallic)
#   - Non-metals (0.0) reflect light equally in all directions (diffuse reflection)
#   - Metals (1.0) reflect light mostly in the mirror direction (specular reflection)
#   - Affects how the material reflects light and environment
#   - Most real-world materials are either fully metallic (1.0) or non-metallic (0.0)
#
# roughnessFactor: float
#   - Controls the microsurface detail which affects light scattering
#   - Range: 0.0 (perfectly smooth, mirror-like) to 1.0 (completely rough, diffuse)
#   - Lower values (0.0-0.3) = shinier, more focused reflections
#   - Higher values (0.7-1.0) = more matte appearance, blurrier reflections
#   - Glass typically uses very low values (0.0-0.1)
#   - Polished metals use low-to-medium values (0.1-0.4)
#
# === Additional Material Properties ===
#
# emissiveFactor: RGB[float]
#   - Self-illumination color as RGB array: [red, green, blue]
#   - Makes the material appear to emit light (does not actually illuminate other objects)
#   - Values typically range from 0.0-1.0, but can be higher for stronger emission
#   - [0,0,0] means no emission (default for non-glowing materials)
#
# alphaMode: string
#   - Defines how transparency is handled. Options:
#     - "OPAQUE": No transparency (default)
#     - "MASK": Binary transparency (pixels are either fully opaque or invisible) using alphaCutoff
#     - "BLEND": Smooth transparency based on alpha channel in baseColorFactor
#
# alphaCutoff: float
#   - Threshold value for "MASK" alphaMode (default is typically 0.5)
#   - Pixels with alpha below this value are discarded entirely
#
# doubleSided: boolean
#   - When true, the material is visible from both sides
#   - When false, only the front faces are visible (back faces are culled)
#   - Important for thin surfaces like leaves, paper, or glass
#
# === Texture Maps ===
#
# baseColorTexture: Texture
#   - Image texture that defines the base color across the surface
#   - Multiplied by baseColorFactor to get the final base color
#
# metallicRoughnessTexture: Texture
#   - Combined texture map where:
#     - Blue channel (B) defines metallic areas
#     - Green channel (G) defines roughness
#   - Values in this texture are multiplied by metallicFactor and roughnessFactor
#
# normalTexture: Texture
#   - Defines surface detail (bumps, dents) without using extra geometry
#   - RGB values represent XYZ normal vector deviations
#
# occlusionTexture: Texture
#   - Defines areas of the surface that are occluded from indirect lighting
#   - Typically used to fake ambient shadows in crevices
#
# emissiveTexture: Texture
#   - Defines which areas of the surface should emit light
#   - Multiplied by emissiveFactor to get final emission
#
# === Special Properties ===
#
# name: string
#   - Optional descriptive name for the material
#   - No visual effect, but useful for organization
#
# ior: float (Index of Refraction)
#   - Defines how light bends when entering/exiting the material
#   - Only relevant for transparent materials
#   - Typical values: glass (1.45-1.55), water (1.33), diamond (2.42)
#   - Not part of standard glTF but supported by some renderers
#
# -----------------------------------------------------------------------------
# Material Type Guide:
#
# Glass:        metallicFactor=0.0, roughnessFactor=0.0-0.05, alphaMode="BLEND", baseColorFactor alpha=0.2-0.5
# Metals:       metallicFactor=1.0, roughnessFactor varies (0.0-0.6), baseColor determines the metal type
# Plastics:     metallicFactor=0.0, roughnessFactor=0.3-0.7
# Cloth:        metallicFactor=0.0, roughnessFactor=0.7-1.0
# Skin:         metallicFactor=0.0, roughnessFactor=0.5-0.7
# Wood:         metallicFactor=0.0, roughnessFactor=0.5-0.9
# Stone:        metallicFactor=0.0, roughnessFactor=0.4-0.9
# Liquids:      metallicFactor=0.0, roughnessFactor=0.0-0.2, alphaMode="BLEND"
# -----------------------------------------------------------------------------

import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import trimesh

# -----------------------------------------------------------------------------
# Default material to use across all classes if none is provided
# -----------------------------------------------------------------------------
DEFAULT_MATERIAL = {
    "baseColorFactor": [0.8, 0.8, 0.8, 0.0],
    "metallicFactor": 0.0,
    "roughnessFactor": 0.0,
    "doubleSided": False,
    "name": "DefaultMaterial",
}


# -----------------------------------------------------------------------------
# Attributes for standard building materials
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Circular cap building block
# -----------------------------------------------------------------------------
class Circle:
    """
    A class for creating circular shapes.

    This can be used independently or as a component in more complex shapes
    like cylinder caps, cones, or other geometric primitives.

    Specify:
    - radius: The radius of the circle
    - segments: The number of segments around the circle's perimeter
    - facing: The direction the circle faces ('up', 'down', or a custom vector)
    - position: The center position of the circle
    """

    def __init__(
        self,
        radius: float = 1.0,
        segments: int = 16,
        facing: Union[str, List[float]] = "up",
        position: Optional[List[float]] = None,
        material: Optional[Dict[str, Any]] = None,
        name: str = "circle",
        thickness: Optional[float] = None,
    ):
        """
        Initialize a circle object.

        Args:
            radius: Radius of the circle (default: 1.0)
            segments: Number of segments around the circle's perimeter (default: 16)
            facing: Direction the circle faces - 'up' (+Y), 'down' (-Y), or a custom [x,y,z] vector
                    (default: 'up')
            position: [x, y, z] position of the center of the circle (default: [0, 0, 0])
            material: Dictionary of material properties (default: None, which uses DEFAULT_MATERIAL)
            name: Name identifier for the circle object (default: "circle")
            thickness: Thickness of the circle in the normal direction (default: None)
                      If provided, creates a 3D disk with the specified thickness.
                      If None, defaults to 1% of the radius (0.01 * radius)
        """
        self.radius = max(0.01, radius)  # Ensure minimum valid radius
        self.segments = max(3, segments)  # Minimum 3 segments required for a valid mesh
        self.position = position if position else [0.0, 0.0, 0.0]
        self.name = name

        # Set default thickness to 1% of radius if not specified
        self.thickness = thickness if thickness is not None else 0.01 * self.radius

        # Set material
        self.material = material if material else DEFAULT_MATERIAL

        # Handle the facing direction
        if facing == "up":
            self.normal = [0.0, 1.0, 0.0]  # Y+ direction
            self.reverse_winding = False
        elif facing == "down":
            self.normal = [0.0, -1.0, 0.0]  # Y- direction
            self.reverse_winding = True
        else:
            # Custom direction - normalize it
            self.normal = self._normalize_vector(facing)

            # If the normal points more downward than upward, reverse winding
            self.reverse_winding = self.normal[1] < 0

        # Create the mesh
        self.mesh = self._create_circle_mesh()

    def _normalize_vector(self, vec: List[float]) -> List[float]:
        """Normalize a vector to unit length"""
        length = math.sqrt(sum(x * x for x in vec))
        if length < 1e-6:  # Avoid division by zero
            return [0.0, 1.0, 0.0]  # Default to up if input is a zero vector
        return [x / length for x in vec]

    def _create_circle_mesh(self) -> trimesh.Trimesh:
        """
        Create the circle mesh with the specified parameters.
        If thickness is set, creates a 3D disk instead of a flat circle.

        Returns:
            A trimesh.Trimesh object representing the circle or disk
        """
        if self.thickness <= 0:
            # If thickness is zero or negative, create a flat circle (original behavior)
            return self._create_flat_circle_mesh()
        else:
            # Otherwise create a 3D disk with thickness
            return self._create_3d_disk_mesh()

    def _create_flat_circle_mesh(self) -> trimesh.Trimesh:
        """
        Create a flat circle mesh (2D).

        Returns:
            A trimesh.Trimesh object representing a flat circle
        """
        # Create the vertices for the circle
        vertices = []

        # Add center point first
        vertices.append([0.0, 0.0, 0.0])  # Center at local origin

        # Add perimeter vertices
        for i in range(self.segments):
            angle = 2.0 * math.pi * i / self.segments
            x = self.radius * math.cos(angle)
            z = self.radius * math.sin(angle)
            vertices.append([x, 0.0, z])

        # Create faces for the circle
        faces = []
        for i in range(self.segments):
            # Current perimeter vertex
            curr_idx = i + 1
            # Next perimeter vertex (wrap around)
            next_idx = (i + 1) % self.segments + 1

            if self.reverse_winding:
                # For downward-facing circles, reverse triangle orientation
                faces.append([0, next_idx, curr_idx])
            else:
                # For upward-facing circles
                faces.append([0, curr_idx, next_idx])  # Create the mesh
        circle_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        return circle_mesh

    def _create_3d_disk_mesh(self) -> trimesh.Trimesh:
        """
        Create a 3D disk mesh with the specified thickness.

        Returns:
            A trimesh.Trimesh object representing a 3D disk
        """
        # Calculate half thickness for top and bottom faces
        half_thickness = self.thickness / 2.0

        vertices = []

        # Create top face vertices (including center)
        top_center_idx = len(vertices)
        vertices.append([0.0, half_thickness, 0.0])  # Top center

        top_perimeter_start_idx = len(vertices)
        for i in range(self.segments):
            angle = 2.0 * math.pi * i / self.segments
            x = self.radius * math.cos(angle)
            z = self.radius * math.sin(angle)
            vertices.append([x, half_thickness, z])  # Top perimeter

        # Create bottom face vertices (including center)
        bottom_center_idx = len(vertices)
        vertices.append([0.0, -half_thickness, 0.0])  # Bottom center

        bottom_perimeter_start_idx = len(vertices)
        for i in range(self.segments):
            angle = 2.0 * math.pi * i / self.segments
            x = self.radius * math.cos(angle)
            z = self.radius * math.sin(angle)
            vertices.append([x, -half_thickness, z])  # Bottom perimeter

        faces = []

        # Create top face triangles
        for i in range(self.segments):
            curr_idx = top_perimeter_start_idx + i
            next_idx = top_perimeter_start_idx + (i + 1) % self.segments

            if self.reverse_winding:
                faces.append([top_center_idx, next_idx, curr_idx])
            else:
                faces.append([top_center_idx, curr_idx, next_idx])

        # Create bottom face triangles
        for i in range(self.segments):
            curr_idx = bottom_perimeter_start_idx + i
            next_idx = bottom_perimeter_start_idx + (i + 1) % self.segments

            if self.reverse_winding:
                faces.append([bottom_center_idx, curr_idx, next_idx])
            else:
                faces.append([bottom_center_idx, next_idx, curr_idx])

        # Create side faces (connecting top and bottom perimeters)
        for i in range(self.segments):
            top_curr = top_perimeter_start_idx + i
            top_next = top_perimeter_start_idx + (i + 1) % self.segments
            bottom_curr = bottom_perimeter_start_idx + i
            bottom_next = bottom_perimeter_start_idx + (i + 1) % self.segments

            # Add two triangles to form a quad for each side segment
            faces.append([top_curr, bottom_curr, top_next])
            faces.append([bottom_curr, bottom_next, top_next])

        # Create the mesh
        disk_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Apply material
        pbr_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=self.material.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0]),
            metallicFactor=self.material.get("metallicFactor", 0.0),
            roughnessFactor=self.material.get("roughnessFactor", 0.0),
            emissiveFactor=self.material.get("emissiveFactor", [0.0, 0.0, 0.0]),
            doubleSided=self.material.get("doubleSided", False),
        )

        # Apply material to mesh
        disk_mesh.visual.material = pbr_material

        # Apply transformation to align with the specified normal and position
        # First create a transformation that aligns with the normal vector
        if self.normal != [0.0, 1.0, 0.0]:  # If not already facing up
            # Find rotation from [0,1,0] to self.normal
            up = np.array([0.0, 1.0, 0.0])
            normal_vec = np.array(self.normal)

            # Calculate rotation axis and angle
            axis = np.cross(up, normal_vec)
            axis_length = np.linalg.norm(axis)

            if axis_length > 1e-6:  # If cross product is not zero
                axis = axis / axis_length
                angle = np.arccos(np.dot(up, normal_vec))

                # Create rotation matrix
                R = trimesh.transformations.rotation_matrix(angle, axis)
                disk_mesh.apply_transform(R)

        # Apply position offset
        if self.position != [0.0, 0.0, 0.0]:
            T = np.eye(4)
            T[:3, 3] = self.position
            disk_mesh.apply_transform(T)

        return disk_mesh

    def get_mesh(self) -> trimesh.Trimesh:
        """
        Get the circle mesh object.

        Returns:
            The circle as a trimesh.Trimesh object
        """
        return self.mesh

    def get_scene(self) -> trimesh.Scene:
        """
        Get the circle as a scene object.

        Returns:
            The circle as a trimesh.Scene object
        """
        scene = trimesh.Scene()
        scene.add_geometry(self.mesh, node_name=self.name)
        return scene

    def update_material(self, material: Dict[str, Any]) -> None:
        """
        Update the material of the circle.

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
# Cylindrical base building block
# -----------------------------------------------------------------------------
class Cylinder:
    """
    A class for creating customizable cylindrical objects with rectangular border segments.

    Specify:
    - radius: The radius of the cylinder
    - height: The height of the cylinder
    - segments: The number of rectangular segments around the border

    Additional options include:
    - material properties
    - position/orientation
    - caps (whether to include top and bottom faces)

    Qualities- the cylinder features:
    - three meshes: the top, bottom and perimeter meshes, allowing for each of these three
    surfaces to be assigned different materials (or be replaced by slightly different components).
    """

    def __init__(
        self,
        radius: float = 1.0,
        height: float = 2.0,
        segments: int = 16,
        caps: bool = True,
        position: Optional[List[float]] = None,
        material: Optional[Dict[str, Any]] = None,
        side_material: Optional[Dict[str, Any]] = None,
        top_material: Optional[Dict[str, Any]] = None,
        bottom_material: Optional[Dict[str, Any]] = None,
        name: str = "cylinder",
        thickness: Optional[float] = None,
    ):
        """
        Initialize a cylinder object.

        Args:
            radius: Radius of the cylinder (default: 1.0)
            height: Height of the cylinder (default: 2.0)
            segments: Number of rectangular segments around the border (default: 16)
            caps: Whether to include top and bottom circular caps (default: True)
            position: [x, y, z] position of the center of the cylinder (default: [0, 0, 0])
            material: Dictionary of material properties for all parts (default: None, uses DEFAULT_MATERIAL)
            side_material: Material for cylinder sides (default: None, uses material or DEFAULT_MATERIAL)
            top_material: Material for top cap (default: None, uses material or DEFAULT_MATERIAL)
            bottom_material: Material for bottom cap (default: None, uses material or DEFAULT_MATERIAL)
            name: Name identifier for the cylinder object (default: "cylinder")
            thickness: Thickness of the cylinder wall (default: None)
                      If provided, creates a solid cylinder with the specified wall thickness.
                      If None, defaults to 1% of the height (0.01 * height)
        """
        self.radius = max(0.01, radius)  # Ensure minimum valid radius
        self.height = max(0.01, height)  # Ensure minimum valid height
        self.segments = max(3, segments)  # Minimum 3 segments required for a valid mesh
        self.caps = caps
        self.position = position if position else [0.0, 0.0, 0.0]
        self.name = name

        # Set default thickness to 1% of height if not specified
        self.thickness = thickness if thickness is not None else 0.01 * self.height

        # Set default material if none provided
        self.material = material if material else DEFAULT_MATERIAL

        # Set materials for different parts, falling back to the main material if not specified
        self.side_material = side_material if side_material else self.material
        self.top_material = top_material if top_material else self.material
        self.bottom_material = bottom_material if bottom_material else self.material

        # Create the mesh components
        self._create_cylinder_meshes()

        # Store a reference to the combined mesh for backwards compatibility
        self.mesh = self.get_mesh()

    def _create_cylinder_meshes(self) -> None:
        """
        Create separate mesh components for the cylinder sides, top, and bottom.
        Each part can have its own material.
        """
        # Create the side mesh (perimeter)
        self.side_mesh = self._create_side_mesh()

        # Create cap meshes if requested
        self.top_mesh = self._create_top_cap_mesh() if self.caps else None
        self.bottom_mesh = self._create_bottom_cap_mesh() if self.caps else None

        # Apply transformation to all components if needed
        if self.position != [0.0, 0.0, 0.0]:
            T = np.eye(4)
            T[:3, 3] = self.position

            self.side_mesh.apply_transform(T)
            if self.top_mesh:
                self.top_mesh.apply_transform(T)
            if self.bottom_mesh:
                self.bottom_mesh.apply_transform(T)

    def _create_side_mesh(self) -> trimesh.Trimesh:
        """
        Create the cylinder side (perimeter) mesh with its material.
        If thickness is greater than 0, creates a solid wall with inner and outer surfaces.

        Returns:
            A trimesh.Trimesh object representing the cylinder sides
        """
        if self.thickness <= 0 or self.thickness >= self.radius:
            # If no thickness or thickness too large, create a standard hollow cylinder (original behavior)
            return self._create_hollow_side_mesh()
        else:
            # Otherwise create a solid wall with thickness
            return self._create_solid_side_mesh()

    def _create_hollow_side_mesh(self) -> trimesh.Trimesh:
        """
        Create a hollow cylinder side mesh with beveled edges between segments.

        Returns:
            A trimesh.Trimesh object representing the hollow cylinder sides with beveled segment edges
        """
        # Create vertices for the cylinder wall
        vertices = []

        # Define bevel size as a fraction of the segment angle
        bevel_fraction = 0.01  
        segment_angle = 2.0 * math.pi / self.segments
        bevel_angle = segment_angle * bevel_fraction
        
        # Each segment now has a main face and two beveled edges
        for i in range(self.segments):
            # Calculate angles for this segment
            main_start_angle = i * segment_angle + bevel_angle
            main_end_angle = (i + 1) * segment_angle - bevel_angle
            
            # Left bevel start angle (end of previous segment's main part)
            left_start_angle = i * segment_angle - bevel_angle if i > 0 else (self.segments - 1) * segment_angle - bevel_angle
            left_end_angle = i * segment_angle + bevel_angle
            
            # Right bevel start angle (end of this segment's main part)
            right_start_angle = (i + 1) * segment_angle - bevel_angle
            right_end_angle = (i + 1) * segment_angle + bevel_angle if i < self.segments - 1 else bevel_angle
            
            # ----- Main face vertices -----
            # Bottom-left corner (main face)
            x = self.radius * math.cos(main_start_angle)
            z = self.radius * math.sin(main_start_angle)
            vertices.append([x, -self.height / 2, z])
            
            # Top-left corner (main face)
            vertices.append([x, self.height / 2, z])
            
            # Top-right corner (main face)
            x = self.radius * math.cos(main_end_angle)
            z = self.radius * math.sin(main_end_angle)
            vertices.append([x, self.height / 2, z])
            
            # Bottom-right corner (main face)
            vertices.append([x, -self.height / 2, z])
            
            # ----- Left bevel face vertices -----
            # Bottom-left corner (left bevel)
            x = self.radius * math.cos(left_start_angle)
            z = self.radius * math.sin(left_start_angle)
            vertices.append([x, -self.height / 2, z])
            
            # Top-left corner (left bevel)
            vertices.append([x, self.height / 2, z])
            
            # Top-right corner (left bevel)
            x = self.radius * math.cos(left_end_angle)
            z = self.radius * math.sin(left_end_angle)
            vertices.append([x, self.height / 2, z])
            
            # Bottom-right corner (left bevel)
            vertices.append([x, -self.height / 2, z])
            
            # ----- Right bevel face vertices -----
            # Bottom-left corner (right bevel)
            x = self.radius * math.cos(right_start_angle)
            z = self.radius * math.sin(right_start_angle)
            vertices.append([x, -self.height / 2, z])
            
            # Top-left corner (right bevel)
            vertices.append([x, self.height / 2, z])
            
            # Top-right corner (right bevel)
            x = self.radius * math.cos(right_end_angle)
            z = self.radius * math.sin(right_end_angle)
            vertices.append([x, self.height / 2, z])
            
            # Bottom-right corner (right bevel)
            vertices.append([x, -self.height / 2, z])

        # Create faces for the cylinder wall
        faces = []
        for i in range(self.segments):
            # For each segment, we have a main face and two bevels, each with 4 vertices
            base_idx = i * 12  # 12 vertices per segment (4 main + 4 left bevel + 4 right bevel)
            
            # Main face triangles
            main_bl = base_idx      # main bottom-left
            main_tl = base_idx + 1  # main top-left
            main_tr = base_idx + 2  # main top-right
            main_br = base_idx + 3  # main bottom-right
            
            faces.append([main_bl, main_br, main_tl])  # First triangle
            faces.append([main_tl, main_br, main_tr])  # Second triangle
            
            # Left bevel triangles
            left_bl = base_idx + 4  # left bevel bottom-left
            left_tl = base_idx + 5  # left bevel top-left
            left_tr = base_idx + 6  # left bevel top-right
            left_br = base_idx + 7  # left bevel bottom-right
            
            faces.append([left_bl, left_br, left_tl])  # First triangle
            faces.append([left_tl, left_br, left_tr])  # Second triangle
            
            # Right bevel triangles
            right_bl = base_idx + 8   # right bevel bottom-left
            right_tl = base_idx + 9   # right bevel top-left
            right_tr = base_idx + 10  # right bevel top-right
            right_br = base_idx + 11  # right bevel bottom-right
            
            faces.append([right_bl, right_br, right_tl])  # First triangle
            faces.append([right_tl, right_br, right_tr])  # Second triangle
            
        # Create the mesh
        side_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Apply material
        pbr_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=self.side_material.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0]),
            metallicFactor=self.side_material.get("metallicFactor", 0.0),
            roughnessFactor=self.side_material.get("roughnessFactor", 0.0),
            emissiveFactor=self.side_material.get("emissiveFactor", [0.0, 0.0, 0.0]),
            doubleSided=self.side_material.get("doubleSided", False),
        )
        
        # Apply material to mesh
        side_mesh.visual.material = pbr_material
        return side_mesh    
    
    def _create_solid_side_mesh(self) -> trimesh.Trimesh:
        """
        Create a solid cylinder side mesh with thickness and beveled edges between segments.

        Returns:
            A trimesh.Trimesh object representing the solid cylinder sides with beveled edges
        """
        # Calculate inner radius by subtracting thickness
        inner_radius = max(0.001, self.radius - self.thickness)

        # Define bevel size as a fraction of the segment angle
        bevel_fraction = 0.01
        segment_angle = 2.0 * math.pi / self.segments
        bevel_angle = segment_angle * bevel_fraction
        
        vertices = []
        
        # Each segment now has a main face and two beveled edges, both for outer and inner surfaces
        for i in range(self.segments):
            # Calculate angles for this segment
            main_start_angle = i * segment_angle + bevel_angle
            main_end_angle = (i + 1) * segment_angle - bevel_angle
            
            # Left bevel start angle (end of previous segment's main part)
            left_start_angle = i * segment_angle - bevel_angle if i > 0 else (self.segments - 1) * segment_angle - bevel_angle
            left_end_angle = i * segment_angle + bevel_angle
            
            # Right bevel start angle (end of this segment's main part)
            right_start_angle = (i + 1) * segment_angle - bevel_angle
            right_end_angle = (i + 1) * segment_angle + bevel_angle if i < self.segments - 1 else bevel_angle
            
            # ----- OUTER SURFACE VERTICES -----
            
            # ----- Main face vertices (outer) -----
            # Bottom-left corner (main face)
            x = self.radius * math.cos(main_start_angle)
            z = self.radius * math.sin(main_start_angle)
            vertices.append([x, -self.height / 2, z])  # 0: outer main bottom-left
            
            # Top-left corner (main face)
            vertices.append([x, self.height / 2, z])   # 1: outer main top-left
            
            # Top-right corner (main face)
            x = self.radius * math.cos(main_end_angle)
            z = self.radius * math.sin(main_end_angle)
            vertices.append([x, self.height / 2, z])   # 2: outer main top-right
            
            # Bottom-right corner (main face)
            vertices.append([x, -self.height / 2, z])  # 3: outer main bottom-right
            
            # ----- Left bevel face vertices (outer) -----
            # Bottom-left corner (left bevel)
            x = self.radius * math.cos(left_start_angle)
            z = self.radius * math.sin(left_start_angle)
            vertices.append([x, -self.height / 2, z])  # 4: outer left bevel bottom-left
            
            # Top-left corner (left bevel)
            vertices.append([x, self.height / 2, z])   # 5: outer left bevel top-left
            
            # Top-right corner (left bevel)
            x = self.radius * math.cos(left_end_angle)
            z = self.radius * math.sin(left_end_angle)
            vertices.append([x, self.height / 2, z])   # 6: outer left bevel top-right
            
            # Bottom-right corner (left bevel)
            vertices.append([x, -self.height / 2, z])  # 7: outer left bevel bottom-right
            
            # ----- Right bevel face vertices (outer) -----
            # Bottom-left corner (right bevel)
            x = self.radius * math.cos(right_start_angle)
            z = self.radius * math.sin(right_start_angle)
            vertices.append([x, -self.height / 2, z])  # 8: outer right bevel bottom-left
            
            # Top-left corner (right bevel)
            vertices.append([x, self.height / 2, z])   # 9: outer right bevel top-left
            
            # Top-right corner (right bevel)
            x = self.radius * math.cos(right_end_angle)
            z = self.radius * math.sin(right_end_angle)
            vertices.append([x, self.height / 2, z])   # 10: outer right bevel top-right
            
            # Bottom-right corner (right bevel)
            vertices.append([x, -self.height / 2, z])  # 11: outer right bevel bottom-right
            
            # ----- INNER SURFACE VERTICES -----
            
            # ----- Main face vertices (inner) -----
            # Bottom-left corner (main face)
            x = inner_radius * math.cos(main_start_angle)
            z = inner_radius * math.sin(main_start_angle)
            vertices.append([x, -self.height / 2, z])  # 12: inner main bottom-left
            
            # Top-left corner (main face)
            vertices.append([x, self.height / 2, z])   # 13: inner main top-left
            
            # Top-right corner (main face)
            x = inner_radius * math.cos(main_end_angle)
            z = inner_radius * math.sin(main_end_angle)
            vertices.append([x, self.height / 2, z])   # 14: inner main top-right
            
            # Bottom-right corner (main face)
            vertices.append([x, -self.height / 2, z])  # 15: inner main bottom-right
            
            # ----- Left bevel face vertices (inner) -----
            # Bottom-left corner (left bevel)
            x = inner_radius * math.cos(left_start_angle)
            z = inner_radius * math.sin(left_start_angle)
            vertices.append([x, -self.height / 2, z])  # 16: inner left bevel bottom-left
            
            # Top-left corner (left bevel)
            vertices.append([x, self.height / 2, z])   # 17: inner left bevel top-left
            
            # Top-right corner (left bevel)
            x = inner_radius * math.cos(left_end_angle)
            z = inner_radius * math.sin(left_end_angle)
            vertices.append([x, self.height / 2, z])   # 18: inner left bevel top-right
            
            # Bottom-right corner (left bevel)
            vertices.append([x, -self.height / 2, z])  # 19: inner left bevel bottom-right
            
            # ----- Right bevel face vertices (inner) -----
            # Bottom-left corner (right bevel)
            x = inner_radius * math.cos(right_start_angle)
            z = inner_radius * math.sin(right_start_angle)
            vertices.append([x, -self.height / 2, z])  # 20: inner right bevel bottom-left
            
            # Top-left corner (right bevel)
            vertices.append([x, self.height / 2, z])   # 21: inner right bevel top-left
            
            # Top-right corner (right bevel)
            x = inner_radius * math.cos(right_end_angle)
            z = inner_radius * math.sin(right_end_angle)
            vertices.append([x, self.height / 2, z])   # 22: inner right bevel top-right
            
            # Bottom-right corner (right bevel)
            vertices.append([x, -self.height / 2, z])  # 23: inner right bevel bottom-right
            
        # Create faces for the cylinder wall
        faces = []
        
        for i in range(self.segments):
            base_idx = i * 24  # 24 vertices per segment (12 outer + 12 inner)
            
            # ----- OUTER SURFACE FACES -----
            
            # Main face triangles (outer surface)
            o_main_bl = base_idx      # outer main bottom-left
            o_main_tl = base_idx + 1  # outer main top-left
            o_main_tr = base_idx + 2  # outer main top-right
            o_main_br = base_idx + 3  # outer main bottom-right
            
            faces.append([o_main_bl, o_main_br, o_main_tl])  # First triangle
            faces.append([o_main_tl, o_main_br, o_main_tr])  # Second triangle
            
            # Left bevel triangles (outer surface)
            o_left_bl = base_idx + 4  # outer left bevel bottom-left
            o_left_tl = base_idx + 5  # outer left bevel top-left
            o_left_tr = base_idx + 6  # outer left bevel top-right
            o_left_br = base_idx + 7  # outer left bevel bottom-right
            
            faces.append([o_left_bl, o_left_br, o_left_tl])  # First triangle
            faces.append([o_left_tl, o_left_br, o_left_tr])  # Second triangle
            
            # Right bevel triangles (outer surface)
            o_right_bl = base_idx + 8   # outer right bevel bottom-left
            o_right_tl = base_idx + 9   # outer right bevel top-left
            o_right_tr = base_idx + 10  # outer right bevel top-right
            o_right_br = base_idx + 11  # outer right bevel bottom-right
            
            faces.append([o_right_bl, o_right_br, o_right_tl])  # First triangle
            faces.append([o_right_tl, o_right_br, o_right_tr])  # Second triangle
            
            # ----- INNER SURFACE FACES (reversed winding) -----
            
            # Main face triangles (inner surface)
            i_main_bl = base_idx + 12  # inner main bottom-left
            i_main_tl = base_idx + 13  # inner main top-left
            i_main_tr = base_idx + 14  # inner main top-right
            i_main_br = base_idx + 15  # inner main bottom-right
            
            faces.append([i_main_bl, i_main_tl, i_main_br])  # First triangle (reversed)
            faces.append([i_main_tl, i_main_tr, i_main_br])  # Second triangle (reversed)
            
            # Left bevel triangles (inner surface)
            i_left_bl = base_idx + 16  # inner left bevel bottom-left
            i_left_tl = base_idx + 17  # inner left bevel top-left
            i_left_tr = base_idx + 18  # inner left bevel top-right
            i_left_br = base_idx + 19  # inner left bevel bottom-right
            
            faces.append([i_left_bl, i_left_tl, i_left_br])  # First triangle (reversed)
            faces.append([i_left_tl, i_left_tr, i_left_br])  # Second triangle (reversed)
            
            # Right bevel triangles (inner surface)
            i_right_bl = base_idx + 20  # inner right bevel bottom-left
            i_right_tl = base_idx + 21  # inner right bevel top-left
            i_right_tr = base_idx + 22  # inner right bevel top-right
            i_right_br = base_idx + 23  # inner right bevel bottom-right
            
            faces.append([i_right_bl, i_right_tl, i_right_br])  # First triangle (reversed)
            faces.append([i_right_tl, i_right_tr, i_right_br])  # Second triangle (reversed)
            
            # ----- TOP EDGE FACES (connecting outer and inner) -----
            
            # Top main segment
            faces.append([o_main_tl, o_main_tr, i_main_tl])  # First triangle
            faces.append([i_main_tl, o_main_tr, i_main_tr])  # Second triangle
            
            # Top left bevel
            faces.append([o_left_tl, o_left_tr, i_left_tl])  # First triangle
            faces.append([i_left_tl, o_left_tr, i_left_tr])  # Second triangle
            
            # Top right bevel
            faces.append([o_right_tl, o_right_tr, i_right_tl])  # First triangle
            faces.append([i_right_tl, o_right_tr, i_right_tr])  # Second triangle
            
            # ----- BOTTOM EDGE FACES (connecting outer and inner) -----
            
            # Bottom main segment
            faces.append([o_main_br, o_main_bl, i_main_bl])  # First triangle
            faces.append([o_main_br, i_main_bl, i_main_br])  # Second triangle
            
            # Bottom left bevel
            faces.append([o_left_br, o_left_bl, i_left_bl])  # First triangle
            faces.append([o_left_br, i_left_bl, i_left_br])  # Second triangle
            
            # Bottom right bevel
            faces.append([o_right_br, o_right_bl, i_right_bl])  # First triangle
            faces.append([o_right_br, i_right_bl, i_right_br])  # Second triangle
            
            # ----- LEFT JOIN FACES -----
            
            # Connect outer left bevel to outer main
            faces.append([o_left_tr, o_main_tl, o_left_br])  # First triangle
            faces.append([o_left_br, o_main_tl, o_main_bl])  # Second triangle
            
            # Connect inner left bevel to inner main
            faces.append([i_left_tr, i_left_br, i_main_tl])  # First triangle (reversed)
            faces.append([i_left_br, i_main_bl, i_main_tl])  # Second triangle (reversed)
            
            # ----- RIGHT JOIN FACES -----
            
            # Connect outer main to outer right bevel
            faces.append([o_main_tr, o_right_tl, o_main_br])  # First triangle
            faces.append([o_main_br, o_right_tl, o_right_bl])  # Second triangle
            
            # Connect inner main to inner right bevel
            faces.append([i_main_tr, i_main_br, i_right_tl])  # First triangle (reversed)
            faces.append([i_main_br, i_right_bl, i_right_tl])  # Second triangle (reversed)
            
        # Create the mesh
        side_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Apply material
        pbr_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=self.side_material.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0]),
            metallicFactor=self.side_material.get("metallicFactor", 0.0),
            roughnessFactor=self.side_material.get("roughnessFactor", 0.0),
            emissiveFactor=self.side_material.get("emissiveFactor", [0.0, 0.0, 0.0]),
            doubleSided=self.side_material.get("doubleSided", False),
        )
        
        # Apply material to mesh
        side_mesh.visual.material = pbr_material
        return side_mesh

    def _create_top_cap_mesh(self) -> trimesh.Trimesh:
        """
        Create the top cap mesh using the Circle class.

        Returns:
            A trimesh.Trimesh object representing the cylinder top cap
        """
        # Use the Circle class to create the top cap
        top_circle = Circle(
            radius=self.radius,
            segments=self.segments,
            facing="up",
            position=[0, self.height / 2, 0],
            material=self.top_material,
            name=f"{self.name}_top",
        )

        # Return just the mesh component
        return top_circle.mesh

    def _create_bottom_cap_mesh(self) -> trimesh.Trimesh:
        """
        Create the bottom cap mesh using the Circle class.

        Returns:
            A trimesh.Trimesh object representing the cylinder bottom cap
        """
        # Use the Circle class to create the bottom cap
        bottom_circle = Circle(
            radius=self.radius,
            segments=self.segments,
            facing="down",  # This ensures proper face orientation
            position=[0, -self.height / 2, 0],
            material=self.bottom_material,
            name=f"{self.name}_bottom",
        )

        # Return just the mesh component
        return bottom_circle.mesh

    def get_mesh(self) -> trimesh.Trimesh:
        """
        Get a combined cylinder mesh object with all parts.

        Returns:
            mesh: The cylinder as a single combined trimesh.Trimesh object
        """
        # Create a list to hold the meshes to combine
        meshes = [self.side_mesh]
        if self.top_mesh:
            meshes.append(self.top_mesh)
        if self.bottom_mesh:
            meshes.append(self.bottom_mesh)

        # Combine all meshes into one
        combined_mesh = trimesh.util.concatenate(meshes)
        return combined_mesh

    def get_scene(self) -> trimesh.Scene:
        """
        Get the cylinder as a scene object with separate meshes for sides, top, and bottom.
        This preserves the separate materials for each part.

        Returns:
            scene: The cylinder as a trimesh.Scene object with separate meshes
        """
        scene = trimesh.Scene()

        # Add each part with its own name
        scene.add_geometry(self.side_mesh, node_name=f"{self.name}_side")

        if self.top_mesh:
            scene.add_geometry(self.top_mesh, node_name=f"{self.name}_top")

        if self.bottom_mesh:
            scene.add_geometry(self.bottom_mesh, node_name=f"{self.name}_bottom")

        return scene

    def save(self, file_path: str) -> bool:
        """
        Save the cylinder to a file.

        Args:
            file_path: Path to save the file to (supports formats like .glb, .obj, .stl)

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Use get_scene to preserve separate materials
            scene = self.get_scene()
            scene.export(file_path)
            return True
        except Exception as e:
            print(f"Error saving cylinder: {e}")
            return False

    def update_side_material(self, material: Dict[str, Any]) -> None:
        """
        Update the material of the cylinder side.

        Args:
            material: Dictionary of material properties
        """
        self.side_material = material

        # Create and apply new material
        pbr_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=material.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0]),
            metallicFactor=material.get("metallicFactor", 0.0),
            roughnessFactor=material.get("roughnessFactor", 0.0),
            emissiveFactor=material.get("emissiveFactor", [0.0, 0.0, 0.0]),
            doubleSided=material.get("doubleSided", False),
        )

        # Apply to side mesh
        self.side_mesh.visual.material = pbr_material

        # Update the combined mesh for backward compatibility
        self.mesh = self.get_mesh()

    def update_top_material(self, material: Dict[str, Any]) -> None:
        """
        Update the material of the cylinder top cap.

        Args:
            material: Dictionary of material properties
        """
        if not self.caps or self.top_mesh is None:
            print("Warning: Cylinder has no top cap to update")
            return

        self.top_material = material

        # Create and apply new material
        pbr_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=material.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0]),
            metallicFactor=material.get("metallicFactor", 0.0),
            roughnessFactor=material.get("roughnessFactor", 0.0),
            emissiveFactor=material.get("emissiveFactor", [0.0, 0.0, 0.0]),
            doubleSided=material.get("doubleSided", False),
        )

        # Apply to top cap mesh
        self.top_mesh.visual.material = pbr_material

        # Update the combined mesh for backward compatibility
        self.mesh = self.get_mesh()

    def update_bottom_material(self, material: Dict[str, Any]) -> None:
        """
        Update the material of the cylinder bottom cap.

        Args:
            material: Dictionary of material properties
        """
        if not self.caps or self.bottom_mesh is None:
            print("Warning: Cylinder has no bottom cap to update")
            return

        self.bottom_material = material

        # Create and apply new material
        pbr_material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=material.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0]),
            metallicFactor=material.get("metallicFactor", 0.0),
            roughnessFactor=material.get("roughnessFactor", 0.0),
            emissiveFactor=material.get("emissiveFactor", [0.0, 0.0, 0.0]),
            doubleSided=material.get("doubleSided", False),
        )

        # Apply to bottom cap mesh
        self.bottom_mesh.visual.material = pbr_material

        # Update the combined mesh for backward compatibility
        self.mesh = self.get_mesh()
