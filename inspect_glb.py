import json
import math
import os
import random
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pyrender
import trimesh

from utils import calculate_camera_distance, get_object_dimensions

# Add compatibility for libraries using np.infty
if not hasattr(np, "infty"):
    np.infty = np.inf


def inspect_materials(
    mesh_or_scene: Union[trimesh.Trimesh, trimesh.Scene, str], detailed: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Locate and display all materials in a trimesh object or scene.

    Args:
        mesh_or_scene: A trimesh.Mesh, trimesh.Scene object, or a string filepath to a 3D model file
        detailed: Whether to show detailed information about each material property

    Returns:
        materials_dict: Dictionary of materials found, with properties as nested dictionaries
    """
    # Load the file if a string is provided
    if isinstance(mesh_or_scene, str):
        if not os.path.exists(mesh_or_scene):
            raise FileNotFoundError(f"File not found: {mesh_or_scene}")
        try:
            print(f"Loading model from: {mesh_or_scene}")
            mesh_or_scene = trimesh.load(mesh_or_scene)
        except Exception as e:
            raise ValueError(f"Failed to load 3D model from {mesh_or_scene}: {str(e)}")

    materials_dict = {}
    material_index = 0

    # Process all meshes in a scene
    if isinstance(mesh_or_scene, trimesh.Scene):
        print(f"\nFound {len(mesh_or_scene.geometry)} geometries in scene")

        # Iterate through all geometries in the scene
        for mesh_name, mesh in mesh_or_scene.geometry.items():
            # Check if mesh has material
            if hasattr(mesh, "visual") and hasattr(mesh.visual, "material"):
                material = mesh.visual.material
                material_name = f"Material_{material_index}"

                # Try to get material name if available
                if hasattr(material, "name") and material.name:
                    material_name = material.name

                print(f"\n{'-' * 80}")
                print(f"Material found in mesh: {mesh_name}")
                print(f"Material type: {type(material).__name__}")

                # Store material properties
                material_props = extract_material_properties(material, detailed)

                # Add to materials dictionary
                materials_dict[material_name] = {
                    "mesh": mesh_name,
                    "type": type(material).__name__,
                    "properties": material_props,
                }

                material_index += 1

    # Process a single mesh
    elif hasattr(mesh_or_scene, "visual") and hasattr(mesh_or_scene.visual, "material"):
        material = mesh_or_scene.visual.material
        material_name = f"Material_{material_index}"

        # Try to get material name if available
        if hasattr(material, "name") and material.name:
            material_name = material.name

        print(f"\n{'-' * 80}")
        print(f"Material found in single mesh")
        print(f"Material type: {type(material).__name__}")

        # Store material properties
        material_props = extract_material_properties(material, detailed)

        # Add to materials dictionary
        materials_dict[material_name] = {
            "mesh": "single_mesh",
            "type": type(material).__name__,
            "properties": material_props,
        }

    # Summary
    print(f"\n{'-' * 80}")
    print(f"Total materials found: {len(materials_dict)}")

    return materials_dict


def extract_material_properties(
    material: Union[trimesh.visual.material.Material, Any], detailed: bool = True
) -> Dict[str, Any]:
    """
    Extract all properties from a material object.

    Args:
        material: A material object (PBRMaterial, SimpleMaterial, etc.)
        detailed: Whether to show detailed information about each property

    Returns:
        properties: Dictionary of material properties
    """
    properties = {}

    # Common properties to check for in PBR materials
    pbr_properties = [
        "baseColorFactor",
        "metallicFactor",
        "roughnessFactor",
        "emissiveFactor",
        "normalTexture",
        "occlusionTexture",
        "emissiveTexture",
        "baseColorTexture",
        "metallicRoughnessTexture",
        "normalScale",
        "occlusionStrength",
        "alphaCutoff",
        "alphaMode",
        "doubleSided",
        "ior",
        "name",
    ]

    # Common properties for standard materials
    standard_properties = ["ambient", "diffuse", "specular", "glossiness", "opacity"]

    # Check if it's a PBR material
    if isinstance(material, trimesh.visual.material.PBRMaterial):
        for prop in pbr_properties:
            if hasattr(material, prop):
                value = getattr(material, prop)
                properties[prop] = format_property_value(prop, value)

                if detailed:
                    print(f"  {prop}: {format_property_value(prop, value)}")

    # Check for standard material properties
    elif isinstance(
        material,
        (trimesh.visual.material.SimpleMaterial, trimesh.visual.material.Material),
    ):
        for prop in standard_properties:
            if hasattr(material, prop):
                value = getattr(material, prop)
                properties[prop] = format_property_value(prop, value)

                if detailed:
                    print(f"  {prop}: {format_property_value(prop, value)}")

    # Get all public attributes
    else:
        for attr_name in dir(material):
            # Skip private attributes, methods, and common built-ins
            if (
                attr_name.startswith("_")
                or callable(getattr(material, attr_name))
                or attr_name in ("copy", "from_color", "to_color", "bytearray")
            ):
                continue

            try:
                value = getattr(material, attr_name)
                properties[attr_name] = format_property_value(attr_name, value)

                if detailed:
                    print(f"  {attr_name}: {format_property_value(attr_name, value)}")
            except:
                # Skip properties that can't be easily accessed or serialized
                pass

    # Check for textures
    if hasattr(material, "image"):
        if material.image is not None:
            properties["has_texture"] = True
            properties["texture_shape"] = (
                material.image.shape if hasattr(material.image, "shape") else "Unknown"
            )

            if detailed:
                print(f"  has_texture: True")
                print(f"  texture_shape: {properties['texture_shape']}")
        else:
            properties["has_texture"] = False

    return properties


def format_property_value(
    prop_name: str, value: Any
) -> Union[str, bool, List, Dict, Any]:
    """
    Format property value for display and storage.

    Args:
        prop_name: Name of the property
        value: Value of the property

    Returns:
        Formatted value as string or native type
    """
    # Handle color factors which are typically arrays
    if prop_name in [
        "baseColorFactor",
        "emissiveFactor",
        "diffuse",
        "ambient",
        "specular",
    ]:
        if hasattr(value, "__iter__"):
            # Format as RGB or RGBA
            if len(value) == 3:
                return f"RGB({value[0]:.3f}, {value[1]:.3f}, {value[2]:.3f})"
            elif len(value) == 4:
                return f"RGBA({value[0]:.3f}, {value[1]:.3f}, {value[2]:.3f}, {value[3]:.3f})"
            else:
                return str(value)
        else:
            return str(value)

    # Handle numeric values
    elif prop_name in [
        "metallicFactor",
        "roughnessFactor",
        "normalScale",
        "occlusionStrength",
        "alphaCutoff",
        "ior",
        "opacity",
        "glossiness",
    ]:
        if isinstance(value, (int, float)):
            return f"{value:.4f}"
        else:
            return str(value)

    # Handle boolean properties
    elif prop_name in ["doubleSided"]:
        return bool(value)

    # Handle string properties
    elif prop_name in ["alphaMode", "name"]:
        return str(value)

    # Handle texture objects specially
    elif prop_name.endswith("Texture"):
        return "Texture object present" if value is not None else "None"

    # Default handling for other types
    else:
        # Try to convert numpy arrays to lists for JSON compatibility
        if isinstance(value, np.ndarray):
            return value.tolist()

        # For other types, attempt string conversion
        try:
            return json.dumps(value)
        except:
            return str(value)


def save_material_info(
    materials_dict: Dict[str, Dict[str, Any]], output_file: str = "material_info.json"
) -> bool:
    """
    Save material information to a JSON file.

    Args:
        materials_dict: Dictionary of materials
        output_file: Path to save the JSON file

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        with open(output_file, "w") as f:
            json.dump(materials_dict, f, indent=2)
        print(f"\nMaterial information saved to: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving material information: {e}")
        return False


def optimize_light_positions(
    num_lights: int,
    distances: Optional[Union[List[float], float]] = None,
    max_iterations: int = 1000,
) -> List[np.ndarray]:
    """
    Use simulated annealing to find optimal light positions around an object
    that maximize the distance between each light.

    Args:
        num_lights: Number of lights to position
        distances: Distance from the center for each light. If a single float is provided,
                  all lights will be at that distance. If a list is provided, each light
                  will be at its specified distance. If None, defaults to a distance of 1.0.
        max_iterations: Maximum number of iterations for the optimization

    Returns:
        best_positions: List of [x, y, z] positions for each light
    """
    if num_lights <= 0:
        return []

    # Handle distances parameter
    if distances is None:
        distances = [1.0] * num_lights
    elif isinstance(distances, (int, float)):
        distances = [float(distances)] * num_lights
    elif len(distances) < num_lights:
        # If not enough distances provided, pad with the last distance
        distances = list(distances) + [distances[-1]] * (num_lights - len(distances))

    # Initial temperature and cooling rate for simulated annealing
    temperature = 1.0
    cooling_rate = 0.995

    # Generate initial random positions on spheres with specified radii
    positions = []
    for i in range(num_lights):
        # Random point on a sphere
        phi = random.uniform(0, 2 * np.pi)
        theta = random.uniform(0, np.pi)
        distance = distances[i]
        x = distance * np.sin(theta) * np.cos(phi)
        y = distance * np.sin(theta) * np.sin(phi)
        z = distance * np.cos(theta)
        positions.append(np.array([x, y, z]))

    # Function to calculate total minimum distance between all pairs of lights
    def calculate_total_distance(positions: List[np.ndarray]) -> float:
        total = 0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = np.linalg.norm(positions[i] - positions[j])
                total += dist
        return total

    current_distance = calculate_total_distance(positions)
    best_positions = positions.copy()
    best_distance = current_distance

    # Simulated annealing optimization
    for iteration in range(max_iterations):
        # Select a random light to move
        light_idx = random.randint(0, num_lights - 1)

        # Create a new candidate position (maintaining the same distance from center)
        phi = random.uniform(0, 2 * np.pi)
        theta = random.uniform(0, np.pi)
        distance = distances[light_idx]
        x = distance * np.sin(theta) * np.cos(phi)
        y = distance * np.sin(theta) * np.sin(phi)
        z = distance * np.cos(theta)

        # Store the old position
        old_position = positions[light_idx].copy()

        # Try the new position
        positions[light_idx] = np.array([x, y, z])
        new_distance = calculate_total_distance(positions)

        # Decide whether to accept the new position
        if new_distance > current_distance:
            # If better, always accept
            current_distance = new_distance
        else:
            # If worse, accept with a probability that decreases with temperature
            probability = math.exp((new_distance - current_distance) / temperature)
            if random.random() < probability:
                current_distance = new_distance
            else:
                # Revert to old position if not accepted
                positions[light_idx] = old_position

        # Update the best solution if current is better
        if current_distance > best_distance:
            best_distance = current_distance
            best_positions = [pos.copy() for pos in positions]

        # Cool down
        temperature *= cooling_rate

    return best_positions


def view_trimesh_object(
    mesh_or_scene: Union[trimesh.Trimesh, trimesh.Scene],
    show_wireframe: bool = False,
    smooth: bool = True,
    background_color: Optional[List[float]] = None,
    num_lights: int = 3,
    light_distances: Optional[Union[List[float], float]] = None,
    light_intensities: Optional[Union[List[float], float]] = None,
    use_raymond_lighting: bool = False,
) -> None:
    """
    Visualize a trimesh object (Mesh or Scene) directly

    Args:
        mesh_or_scene: A trimesh.Mesh or trimesh.Scene object to visualize
        show_wireframe: Whether to show wireframe overlay
        smooth: Whether to apply smooth shading
        background_color: RGB tuple for background color, e.g. (0.5, 0.5, 0.5)
        num_lights: Number of lights to add to the scene (minimum 0, default 3)
                    Set to 0 to remove all custom lights
        light_distances: Distance from center for each light.
                        If float, all lights use same distance.
                        If list, each light uses its specified distance.
        light_intensities: Intensity for each light (default is 50.0).
                          If float, all lights use same intensity.
                          If list, each light uses its specified intensity.
                          Higher values make lights appear brighter/closer.
                          Recommendation: 50.0
        use_raymond_lighting: Whether to use pyrender's default raymond lighting setup.
                            Set to False to remove the default three lights.

    Returns:
        None
    """
    try:
        # Create a pyrender scene
        scene = pyrender.Scene(
            bg_color=background_color if background_color else [0.0, 0.0, 0.0, 0.0]
        )

        # Check if we have a scene or a single mesh
        if isinstance(mesh_or_scene, trimesh.Scene):
            # For scene objects, iterate through all the meshes
            for mesh_name, mesh in mesh_or_scene.geometry.items():
                # Convert each trimesh to a pyrender mesh with material transfer
                material = None
                if hasattr(mesh, "visual") and hasattr(mesh.visual, "material"):
                    # Extract material properties from trimesh material
                    try:
                        # Handle PBR materials
                        if isinstance(
                            mesh.visual.material, trimesh.visual.material.PBRMaterial
                        ):
                            material = pyrender.MetallicRoughnessMaterial(
                                baseColorFactor=mesh.visual.material.baseColorFactor,
                                metallicFactor=mesh.visual.material.metallicFactor,
                                roughnessFactor=mesh.visual.material.roughnessFactor,
                                emissiveFactor=(
                                    mesh.visual.material.emissiveFactor
                                    if hasattr(mesh.visual.material, "emissiveFactor")
                                    else [0.0, 0.0, 0.0]
                                ),
                                alphaMode=(
                                    "BLEND"
                                    if mesh.visual.material.baseColorFactor[3] < 1.0
                                    else "OPAQUE"
                                ),
                            )
                        # Handle standard trimesh materials
                        elif hasattr(mesh.visual.material, "diffuse"):
                            diffuse = (
                                mesh.visual.material.diffuse / 255.0
                                if isinstance(mesh.visual.material.diffuse[0], int)
                                else mesh.visual.material.diffuse
                            )
                            material = pyrender.MetallicRoughnessMaterial(
                                baseColorFactor=(
                                    list(diffuse) + [1.0]
                                    if len(diffuse) == 3
                                    else diffuse
                                ),
                                metallicFactor=0.0,
                                roughnessFactor=0.5,
                            )
                    except Exception as mat_error:
                        print(
                            f"Warning: Could not convert material for {mesh_name}: {mat_error}"
                        )

                # Transfer textures if available
                if hasattr(mesh, "visual") and hasattr(mesh.visual, "texture"):
                    try:
                        # If mesh has textures, create a textured material
                        py_mesh = pyrender.Mesh.from_trimesh(
                            mesh, smooth=smooth, material=material
                        )
                    except Exception as tex_error:
                        print(
                            f"Warning: Could not transfer texture for {mesh_name}: {tex_error}"
                        )
                        py_mesh = pyrender.Mesh.from_trimesh(
                            mesh, smooth=smooth, material=material
                        )
                else:
                    # Otherwise create a mesh with just material (or default material)
                    py_mesh = pyrender.Mesh.from_trimesh(
                        mesh, smooth=smooth, material=material
                    )

                scene.add(py_mesh)

            # Get the scene's bounding box for camera positioning
            bounds = mesh_or_scene.bounds
        else:
            # For a single mesh object
            # Handle material for single mesh
            material = None
            if hasattr(mesh_or_scene, "visual") and hasattr(
                mesh_or_scene.visual, "material"
            ):
                try:
                    # Handle PBR materials
                    if isinstance(
                        mesh_or_scene.visual.material,
                        trimesh.visual.material.PBRMaterial,
                    ):
                        material = pyrender.MetallicRoughnessMaterial(
                            baseColorFactor=mesh_or_scene.visual.material.baseColorFactor,
                            metallicFactor=mesh_or_scene.visual.material.metallicFactor,
                            roughnessFactor=mesh_or_scene.visual.material.roughnessFactor,
                            emissiveFactor=(
                                mesh_or_scene.visual.material.emissiveFactor
                                if hasattr(
                                    mesh_or_scene.visual.material, "emissiveFactor"
                                )
                                else [0.0, 0.0, 0.0]
                            ),
                            alphaMode=(
                                "BLEND"
                                if mesh_or_scene.visual.material.baseColorFactor[3]
                                < 1.0
                                else "OPAQUE"
                            ),
                        )
                    # Handle standard trimesh materials
                    elif hasattr(mesh_or_scene.visual.material, "diffuse"):
                        diffuse = (
                            mesh_or_scene.visual.material.diffuse / 255.0
                            if isinstance(mesh_or_scene.visual.material.diffuse[0], int)
                            else mesh_or_scene.visual.material.diffuse
                        )
                        material = pyrender.MetallicRoughnessMaterial(
                            baseColorFactor=(
                                list(diffuse) + [1.0] if len(diffuse) == 3 else diffuse
                            ),
                            metallicFactor=0.0,
                            roughnessFactor=0.5,
                        )
                except Exception as mat_error:
                    print(f"Warning: Could not convert material: {mat_error}")

            # Transfer texture if available
            if hasattr(mesh_or_scene, "visual") and hasattr(
                mesh_or_scene.visual, "texture"
            ):
                try:
                    py_mesh = pyrender.Mesh.from_trimesh(
                        mesh_or_scene, smooth=smooth, material=material
                    )
                except Exception as tex_error:
                    print(f"Warning: Could not transfer texture: {tex_error}")
                    py_mesh = pyrender.Mesh.from_trimesh(
                        mesh_or_scene, smooth=smooth, material=material
                    )
            else:
                py_mesh = pyrender.Mesh.from_trimesh(
                    mesh_or_scene, smooth=smooth, material=material
                )

            scene.add(py_mesh)

            # Get the mesh's bounding box for camera positioning
            bounds = mesh_or_scene.bounds

        # Calculate the scene dimensions from bounds
        centroid = (bounds[0] + bounds[1]) / 2.0
        extents = bounds[1] - bounds[0]
        scale = max(
            extents
        )  # Calculate camera position to ensure the entire object is visible
        # Position the camera at a distance that ensures the object fits in view
        # using a standard field of view
        fov = np.pi / 3.0  # 60 degrees
        distance = calculate_camera_distance(scale, fov)

        # Create a camera pose looking at the centroid from a distance
        camera_pose = np.eye(4)
        camera_pose[2, 3] = distance  # Set Z distance

        # Add a camera with the calculated pose
        camera = pyrender.PerspectiveCamera(yfov=fov, aspectRatio=1.0)
        scene.add(camera, pose=camera_pose)

        # Add custom lights if num_lights > 0
        if num_lights > 0:
            # If no light_distances provided, use the calculated scene distance
            if light_distances is None:
                light_distances = distance

            # Handle light intensities
            if light_intensities is None:
                light_intensities = 50.0

            # Convert single values to lists for both distances and intensities
            if isinstance(light_distances, (int, float)):
                light_distances = [float(light_distances)] * num_lights
            elif len(light_distances) < num_lights:
                light_distances = list(light_distances) + [light_distances[-1]] * (
                    num_lights - len(light_distances)
                )

            if isinstance(light_intensities, (int, float)):
                light_intensities = [float(light_intensities)] * num_lights
            elif len(light_intensities) < num_lights:
                light_intensities = list(light_intensities) + [
                    light_intensities[-1]
                ] * (num_lights - len(light_intensities))

            # Optimize light positions using simulated annealing
            light_positions = optimize_light_positions(num_lights, light_distances)

            # Add lights with specified intensities
            for i, light_pos in enumerate(light_positions):
                light_pose = np.eye(4)
                light_pose[:3, 3] = light_pos
                scene.add(
                    pyrender.PointLight(
                        color=[1.0, 1.0, 1.0], intensity=light_intensities[i]
                    ),
                    pose=light_pose,
                )

        # Configure viewer flags
        flags = {
            "wireframe": show_wireframe,
            "show_world_axis": True,
        }

        # Visualize the scene
        pyrender.Viewer(scene, use_raymond_lighting=use_raymond_lighting, **flags)

    except Exception as e:
        print(f"Error visualizing trimesh object: {e}")


def view_glb_file(file_path: str, **kwargs: Any) -> None:
    """
    View a GLB file using pyrender

    Args:
        file_path: Path to the .glb file to be viewed
        kwargs: Additional arguments to pass to the view_trimesh_object function
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return

    # Check if file is a GLB file
    if not file_path.lower().endswith(".glb"):
        print(f"Error: File {file_path} is not a GLB file")
        return

    try:
        # Load the GLB file using trimesh
        trimesh_scene = trimesh.load(file_path)

        # Visualize using the new function
        view_trimesh_object(trimesh_scene, **kwargs)

    except Exception as e:
        print(f"Error loading or rendering the GLB file: {e}")


if __name__ == "__main__":
    glb_file_path = "C:/Users/danie/OneDrive/Desktop/Fun_Apps/GithubCity/assets/building_1x1_0_f.glb"
    # Uncomment to view the GLB file in a 3D viewer
    view_glb_file(glb_file_path, light_intensities=100.0)
    # Check dimensions
    dimensions = get_object_dimensions(glb_file_path)
    print("\nObject Dimensions:")
    print(f"Height (Y-axis): {dimensions['height']:.3f} units")
    print(f"Width (X-axis): {dimensions['width']:.3f} units")
    print(f"Depth (Z-axis): {dimensions['depth']:.3f} units")

    # Inspect materials
    materials = inspect_materials(glb_file_path, detailed=True)
    save_material_info(
        materials, output_file="./outputs/building_1x1_0_f_material_info.json"
    )

    # Example of creating and visualizing a simple trimesh object
    # mesh = trimesh.creation.box(extents=[1, 1, 1])  # Create a simple box
    # view_trimesh_object(mesh, show_wireframe=True)
