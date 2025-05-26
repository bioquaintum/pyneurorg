# pyneurorg/electrophysiology/brian_monitors.py

"""
Helper functions for creating and configuring Brian2 monitors.

These functions simplify the setup of common monitors like SpikeMonitor,
StateMonitor, and PopulationRateMonitor for pyneurorg simulations.
"""

import brian2 as b2

def setup_spike_monitor(source, record=True, name=None, **kwargs):
    """
    Creates and configures a Brian2 SpikeMonitor.

    Parameters
    ----------
    source : brian2.groups.Group
        The Brian2 Group (e.g., NeuronGroup) from which to record spikes.
    record : bool or sequence of int, optional
        Which neurons to record from. If True, record from all neurons.
        If a sequence of ints, record from neurons with these indices.
        (default: True).
    name : str, optional
        A unique name for the monitor. If None, Brian2 will generate one.
        (default: None).
    **kwargs :
        Additional keyword arguments to pass to the `brian2.SpikeMonitor`
        constructor.

    Returns
    -------
    brian2.monitors.spikemonitor.SpikeMonitor
        The configured SpikeMonitor object.

    Examples
    --------
    >>> from brian2 import NeuronGroup, SpikeMonitor, run, ms
    >>> from pyneurorg.electrophysiology.brian_monitors import setup_spike_monitor
    >>> G = NeuronGroup(10, 'dv/dt = -v/(10*ms) : 1', threshold='v>1', reset='v=0', method='exact')
    >>> G.v = 1.1 # Make them spike
    >>> spikemon = setup_spike_monitor(G, name="my_spikes")
    >>> # In a Network: net = Network(G, spikemon); net.run(1*ms)
    """
    if name is None: # Ensure a unique name if not provided for easier retrieval later
        name = f'{source.name}_spikemon_{b2.defaultclock.t/b2.ms:.0f}ms'

    monitor = b2.SpikeMonitor(source, record=record, name=name, **kwargs)
    return monitor


def setup_state_monitor(source, variables, record=True, dt=None, name=None, **kwargs):
    """
    Creates and configures a Brian2 StateMonitor.

    Parameters
    ----------
    source : brian2.groups.Group
        The Brian2 Group (e.g., NeuronGroup) from which to record state variables.
    variables : str or list of str
        The state variable(s) to record (e.g., 'v', ['v', 'u']).
    record : bool or sequence of int or slice, optional
        Which neurons to record from. If True, record from all neurons.
        If a sequence of ints or a slice, record from specified neurons.
        (default: True).
    dt : brian2.units.fundamentalunits.Quantity, optional
        The time step for recording. If None, records at every simulation time step.
        (default: None).
    name : str, optional
        A unique name for the monitor. If None, Brian2 will generate one.
        (default: None).
    **kwargs :
        Additional keyword arguments to pass to the `brian2.StateMonitor`
        constructor.

    Returns
    -------
    brian2.monitors.statemonitor.StateMonitor
        The configured StateMonitor object.

    Examples
    --------
    >>> from brian2 import NeuronGroup, StateMonitor, run, ms, mV
    >>> from pyneurorg.electrophysiology.brian_monitors import setup_state_monitor
    >>> G = NeuronGroup(1, 'dv/dt = (1-v)/(10*ms) : 1 (unless refractory)', threshold='v>0.8', reset='v=0', refractory=5*ms, method='exact')
    >>> G.v = 0
    >>> statemon = setup_state_monitor(G, 'v', name="my_vm_trace", dt=0.1*ms)
    >>> # In a Network: net = Network(G, statemon); net.run(10*ms)
    """
    if name is None:
        name = f'{source.name}_statemon_{b2.defaultclock.t/b2.ms:.0f}ms'

    monitor = b2.StateMonitor(source, variables, record=record, dt=dt, name=name, **kwargs)
    return monitor


def setup_population_rate_monitor(source, name=None, **kwargs):
    """
    Creates and configures a Brian2 PopulationRateMonitor.

    Parameters
    ----------
    source : brian2.groups.Group
        The Brian2 Group (e.g., NeuronGroup) for which to monitor the
        population firing rate.
    name : str, optional
        A unique name for the monitor. If None, Brian2 will generate one.
        (default: None).
    **kwargs :
        Additional keyword arguments to pass to the `brian2.PopulationRateMonitor`
        constructor (e.g., `bin` for binning window if not using smoothing).

    Returns
    -------
    brian2.monitors.ratemonitor.PopulationRateMonitor
        The configured PopulationRateMonitor object.

    Examples
    --------
    >>> from brian2 import NeuronGroup, PopulationRateMonitor, run, ms, Hz
    >>> from pyneurorg.electrophysiology.brian_monitors import setup_population_rate_monitor
    >>> G = NeuronGroup(100, 'dv/dt = -v/(10*ms) : 1', threshold='v>1', reset='v=0', method='exact')
    >>> G.v = 'rand()*1.5' # Some initial spread
    >>> ratemon = setup_population_rate_monitor(G, name="my_pop_rate")
    >>> # In a Network: net = Network(G, ratemon); net.run(100*ms)
    """
    if name is None:
        name = f'{source.name}_ratemon_{b2.defaultclock.t/b2.ms:.0f}ms'
    
    # PopulationRateMonitor by default uses a smoothing window.
    # If precise binning is needed, 'bin' argument can be passed in kwargs.
    monitor = b2.PopulationRateMonitor(source, name=name, **kwargs)
    return monitor

# Future considerations:
# - Monitors for specific MEA electrode "readings" (e.g., LFP proxy)
#   could be more complex and might involve custom NeuronGroup "sensors"
#   or NetworkOperation to calculate the signal.
