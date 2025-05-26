# pyneurorg/simulation/simulator.py

"""
Defines the Simulator class for orchestrating pyneurorg simulations.

The Simulator class takes an Organoid instance, allows adding monitors,
constructs a Brian2 Network, and runs the simulation.
"""

import brian2 as b2
from ..organoid.organoid import Organoid # For type hinting
from ..electrophysiology import brian_monitors as pbg_monitors

class Simulator:
    """
    Orchestrates Brian2 simulations for a given pyneurorg Organoid.

    This class manages the collection of Brian2 objects from an Organoid,
    allows for the addition of monitors, builds a Brian2 Network,
    runs simulations, and provides access to recorded data.

    Parameters
    ----------
    organoid : pyneurorg.organoid.organoid.Organoid
        The pyneurorg Organoid instance to be simulated.
    brian2_dt : brian2.units.fundamentalunits.Quantity, optional
        The default clock dt for the simulation. If None, Brian2's default
        (currently 0.1*ms) will be used or inherited. (default: None).

    Attributes
    ----------
    organoid : pyneurorg.organoid.organoid.Organoid
        The associated Organoid object.
    brian_network : brian2.Network or None
        The constructed Brian2 Network object. Initially None.
    monitors : dict
        A dictionary to store added monitor objects, keyed by their user-defined names.
    brian_dt : brian2.units.fundamentalunits.Quantity
        The simulation time step.
    """

    def __init__(self, organoid: Organoid, brian2_dt=None):
        """
        Initializes a new Simulator instance.
        """
        if not isinstance(organoid, Organoid):
            raise TypeError("organoid must be an instance of pyneurorg.organoid.Organoid.")

        self.organoid = organoid
        self.brian_network = None
        self.monitors = {} 
        
        if brian2_dt is not None:
            if not isinstance(brian2_dt, b2.Quantity) or not (brian2_dt.dimensions == b2.second.dimensions):
                raise TypeError("brian2_dt must be a Brian2 Quantity with time units.")
            self.brian_dt = brian2_dt
            b2.defaultclock.dt = self.brian_dt 
        else:
            self.brian_dt = b2.defaultclock.dt 
        
        self._network_objects = list(self.organoid.brian2_objects) # Start with objects from organoid

    def add_recording(self, monitor_name: str, monitor_type: str, target_group_name: str, **kwargs):
        """
        Adds a Brian2 monitor to record activity from a specified neuron group.

        Parameters
        ----------
        monitor_name : str
            A unique name to identify this monitor (e.g., "exc_spikes", "inh_vm").
        monitor_type : str
            The type of monitor to add. Supported types: "spike", "state", "population_rate".
        target_group_name : str
            The name of the NeuronGroup within the organoid to monitor.
        **kwargs :
            Additional keyword arguments to pass to the specific monitor setup function
            from `pyneurorg.electrophysiology.brian_monitors`.
            For "state" monitor, `variables` (str or list) is required.
            For "spike" or "state", `record` (bool or list/slice) can be provided.

        Returns
        -------
        brian2.monitors.Monitor
            The created Brian2 monitor object.

        Raises
        ------
        ValueError
            If `monitor_name` already exists, `target_group_name` is not found,
            or `monitor_type` is unsupported.
        KeyError
            If required arguments for a monitor type (like `variables` for 'state') are missing.
        """
        if monitor_name in self.monitors:
            raise ValueError(f"Monitor with name '{monitor_name}' already exists.")
        
        target_group = self.organoid.get_neuron_group(target_group_name)
        
        monitor_object = None
        brian2_monitor_internal_name = kwargs.pop('name', f"pyb_mon_{monitor_name}_{target_group.name}")

        if monitor_type.lower() == "spike":
            monitor_object = pbg_monitors.setup_spike_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "state":
            if 'variables' not in kwargs:
                raise KeyError("Argument 'variables' (str or list of str) is required for 'state' monitor.")
            monitor_object = pbg_monitors.setup_state_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "population_rate":
            monitor_object = pbg_monitors.setup_population_rate_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        else:
            raise ValueError(f"Unsupported monitor_type: '{monitor_type}'. "
                             "Supported types are 'spike', 'state', 'population_rate'.")

        if monitor_object is not None:
            self.monitors[monitor_name] = monitor_object
            if monitor_object not in self._network_objects:
                self._network_objects.append(monitor_object)
        
        return monitor_object

    def build_network(self, **network_kwargs):
        """
        Constructs the Brian2 Network object from all components.

        This method should typically be called internally by `run()` if the
        network hasn't been built yet, but can be called explicitly.

        Parameters
        ----------
        **network_kwargs :
            Additional keyword arguments to pass to the `brian2.Network`
            constructor.
        """
        self.brian_network = b2.Network(self._network_objects, **network_kwargs)


    def run(self, duration: b2.units.fundamentalunits.Quantity, report=None, report_period=10*b2.second, **run_kwargs):
        """
        Runs the simulation for the specified duration.

        If the Brian2 Network has not been built yet, it will be built first.

        Parameters
        ----------
        duration : brian2.units.fundamentalunits.Quantity
            The duration for which to run the simulation (e.g., 100*b2.ms).
        report : str or None, optional
            How to report simulation progress (e.g., 'text', 'stdout', or a function).
            (default: None).
        report_period : brian2.units.fundamentalunits.Quantity, optional
            How often to report progress if `report` is specified (default: 10*second).
        **run_kwargs :
            Additional keyword arguments to pass to the `brian_network.run()`
            method (e.g., `level` for managing object hierarchy in multiple runs).
        """
        if not isinstance(duration, b2.Quantity) or not (duration.dimensions == b2.second.dimensions):
            raise TypeError("duration must be a Brian2 Quantity with time units.")

        if self.brian_network is None:
            self.build_network(**run_kwargs.pop('network_kwargs', {}))

        if self.brian_network is None: 
            raise RuntimeError("Brian2 Network could not be built or is still None.")

        self.brian_network.run(duration, report=report, report_period=report_period, **run_kwargs)

    def get_data(self, monitor_name: str):
        """
        Retrieves the data recorded by a specified monitor.

        Parameters
        ----------
        monitor_name : str
            The user-defined name of the monitor whose data is to be retrieved.

        Returns
        -------
        object
            The data object from the monitor. The type of this object depends
            on the monitor type (e.g., for SpikeMonitor, it contains .i, .t;
            for StateMonitor, it contains recorded variables as attributes).

        Raises
        ------
        KeyError
            If `monitor_name` is not found in the registered monitors.
        """
        if monitor_name not in self.monitors:
            raise KeyError(f"Monitor with name '{monitor_name}' not found. Available monitors: {list(self.monitors.keys())}")
        return self.monitors[monitor_name]

    def store_simulation(self, filename="pyneurorg_sim_state"):
        """
        Stores the current state of the simulation network.

        Parameters
        ----------
        filename : str, optional
            The filename (without extension) to store the state.
            (default: "pyneurorg_sim_state").
        """
        if self.brian_network is None:
            print("Warning: Network not built yet. Nothing to store.")
            return
        self.brian_network.store(name=filename) 
        print(f"Simulation state stored in '{filename}.bri'")


    def restore_simulation(self, filename="pyneurorg_sim_state"):
        """
        Restores the state of the simulation network from a file.

        Note: The network structure (NeuronGroups, Synapses, Monitors)
        must be identical to the one that was stored. This typically means
        re-creating the Simulator and Organoid with the same parameters
        before calling restore.

        Parameters
        ----------
        filename : str, optional
            The filename (without extension) to restore the state from.
            (default: "pyneurorg_sim_state").
        """
        if self.brian_network is None:
            print("Warning: Network not explicitly built locally before restore. Brian2 will handle network object.")
        
        b2.restore(name=filename) 
        print(f"Simulation state restored from '{filename}.bri'. Network may need to be rebuilt on next run.")
        self.brian_network = None 
        self.brian_dt = b2.defaultclock.dt 


    def __str__(self):
        status = "Built" if self.brian_network else "Not Built"
        num_monitors = len(self.monitors)
        return (f"<Simulator for Organoid '{self.organoid.name}' "
                f"with {num_monitors} user-defined monitor(s). Network Status: {status}>")

    def __repr__(self):
        return self.__str__()
