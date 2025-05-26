# pyneurorg/organoid/organoid.py

"""
Defines the main Organoid class for pybrainorg simulations.

The Organoid class acts as a container and manager for Brian2 NeuronGroup
and Synapses objects, along with their spatial properties.
"""

import brian2 as b2
import numpy as np
# Importar modelos e funções espaciais dos outros módulos do pybrainorg
from ..core import neuron_models as pbg_neuron_models
from ..core import synapse_models as pbg_synapse_models
from . import spatial as pbg_spatial # Importando o módulo spatial corrigido


class Organoid:
    """
    Represents a brain organoid structure with neuronal populations and synapses.
    Manages the underlying Brian2 NeuronGroup and Synapses objects,
    along with their spatial arrangement and connectivity.
    """

    def __init__(self, name="pybrainorg_organoid", default_brian2_prefs=None):
        """ Initializes a new Organoid instance. """
        self.name = name
        self.neuron_groups = {}
        self.synapses = {}
        self.positions = {} # Stores positions as brian2.Quantity in um
        self.brian2_objects = []

        if default_brian2_prefs:
            for key, value in default_brian2_prefs.items():
                b2.prefs[key] = value
        
        self._neuron_id_counter = 0

    def add_neurons(self, name, num_neurons, model_name, model_params=None,
                    positions=None, spatial_distribution_func=None, spatial_params=None,
                    initial_values=None, **kwargs):
        """
        Adds a population of neurons (a NeuronGroup) to the organoid.

        Parameters
        ----------
        name : str
            A unique name for this neuron group.
        num_neurons : int
            The number of neurons in this group.
        model_name : str
            Name of the neuron model function from `pybrainorg.core.neuron_models`.
        model_params : dict, optional
            Parameters for the neuron model function.
        positions : brian2.units.fundamentalunits.Quantity or array-like, optional
            A (num_neurons, 3) array of (x,y,z) coordinates.
            If a Brian2 Quantity, must have length dimensions.
            If an array-like of numbers, assumed to be in micrometers (um).
            If provided, `spatial_distribution_func` is ignored.
        spatial_distribution_func : str, optional
            Name of the spatial distribution function from `pybrainorg.organoid.spatial`
            (e.g., "random_positions_in_cube"). Used if `positions` is None.
        spatial_params : dict, optional
            Parameters for `spatial_distribution_func`.
        initial_values : dict, optional
            Initial values for neuron state variables (e.g., {'v': -65*b2.mV}).
        **kwargs :
            Additional arguments for `brian2.NeuronGroup`.

        Returns
        -------
        brian2.NeuronGroup
            The created Brian2 NeuronGroup object.
        """
        if name in self.neuron_groups:
            raise ValueError(f"Neuron group with name '{name}' already exists.")
        if model_params is None:
            model_params = {}

        # Get neuron model definition
        try:
            model_func = getattr(pbg_neuron_models, model_name)
        except AttributeError:
            raise ValueError(f"Neuron model function '{model_name}' not found in pybrainorg.core.neuron_models.")
        model_def = model_func(**model_params)

        
        neuron_positions_um_qty = None # Will store positions as Quantity in um

        if positions is not None:
            if isinstance(positions, b2.Quantity):
                if positions.dimensions == b2.metre.dimensions:
                    # Convert to um for internal storage and consistency
                    value_in_um_scalar_array = np.asarray(positions / b2.um)
                    neuron_positions_um_qty = value_in_um_scalar_array * b2.um
                else:
                    raise TypeError("Provided 'positions' Quantity must have length dimensions.")
            elif isinstance(positions, (np.ndarray, list, tuple)):
                # Assume um if raw array/list/tuple of numbers
                try:
                    positions_arr = np.asarray(positions, dtype=float)
                    if positions_arr.ndim != 2 or positions_arr.shape[1] != 3:
                        raise ValueError("If 'positions' is an array/list, it must be N x 3.")
                    neuron_positions_um_qty = positions_arr * b2.um
                except Exception as e:
                    raise TypeError(f"Could not interpret 'positions' as coordinate array (assumed um): {e}")
            else:
                raise TypeError("Provided 'positions' must be a Brian2 Quantity with length units, or an array-like (assumed um).")

            if neuron_positions_um_qty.shape[0] != num_neurons:
                 raise ValueError(f"Provided positions shape ({neuron_positions_um_qty.shape[0]},3) "
                                  f"first dimension does not match num_neurons ({num_neurons}).")

        elif spatial_distribution_func is not None:
            if spatial_params is None:
                spatial_params = {}
            # N is a required param for spatial functions, but they also take num_neurons
            # Ensure consistency or let spatial function handle it.
            # Our spatial functions now default to um.
            current_spatial_params = spatial_params.copy() # Avoid modifying original dict
            current_spatial_params['N'] = num_neurons

            try:
                spatial_func = getattr(pbg_spatial, spatial_distribution_func)
            except AttributeError:
                raise ValueError(f"Spatial distribution function '{spatial_distribution_func}' not found in pybrainorg.organoid.spatial.")
            
            # Spatial functions are refactored to return Quantities in um
            neuron_positions_um_qty = spatial_func(**current_spatial_params)
            if not (isinstance(neuron_positions_um_qty, b2.Quantity) and neuron_positions_um_qty.dimensions == b2.metre.dimensions):
                 raise TypeError(f"Spatial function '{spatial_distribution_func}' did not return a Brian2 Quantity with length dimensions.")
            if neuron_positions_um_qty.shape != (num_neurons, 3):
                raise ValueError(f"Spatial function '{spatial_distribution_func}' returned positions with incorrect shape.")
        else:
            raise ValueError("Either 'positions' or 'spatial_distribution_func' must be provided for neurons.")
       

        # Create NeuronGroup
        current_initial_values = {}
        if 'namespace' in model_def:
            for key, val in model_def['namespace'].items():
                if key.endswith('_default_init'):
                    var_name = key.replace('_default_init', '')
                    current_initial_values[var_name] = val
        
        if initial_values:
            current_initial_values.update(initial_values)

        # For Brian2's spatialneuron, positions are passed differently.
        # For a standard NeuronGroup, we don't pass positions to its constructor directly for 3D.
        # We store them in self.positions and the user/other modules can use them.
        # If Brian2's future spatial features require it, this can be adapted.
        ng = b2.NeuronGroup(
            N=num_neurons,
            model=model_def['model'],
            threshold=model_def.get('threshold'),
            reset=model_def.get('reset'),
            refractory=model_def.get('refractory', False),
            method=kwargs.pop('method', model_def.get('method', 'auto')),
            namespace=model_def.get('namespace', {}),
            name=name,
            **kwargs
        )

        for var_name, value in current_initial_values.items():
            if hasattr(ng, var_name):
                setattr(ng, var_name, value)
            else:
                print(f"Warning: Initial value for '{var_name}' provided, but not found in model for group '{name}'.")

        self.neuron_groups[name] = ng
        self.positions[name] = neuron_positions_um_qty # Store the Quantity in um
        self.brian2_objects.append(ng)
        return ng

  
    def add_synapses(self, name, pre_group_name, post_group_name,
                     model_name, model_params=None,
                     connect_condition=None, connect_prob=None, connect_n=None,
                     on_pre_params=None, on_post_params=None,
                     synaptic_params=None, **kwargs):
        """
        Adds a set of synapses (a Synapses object) connecting two neuron groups.
        (Implementation details as before, ensuring it uses the updated Organoid structure)
        """
        if name in self.synapses:
            raise ValueError(f"Synapse group with name '{name}' already exists.")
        if pre_group_name not in self.neuron_groups:
            raise ValueError(f"Presynaptic neuron group '{pre_group_name}' not found.")
        if post_group_name not in self.neuron_groups:
            raise ValueError(f"Postsynaptic neuron group '{post_group_name}' not found.")

        if model_params is None: model_params = {}
        if on_pre_params is None: on_pre_params = {}
        if on_post_params is None: on_post_params = {}
        if synaptic_params is None: synaptic_params = {}

        pre_ng = self.neuron_groups[pre_group_name]
        post_ng = self.neuron_groups[post_group_name]

        try:
            model_func = getattr(pbg_synapse_models, model_name)
        except AttributeError:
            raise ValueError(f"Synapse model function '{model_name}' not found in pybrainorg.core.synapse_models.")
        model_def = model_func(**model_params)

        syn = b2.Synapses(
            source=pre_ng, target=post_ng,
            model=model_def['model'],
            on_pre=model_def.get('on_pre'), on_post=model_def.get('on_post'),
            namespace=model_def.get('namespace', {}),
            method=kwargs.pop('method', model_def.get('method', 'auto')),
            name=name, **kwargs
        )

        if connect_condition is not None: syn.connect(condition=connect_condition)
        elif connect_prob is not None: syn.connect(p=connect_prob)
        elif connect_n is not None: syn.connect(n=connect_n)
        else:
            if len(pre_ng) * len(post_ng) > 0:
                 print(f"Warning: No connection rule for synapses '{name}'. Defaulting to all-to-all if small.")
                 if len(pre_ng) * len(post_ng) < 100000: syn.connect()
                 else: print(f"Skipping default all-to-all for '{name}' (too large).")
        
        for param_name, value in synaptic_params.items():
            if hasattr(syn, param_name): setattr(syn, param_name, value)
            else: print(f"Warning: Synaptic param '{param_name}' not found in model for '{name}'.")
        for param_name, value in on_pre_params.items():
             if param_name == 'delay': syn.delay = value
        
        self.synapses[name] = syn
        self.brian2_objects.append(syn)
        return syn

    def get_neuron_group(self, name):
        if name not in self.neuron_groups: raise KeyError(f"Neuron group '{name}' not found.")
        return self.neuron_groups[name]

    def get_synapses(self, name):
        if name not in self.synapses: raise KeyError(f"Synapses group '{name}' not found.")
        return self.synapses[name]

    def get_positions(self, neuron_group_name):
        if neuron_group_name not in self.positions: raise KeyError(f"Positions for '{neuron_group_name}' not found.")
        return self.positions[neuron_group_name]

    def __str__(self):
        return (f"<Organoid '{self.name}' with {len(self.neuron_groups)} neuron group(s) "
                f"and {len(self.synapses)} synapse group(s)>")

    def __repr__(self):
        return self.__str__()
