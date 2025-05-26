# pybrainorg/organoid/spatial.py

"""
Functions for generating and manipulating spatial coordinates of neurons
within a pybrainorg organoid.

All coordinate and size inputs are either Brian2 Quantities with length
dimensions or are assumed to be in micrometers (um) if provided as raw numbers.
All outputs representing coordinates or distances are Brian2 Quantities in um.
"""

import numpy as np
import brian2 as b2
from brian2.units.fundamentalunits import DIMENSIONLESS

def _ensure_um_quantity(value, name="value"):
    """
    Ensures the value is a Brian2 Quantity in micrometers (um).
    If a raw number is given, it's assumed to be in um.
    If a Brian2 Quantity with length dimensions is given, it's converted.
    """
    if isinstance(value, b2.Quantity):
        if value.dimensions == b2.metre.dimensions:
            # To get a new Quantity in um, we first get its value in um, then multiply by b2.um
            # value_in_um_scalar = value / b2.um # This would be a float
            # return value_in_um_scalar * b2.um
            # More direct: Brian2 handles this if you just express it in the target unit
            # A Quantity object inherently stores its value in base SI units.
            # When you multiply by a unit, it creates a new Quantity.
            # To convert, you divide by the old unit and multiply by the new,
            # or simply represent the SI value with the new unit.
            # The most straightforward way to get a Quantity in specific units from another Quantity
            # is to ensure it's correctly scaled.
            # If q = 1*b2.mm, then float(q / b2.um) gives 1000.0.
            # So, (q / b2.um) * b2.um is essentially q, but forces representation.
            # Let's simplify: just return the value multiplied by b2.um if it was a number,
            # or if it was a Quantity, ensure it has length dims and return it as is,
            # subsequent functions will divide by b2.um to get the numerical value.
            # OR, always convert to a numerical value in um, then re-multiply by b2.um. This is safer.
            value_as_um_scalar = float(value / b2.um)
            return value_as_um_scalar * b2.um
        else:
            raise TypeError(f"'{name}' ({value}) must be a Brian2 Quantity with length dimensions or a number (assumed um).")
    elif isinstance(value, (int, float, np.number)):
        return value * b2.um # Assume um if raw number
    else:
        raise TypeError(f"'{name}' ({value}) must be a Brian2 Quantity with length dimensions or a number (assumed um).")

def _ensure_um_tuple(value_tuple, name="value_tuple"):
    """Converts a 3-tuple to Brian2 Quantities in um."""
    if not (isinstance(value_tuple, (tuple, list)) and len(value_tuple) == 3):
        raise TypeError(f"'{name}' must be a 3-tuple of numbers (assumed um) or Brian2 Quantities with length.")
    return tuple(_ensure_um_quantity(v, f"{name}_component_{i}") for i, v in enumerate(value_tuple))


def random_positions_in_cube(N, side_length=100, center=(0,0,0)):
    """
    Generates N random 3D positions uniformly distributed within a cube.
    Input parameters are assumed to be in micrometers (um) if raw numbers.
    Output is a Brian2 Quantity in um.
    """
    if not isinstance(N, int) or N <= 0:
        raise ValueError("N must be a positive integer.")

    side_length_um_qty = _ensure_um_quantity(side_length, "side_length")
    center_um_qty_tuple = _ensure_um_tuple(center, "center")

    # Get numerical values in um for calculation
    side_length_val_um = float(side_length_um_qty / b2.um)
    center_val_um = np.array([float(c / b2.um) for c in center_um_qty_tuple])

    positions_val_um = (np.random.rand(N, 3) - 0.5) * side_length_val_um
    positions_val_um += center_val_um

    return positions_val_um * b2.um


def random_positions_in_sphere(N, radius=100, center=(0,0,0)):
    """
    Generates N random 3D positions uniformly distributed within a sphere.
    Input parameters are assumed to be in micrometers (um) if raw numbers.
    Output is a Brian2 Quantity in um.
    """
    if not isinstance(N, int) or N <= 0:
        raise ValueError("N must be a positive integer.")

    radius_um_qty = _ensure_um_quantity(radius, "radius")
    center_um_qty_tuple = _ensure_um_tuple(center, "center")

    radius_val_um = float(radius_um_qty / b2.um)
    center_val_um = np.array([float(c / b2.um) for c in center_um_qty_tuple])
    
    positions_val_um = np.zeros((N, 3))
    count = 0

    while count < N:
        x, y, z = (np.random.rand(3) * 2 - 1) * radius_val_um
        if x**2 + y**2 + z**2 <= radius_val_um**2:
            positions_val_um[count, :] = [x, y, z]
            count += 1
    
    positions_val_um += center_val_um
    return positions_val_um * b2.um


