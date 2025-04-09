import os
import numpy as np
import pyrender
import trimesh

# Add compatibility for libraries using np.infty
if not hasattr(np, 'infty'):
    np.infty = np.inf


def explore_glb_contents(file_path, output_file=None):
    """
    Recursively explore a GLB file and print its contents and attributes
    
    Args:
        file_path (str): Path to the .glb file to be explored
        output_file (str, optional): Path to save the output to a text file
    
    Returns:
        scene_structure: A dictionary containing the scene structure and attributes
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return {}
    
    # Check if file is a GLB file
    if not file_path.lower().endswith('.glb'):
        print(f"Error: File {file_path} is not a GLB file")
        return {}
    
    try:
        # Load the GLB file using trimesh
        scene = trimesh.load(file_path)
        
        # Dictionary to store the scene structure
        scene_structure = {}
        
        # Store basic scene info
        scene_structure["file_name"] = os.path.basename(file_path)
        scene_structure["file_path"] = file_path
        
        # Recursively explore and store scene contents
        if isinstance(scene, trimesh.Scene):
            print(f"\nExploring GLB file: {file_path}")
            scene_structure["type"] = "Scene"
            scene_structure["metadata"] = getattr(scene, "metadata", {})
            scene_structure["graph"] = explore_scene_graph(scene.graph)
            scene_structure["geometry"] = explore_scene_geometry(scene)
            
            # Output to console
            print_scene_structure(scene_structure)
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(f"GLB File Analysis: {file_path}\n")
                    f.write("=" * 80 + "\n\n")
                    write_scene_structure(scene_structure, f)
                print(f"\nAnalysis saved to {output_file}")
                
        else:
            print(f"The file {file_path} contains a single mesh, not a scene")
            scene_structure["type"] = "Mesh"
            scene_structure["attributes"] = get_object_attributes(scene)
            print_scene_structure(scene_structure)
            
        return scene_structure
    
    except Exception as e:
        print(f"Error exploring the GLB file: {e}")
        return {}


def explore_scene_graph(graph):
    """Explore the scene graph and return its structure"""
    result = {}
    for node_name, node_data in graph.items():
        result[node_name] = {
            "transform": node_data.get("transform", "None").tolist() if isinstance(node_data.get("transform"), np.ndarray) else None,
            "children": node_data.get("children", []),
            "geometry": node_data.get("geometry", None),
            "camera": node_data.get("camera", None),
            "extras": node_data.get("extras", None)
        }
    return result


def explore_scene_geometry(scene):
    """Explore the scene geometry and return its structure"""
    result = {}
    for geom_name, geom in scene.geometry.items():
        result[geom_name] = get_object_attributes(geom)
    return result


def get_object_attributes(obj):
    """Get all attributes of an object that are not callable or private"""
    result = {}
    for attr_name in dir(obj):
        if not attr_name.startswith('_') and not callable(getattr(obj, attr_name)):
            try:
                attr_value = getattr(obj, attr_name)
                
                # Convert numpy arrays to lists for display
                if isinstance(attr_value, np.ndarray):
                    # If array is large, just show shape and type
                    if attr_value.size > 100:
                        result[attr_name] = f"ndarray(shape={attr_value.shape}, dtype={attr_value.dtype})"
                    else:
                        result[attr_name] = attr_value.tolist()
                # Handle other special types
                elif isinstance(attr_value, (list, tuple)) and len(attr_value) > 100:
                    result[attr_name] = f"{type(attr_value).__name__} of length {len(attr_value)}"
                elif hasattr(attr_value, '__dict__'):
                    result[attr_name] = f"{type(attr_value).__name__} object"
                else:
                    result[attr_name] = attr_value
            except:
                result[attr_name] = "Error accessing attribute"
    return result


def print_scene_structure(structure, indent=0):
    """Print the scene structure in a readable format"""
    indent_str = "  " * indent
    
    for key, value in structure.items():
        if isinstance(value, dict):
            print(f"{indent_str}{key}:")
            print_scene_structure(value, indent + 1)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            print(f"{indent_str}{key}:")
            for item in value:
                print_scene_structure(item, indent + 1)
        else:
            print(f"{indent_str}{key}: {value}")


def write_scene_structure(structure, file, indent=0):
    """Write the scene structure to a file"""
    indent_str = "  " * indent
    
    for key, value in structure.items():
        if isinstance(value, dict):
            file.write(f"{indent_str}{key}:\n")
            write_scene_structure(value, file, indent + 1)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            file.write(f"{indent_str}{key}:\n")
            for item in value:
                write_scene_structure(item, file, indent + 1)
        else:
            file.write(f"{indent_str}{key}: {value}\n")


def view_glb_file(file_path):
    """
    View a GLB file using pyrender
    
    Args:
        file_path (str): Path to the .glb file to be viewed
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
        
        # Create a pyrender scene
        scene = pyrender.Scene()
        
        # Check if we loaded a scene or a single mesh
        if isinstance(trimesh_scene, trimesh.Scene):
            # For scene objects, iterate through all the meshes
            for mesh_name, mesh in trimesh_scene.geometry.items():
                # Convert each trimesh to a pyrender mesh
                py_mesh = pyrender.Mesh.from_trimesh(mesh)
                scene.add(py_mesh)
        else:
            # For a single mesh object
            mesh = pyrender.Mesh.from_trimesh(trimesh_scene)
            scene.add(mesh)
        
        # Add a camera and light
        camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
        scene.add(camera, pose=np.eye(4))
        scene.add(pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0))
        
        # Visualize the scene
        pyrender.Viewer(scene, use_raymond_lighting=True, show_world_axis=True)
        
    except Exception as e:
        print(f"Error loading or rendering the GLB file: {e}")

        
if __name__ == "__main__":
    glb_file_path = "C:/Users/danie/OneDrive/Desktop/Fun_Apps/GithubCity/assets/building_1x1_0_f.glb"
    
    # Explore the GLB contents
    output_file = os.path.splitext(glb_file_path)[0] + "_analysis.txt"
    explore_glb_contents(glb_file_path, output_file)
    
    # Uncomment to view the GLB file in a 3D viewer
    # view_glb_file(glb_file_path)
