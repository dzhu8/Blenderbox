import os
import numpy as np
import pyrender
import trimesh
import random
import math
from utils import get_object_dimensions, calculate_camera_distance

# Add compatibility for libraries using np.infty
if not hasattr(np, 'infty'):
    np.infty = np.inf

def optimize_light_positions(num_lights, distances=None, max_iterations=1000):
    """
    Use simulated annealing to find optimal light positions around an object
    that maximize the distance between each light.
    
    Args:
        num_lights (int): Number of lights to position
        distances (list or float): Distance from the center for each light. If a single float is provided,
                                  all lights will be at that distance. If a list is provided, each light
                                  will be at its specified distance. If None, defaults to a distance of 1.0.
        max_iterations (int): Maximum number of iterations for the optimization
        
    Returns:
        list: List of [x, y, z] positions for each light
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
    def calculate_total_distance(positions):
        total = 0
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                dist = np.linalg.norm(positions[i] - positions[j])
                total += dist
        return total
    
    current_distance = calculate_total_distance(positions)
    best_positions = positions.copy()
    best_distance = current_distance
    
    # Simulated annealing optimization
    for iteration in range(max_iterations):
        # Select a random light to move
        light_idx = random.randint(0, num_lights-1)
        
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

def view_trimesh_object(mesh_or_scene, show_wireframe=False, smooth=True, background_color=None, 
                    num_lights=3, light_distances=None, light_intensities=None, use_raymond_lighting=False,
                    screen_fill_percentage=0.75):
    """
    Visualize a trimesh object (Mesh or Scene) directly
    
    Args:
        mesh_or_scene: A trimesh.Mesh or trimesh.Scene object to visualize
        show_wireframe (bool): Whether to show wireframe overlay
        smooth (bool): Whether to apply smooth shading
        background_color (tuple): RGB tuple for background color, e.g. (0.5, 0.5, 0.5)
        num_lights (int): Number of lights to add to the scene (minimum 0, default 3)
                          Set to 0 to remove all custom lights
        light_distances (list or float): Distance from center for each light.
                                        If float, all lights use same distance.
                                        If list, each light uses its specified distance.
        light_intensities (list or float): Intensity for each light (default is 50.0).
                                          If float, all lights use same intensity.
                                          If list, each light uses its specified intensity.
                                          Higher values make lights appear brighter/closer. 
                                          Recommendation: 50.0
        use_raymond_lighting (bool): Whether to use pyrender's default raymond lighting setup.
                                    Set to False to remove the default three lights.
        screen_fill_percentage (float): How much of the screen should be filled by the object (0.1 to 1.0)
                                       Higher values zoom in closer, lower values zoom out further.
                                       Default: 0.75 (object fills 75% of the screen)
        
    Returns:
        None
    """
    try:
        # Create a pyrender scene
        scene = pyrender.Scene(bg_color=background_color if background_color else [0.0, 0.0, 0.0, 0.0])
        
        # Check if we have a scene or a single mesh
        if isinstance(mesh_or_scene, trimesh.Scene):
            # For scene objects, iterate through all the meshes
            for mesh_name, mesh in mesh_or_scene.geometry.items():
                # Convert each trimesh to a pyrender mesh with material transfer
                material = None
                if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'material'):
                    # Extract material properties from trimesh material
                    try:
                        # Handle PBR materials
                        if isinstance(mesh.visual.material, trimesh.visual.material.PBRMaterial):
                            material = pyrender.MetallicRoughnessMaterial(
                                baseColorFactor=mesh.visual.material.baseColorFactor,
                                metallicFactor=mesh.visual.material.metallicFactor,
                                roughnessFactor=mesh.visual.material.roughnessFactor,
                                emissiveFactor=mesh.visual.material.emissiveFactor if hasattr(mesh.visual.material, 'emissiveFactor') else [0.0, 0.0, 0.0],
                                alphaMode='BLEND' if mesh.visual.material.baseColorFactor[3] < 1.0 else 'OPAQUE'
                            )
                        # Handle standard trimesh materials
                        elif hasattr(mesh.visual.material, 'diffuse'):
                            diffuse = mesh.visual.material.diffuse / 255.0 if isinstance(mesh.visual.material.diffuse[0], int) else mesh.visual.material.diffuse
                            material = pyrender.MetallicRoughnessMaterial(
                                baseColorFactor=list(diffuse) + [1.0] if len(diffuse) == 3 else diffuse,
                                metallicFactor=0.0,
                                roughnessFactor=0.5
                            )
                    except Exception as mat_error:
                        print(f"Warning: Could not convert material for {mesh_name}: {mat_error}")
                
                # Transfer textures if available
                if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'texture'):
                    try:
                        # If mesh has textures, create a textured material
                        py_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=smooth, material=material)
                    except Exception as tex_error:
                        print(f"Warning: Could not transfer texture for {mesh_name}: {tex_error}")
                        py_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=smooth, material=material)
                else:
                    # Otherwise create a mesh with just material (or default material)
                    py_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=smooth, material=material)
                
                scene.add(py_mesh)
            
            # Get the scene's bounding box for camera positioning
            bounds = mesh_or_scene.bounds
        else:
            # For a single mesh object
            # Handle material for single mesh
            material = None
            if hasattr(mesh_or_scene, 'visual') and hasattr(mesh_or_scene.visual, 'material'):
                try:
                    # Handle PBR materials
                    if isinstance(mesh_or_scene.visual.material, trimesh.visual.material.PBRMaterial):
                        material = pyrender.MetallicRoughnessMaterial(
                            baseColorFactor=mesh_or_scene.visual.material.baseColorFactor,
                            metallicFactor=mesh_or_scene.visual.material.metallicFactor,
                            roughnessFactor=mesh_or_scene.visual.material.roughnessFactor,
                            emissiveFactor=mesh_or_scene.visual.material.emissiveFactor if hasattr(mesh_or_scene.visual.material, 'emissiveFactor') else [0.0, 0.0, 0.0],
                            alphaMode='BLEND' if mesh_or_scene.visual.material.baseColorFactor[3] < 1.0 else 'OPAQUE'
                        )
                    # Handle standard trimesh materials
                    elif hasattr(mesh_or_scene.visual.material, 'diffuse'):
                        diffuse = mesh_or_scene.visual.material.diffuse / 255.0 if isinstance(mesh_or_scene.visual.material.diffuse[0], int) else mesh_or_scene.visual.material.diffuse
                        material = pyrender.MetallicRoughnessMaterial(
                            baseColorFactor=list(diffuse) + [1.0] if len(diffuse) == 3 else diffuse,
                            metallicFactor=0.0,
                            roughnessFactor=0.5
                        )
                except Exception as mat_error:
                    print(f"Warning: Could not convert material: {mat_error}")
            
            # Transfer texture if available
            if hasattr(mesh_or_scene, 'visual') and hasattr(mesh_or_scene.visual, 'texture'):
                try:
                    py_mesh = pyrender.Mesh.from_trimesh(mesh_or_scene, smooth=smooth, material=material)
                except Exception as tex_error:
                    print(f"Warning: Could not transfer texture: {tex_error}")
                    py_mesh = pyrender.Mesh.from_trimesh(mesh_or_scene, smooth=smooth, material=material)
            else:
                py_mesh = pyrender.Mesh.from_trimesh(mesh_or_scene, smooth=smooth, material=material)
                
            scene.add(py_mesh)
            
            # Get the mesh's bounding box for camera positioning
            bounds = mesh_or_scene.bounds
        
        # Calculate the scene dimensions from bounds
        centroid = (bounds[0] + bounds[1]) / 2.0
        extents = bounds[1] - bounds[0]
        scale = max(extents)
        
        # Calculate camera position to ensure the entire object is visible
        # Position the camera at a distance that ensures the object fits in view
        # using a standard field of view
        fov = np.pi / 3.0  # 60 degrees
        distance = calculate_camera_distance(scale, fov, screen_fill_percentage)  # Pass the screen_fill_percentage

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
                light_distances = list(light_distances) + [light_distances[-1]] * (num_lights - len(light_distances))
            
            if isinstance(light_intensities, (int, float)):
                light_intensities = [float(light_intensities)] * num_lights
            elif len(light_intensities) < num_lights:
                light_intensities = list(light_intensities) + [light_intensities[-1]] * (num_lights - len(light_intensities))
                
            # Optimize light positions using simulated annealing
            light_positions = optimize_light_positions(num_lights, light_distances)
            
            # Add lights with specified intensities
            for i, light_pos in enumerate(light_positions):
                light_pose = np.eye(4)
                light_pose[:3, 3] = light_pos
                scene.add(pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=light_intensities[i]), pose=light_pose)
        
        # Configure viewer flags
        flags = {
            'wireframe': show_wireframe, 
            'show_world_axis': True,
        }
        
        # Visualize the scene
        pyrender.Viewer(scene, use_raymond_lighting=use_raymond_lighting, **flags)
        
    except Exception as e:
        print(f"Error visualizing trimesh object: {e}")


def view_glb_file(file_path, **kwargs):
    """
    View a GLB file using pyrender
    
    Args:
        file_path (str): Path to the .glb file to be viewed
        kwargs: Additional arguments to pass to the view_trimesh_object function
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return
    
    # Check if file is a GLB file
    if not file_path.lower().endswith('.glb'):
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
    
    
    # Example of creating and visualizing a simple trimesh object
    # mesh = trimesh.creation.box(extents=[1, 1, 1])  # Create a simple box
    # view_trimesh_object(mesh, show_wireframe=True)