def random_positions_on_sphere_surface(N, radius=100, center=(0,0,0)):
    """
    Generates N random 3D positions uniformly distributed on the surface of a sphere.
    Input parameters are assumed to be in micrometers (um) if raw numbers.
    Output is a Brian2 Quantity in um.
    """
    if not isinstance(N, int) or N <= 0:
        raise ValueError("N must be a positive integer.")

    radius_um_qty = _ensure_um_quantity(radius, "radius")
    center_um_qty_tuple = _ensure_um_tuple(center, "center")
    
    radius_val_um = float(radius_um_qty / b2.um)
    center_val_um = np.array([float(c / b2.um) for c in center_um_qty_tuple])

    gauss_points = np.random.normal(size=(N, 3))
    norm = np.linalg.norm(gauss_points, axis=1, keepdims=True)
    norm[norm == 0] = 1
    unit_sphere_points = gauss_points / norm
    positions_val_um = unit_sphere_points * radius_val_um
    positions_val_um += center_val_um

    return positions_val_um * b2.um


def _extract_value_in_um(quantity_or_array, name="value"):
    """
    Helper to get the numerical value of a length quantity in micrometers.
    If input is a raw number or NumPy array, it's assumed to be in um.
    If input is a Brian2 Quantity with length dimensions, it's converted to um value.
    Returns a NumPy array of numerical values.
    """
    if isinstance(quantity_or_array, b2.Quantity):
        if quantity_or_array.dimensions == b2.metre.dimensions:
            # Convert the Quantity to a NumPy array of its values in micrometers
            return np.asarray(quantity_or_array / b2.um)
        else:
            raise TypeError(f"'{name}' ({quantity_or_array}) must be a Brian2 Quantity with length dimensions or a number/array (assumed um).")
    elif isinstance(quantity_or_array, (int, float, np.number)): # Handle scalar numbers
        return np.array([quantity_or_array]) # Return as a numpy array
    elif isinstance(quantity_or_array, np.ndarray):
        return quantity_or_array # Assume um
    else:
        raise TypeError(f"'{name}' ({quantity_or_array}) must be a Brian2 Quantity with length dimensions, a number, or a NumPy array (assumed um).")


def distance_matrix(positions1, positions2=None):
    """
    Calculates the Euclidean distance matrix between two sets of 3D points.
    Inputs are assumed to be in micrometers (um) if raw numbers/arrays,
    or are converted to um values if Brian2 Quantities with length dimensions.
    The output distance matrix will be a Brian2 Quantity in um.
    """
    p1_val_um = _extract_value_in_um(positions1, "positions1")
    if p1_val_um.ndim == 1 and p1_val_um.shape[0] == 3: # Handle single 3D point for p1
        p1_val_um = p1_val_um.reshape(1, 3)
    elif p1_val_um.ndim != 2 or p1_val_um.shape[1] != 3:
        raise ValueError("positions1 must be an N x 3 array or a single 3-element array/list.")

    if positions2 is None:
        p2_val_um = p1_val_um
    else:
        p2_val_um = _extract_value_in_um(positions2, "positions2")
        if p2_val_um.ndim == 1 and p2_val_um.shape[0] == 3: # Handle single 3D point for p2
            p2_val_um = p2_val_um.reshape(1, 3)
        elif p2_val_um.ndim != 2 or p2_val_um.shape[1] != 3:
            raise ValueError("positions2 must be an M x 3 array or a single 3-element array/list, or None.")

    try:
        from scipy.spatial.distance import cdist
        dist_val_um = cdist(p1_val_um, p2_val_um, metric='euclidean')
    except ImportError:
        # Fallback manual calculation
        # Reshape for broadcasting if one of them is a single point
        p1_val_um_b = p1_val_um[:, np.newaxis, :] if p1_val_um.ndim == 2 else p1_val_um[np.newaxis, np.newaxis, :]
        p2_val_um_b = p2_val_um[np.newaxis, :, :] if p2_val_um.ndim == 2 else p2_val_um[np.newaxis, np.newaxis, :]
        
        diff = p1_val_um_b - p2_val_um_b # Difference for all pairs
        dist_sq_val = np.sum(diff**2, axis=2)
        dist_val_um = np.sqrt(dist_sq_val)
        if p1_val_um.shape[0] == 1 and p2_val_um.shape[0] > 1: dist_val_um = dist_val_um.ravel()
        elif p2_val_um.shape[0] == 1 and p1_val_um.shape[0] > 1: dist_val_um = dist_val_um.ravel()
        elif p1_val_um.shape[0] == 1 and p2_val_um.shape[0] == 1: dist_val_um = dist_val_um[0,0]


    return dist_val_um * b2.um