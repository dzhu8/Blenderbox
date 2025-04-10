import numpy as np
import trimesh
import os
import math

# ------------------------------------------------------------------------------------------------
# Get the default camera zoom
# ------------------------------------------------------------------------------------------------
def calculate_camera_distance(object_scale, fov=np.pi/3.0, screen_fill_percentage=0.75):
    """
    Calculate camera distance to position an object to fill a certain percentage of the screen.
    
    Args:
        object_scale (float): The scale (largest dimension) of the object
        fov (float): Field of view angle in radians (default: pi/3 or 60 degrees)
        screen_fill_percentage (float): Percentage of the screen width/height that the object should fill (0.1 to 1.0)
                                        Higher values bring the camera closer to the object.
                                        Lower values position the camera farther away.
    
    Returns:
        dist: The optimal camera distance to achieve the desired screen fill percentage
    """
    # Validate the screen fill percentage
    screen_fill_percentage = max(0.1, min(1.0, screen_fill_percentage))
    
    # At distance = scale/tan(fov/2), the object would exactly fill the screen
    # We adjust this to fill only a percentage of the screen
    # When percentage = 1.0, the multiplier should be 1.0
    # When percentage = 0.1, the multiplier should be higher (around 10)
    
    # Since the size of the object on screen is inversely proportional to distance,
    # we divide by the percentage to get the distance multiplier
    distance_multiplier = 1.0 / screen_fill_percentage
    
    # Calculate the base distance at which the object would fill the entire viewport
    base_distance = object_scale / math.tan(fov/2)
    
    # Apply the multiplier
    dist = base_distance * distance_multiplier
    return dist


def get_object_dimensions(mesh_or_scene):
    """
    Calculate and return the dimensions of a trimesh object or scene.
    
    Args:
        mesh_or_scene: A trimesh.Mesh, trimesh.Scene object, or a string filepath to a 3D model file
        
    Returns:
        dims: Dictionary containing the following dimension information:
            - height: Height of the object (Y axis)
            - width: Width of the object (X axis)
            - depth: Depth of the object (Z axis)
            - diameter: Maximum diameter (diagonal)
            - bounds: Raw bounding box coordinates [[min_x, min_y, min_z], [max_x, max_y, max_z]]
            - volume: Volume of the object (if available)
            - surface_area: Surface area (if available)
            - centroid: Center point of the object
            - units: String indicating the units are arbitrary
    """
    # If input is a string, assume it's a file path and try to load it
    if isinstance(mesh_or_scene, str):
        if not os.path.exists(mesh_or_scene):
            raise FileNotFoundError(f"File not found: {mesh_or_scene}")
        try:
            mesh_or_scene = trimesh.load(mesh_or_scene)
        except Exception as e:
            raise ValueError(f"Failed to load 3D model from {mesh_or_scene}: {str(e)}")
    
    # Get bounds from either a scene or mesh
    if isinstance(mesh_or_scene, trimesh.Scene):
        bounds = mesh_or_scene.bounds
        # Try to get cumulative volume if available
        volume = sum([m.volume for m in mesh_or_scene.geometry.values() 
                      if hasattr(m, 'volume')]) if mesh_or_scene.geometry else None
        # Try to get cumulative surface area if available
        surface_area = sum([m.area for m in mesh_or_scene.geometry.values() 
                           if hasattr(m, 'area')]) if mesh_or_scene.geometry else None
    else:
        bounds = mesh_or_scene.bounds
        volume = mesh_or_scene.volume if hasattr(mesh_or_scene, 'volume') else None
        surface_area = mesh_or_scene.area if hasattr(mesh_or_scene, 'area') else None
    
    # Calculate dimensions
    dimensions = bounds[1] - bounds[0]
    width = dimensions[0]   # X-axis
    height = dimensions[1]  # Y-axis
    depth = dimensions[2]   # Z-axis
    
    # Calculate maximum diagonal distance (diameter)
    diameter = np.linalg.norm(dimensions)
    
    # Calculate centroid
    centroid = (bounds[0] + bounds[1]) / 2.0
    
    # Return all dimension information
    dims = {
        'width': width,
        'height': height,
        'depth': depth,
        'diameter': diameter,
        'bounds': bounds,
        'volume': volume,
        'surface_area': surface_area,
        'centroid': centroid,
        'units': 'arbitrary units'
    }

    return dims


def calculate_light_intensity(dimensions, base_intensity=50.0, scaling_factor=5.0):
    """
    Calculate a suggested light intensity based on object dimensions.
    Uses the inverse square law to scale intensity with object size.
    
    Args:
        dimensions: Dictionary containing object dimensions (from get_object_dimensions)
        base_intensity: Minimum light intensity to use (default: 50.0)
        scaling_factor: Multiplier for the intensity calculation (default: 5.0)
        
    Returns:
        suggested_intensity: Suggested light intensity value
    """
    # Use diameter as the key measurement for calculating light intensity
    # This accounts for the inverse square law of light intensity
    if isinstance(dimensions, dict) and 'diameter' in dimensions:
        diameter = dimensions['diameter']
    else:
        # If passed a number directly instead of a dimensions dictionary
        diameter = float(dimensions)
    
    # Calculate intensity - proportional to the square of the diameter
    # with a minimum value and scaling factor
    suggested_intensity = max(base_intensity, diameter * diameter * scaling_factor)
    
    return suggested_intensity