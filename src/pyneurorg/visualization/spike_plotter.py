# pyneurorg/visualization/spike_plotter.py

"""
Functions for visualizing spike train data and membrane potential traces
from pyneurorg simulations, using Matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
import brian2 as b2

def plot_raster(spike_indices, spike_times, duration=None, ax=None,
                marker_size=2, marker_color='black', title="Raster Plot",
                time_unit_display=b2.ms, ylabel="Neuron Index"):
    """
    Generates a raster plot of spike activity.

    Parameters
    ----------
    spike_indices : array-like or brian2.core.variables.VariableView
        Array of neuron indices corresponding to each spike. Typically `SpikeMonitor.i`.
    spike_times : brian2.core.variables.VariableView or brian2.units.fundamentalunits.Quantity
        Array of spike times. Typically `SpikeMonitor.t`. Will be converted to `time_unit_display`.
    duration : brian2.units.fundamentalunits.Quantity or float, optional
        Total duration for the x-axis limit. If a Brian2 Quantity, it's converted
        to `time_unit_display`. If a float, it's assumed to be in `time_unit_display`.
    ax : matplotlib.axes.Axes, optional
        An existing Matplotlib Axes object to plot on.
    marker_size : int, optional
        Size of the markers for spikes.
    marker_color : str, optional
        Color of the spike markers.
    title : str, optional
        Title for the plot.
    time_unit_display : brian2.units.fundamentalunits.UnitSymbol, optional
        The Brian2 unit to use for displaying time on the x-axis (default: b2.ms).
    ylabel : str, optional
        Label for the y-axis.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    # --- CORREÇÃO PARA LIDAR COM VariableView E Quantity ---
    # Get numerical values of spike_times in the desired display unit
    try:
        # For VariableView or Quantity, dividing by the unit gives a plain NumPy array of numbers
        plot_times_val = np.asarray(spike_times / time_unit_display)
    except AttributeError: # If spike_times doesn't have units (e.g., already a raw array in correct scale)
        plot_times_val = np.asarray(spike_times)
    except Exception as e:
        raise TypeError(f"Could not process spike_times. Expected Brian2 VariableView/Quantity or array-like. Error: {e}")

    # Ensure spike_indices is a NumPy array
    plot_indices_val = np.asarray(spike_indices)
    if not (plot_indices_val.ndim == 1 and plot_times_val.ndim == 1 and len(plot_indices_val) == len(plot_times_val)):
        if len(plot_indices_val) == 0 and len(plot_times_val) == 0: # Empty, which is fine
            pass
        else:
            raise ValueError("spike_indices and spike_times must be 1D arrays of the same length.")


    plot_duration_val = None
    if duration is not None:
        if isinstance(duration, b2.Quantity):
            if duration.dimensions != b2.second.dimensions:
                raise TypeError("duration must have time dimensions if it's a Brian2 Quantity.")
            plot_duration_val = float(duration / time_unit_display)
        elif isinstance(duration, (int, float)):
            plot_duration_val = float(duration)
        else:
            raise TypeError("duration must be a Brian2 Quantity, a number, or None.")
    # --- FIM DA CORREÇÃO ---

    if len(plot_times_val) > 0 or plot_duration_val is not None:
        ax.plot(plot_times_val, plot_indices_val, '|', markersize=marker_size, color=marker_color)
        ax.set_xlabel(f"Time ({time_unit_display!s})")
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        if plot_duration_val is not None:
            ax.set_xlim([0, plot_duration_val])
        elif len(plot_times_val) > 0:
            min_t, max_t = np.min(plot_times_val), np.max(plot_times_val)
            padding = 0.05 * (max_t - min_t) if (max_t - min_t) > 1e-9 else 0.05 * max_t
            if padding == 0 and max_t == 0 : padding = 1.0
            ax.set_xlim([max(0, min_t - padding), max_t + padding])
        else:
            ax.set_xlim([0, 1])

        if len(plot_indices_val) > 0:
            ax.set_ylim([np.min(plot_indices_val) - 0.5, np.max(plot_indices_val) + 0.5])
        else:
            ax.set_ylim([-0.5, 0.5])
    else:
        ax.set_xlabel(f"Time ({time_unit_display!s})")
        ax.set_ylabel(ylabel)
        ax.set_title(title + " (No data)")
        ax.set_xlim([0,1]); ax.set_ylim([-0.5, 0.5])

    ax.grid(True, linestyle=':', alpha=0.7)
    return ax


def plot_vm_traces(state_monitor, neuron_indices=None, time_unit_display=b2.ms, voltage_unit_display=b2.mV,
                   ax=None, title="Membrane Potential Traces",
                   xlabel=None, ylabel=None, legend_loc="best", alpha=0.8):
    """
    Plots membrane potential (Vm) traces for selected neurons from a StateMonitor.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    # --- CORREÇÃO PARA LIDAR COM VariableView E Quantity PARA DADOS DE VOLTAGEM E TEMPO ---
    times_qty = state_monitor.t # This is a VariableView
    
    # Determine which variable to plot as Vm
    voltage_data_raw = None # This will be the VariableView or Quantity
    voltage_var_name_recorded = ""

    if hasattr(state_monitor, 'v'): # Common case where 'v' is directly an attribute
        voltage_data_raw = state_monitor.v
        voltage_var_name_recorded = 'v'
    elif state_monitor.variables: # Check the dict of recorded variables if 'v' is not a direct attr
        if 'v' in state_monitor.variables:
            voltage_data_raw = getattr(state_monitor, 'v') # It might still be an attribute
            voltage_var_name_recorded = 'v'
        else: # Fallback to the first recorded variable
            first_var_key = list(state_monitor.variables.keys())[0]
            voltage_data_raw = getattr(state_monitor, first_var_key)
            voltage_var_name_recorded = first_var_key
            print(f"Info: Plotting variable '{voltage_var_name_recorded}' as Vm from StateMonitor.")
    else:
        raise AttributeError("StateMonitor does not seem to have recorded 'v' or any other variables.")
    
    if voltage_data_raw is None:
        raise AttributeError("Could not extract voltage data from StateMonitor.")

    # Get numerical values in desired display units
    try:
        times_val = np.asarray(times_qty / time_unit_display)
    except Exception as e:
        raise TypeError(f"Could not process StateMonitor.t. Error: {e}")
    
    try:
        voltages_val = np.asarray(voltage_data_raw / voltage_unit_display)
    except Exception as e:
        raise TypeError(f"Could not process StateMonitor variable '{voltage_var_name_recorded}'. Error: {e}")
    # --- FIM DA CORREÇÃO ---

    num_actually_recorded_neurons = voltages_val.shape[0]
    indices_in_monitor_to_plot = []

    if neuron_indices is None:
        if num_actually_recorded_neurons <= 5:
            indices_in_monitor_to_plot = list(range(num_actually_recorded_neurons))
        elif num_actually_recorded_neurons > 0:
            raise ValueError(f"{num_actually_recorded_neurons} neurons recorded by StateMonitor. Please specify `neuron_indices`.")
    elif isinstance(neuron_indices, int):
        if not (0 <= neuron_indices < num_actually_recorded_neurons):
            raise ValueError(f"neuron_index {neuron_indices} out of bounds for monitor's data (0-{num_actually_recorded_neurons-1}).")
        indices_in_monitor_to_plot = [neuron_indices]
    elif isinstance(neuron_indices, (list, slice, np.ndarray)):
        # (Lógica para processar list/slice como antes)
        if isinstance(neuron_indices, slice):
            indices_in_monitor_to_plot = list(range(*neuron_indices.indices(num_actually_recorded_neurons)))
        else: 
            indices_in_monitor_to_plot = list(neuron_indices)
        for idx_mon in indices_in_monitor_to_plot:
            if not (0 <= idx_mon < num_actually_recorded_neurons):
                raise ValueError(f"Neuron index {idx_mon} out of bounds for monitor's data (0-{num_actually_recorded_neurons-1}).")
    else:
        raise TypeError("neuron_indices must be None, int, list, slice, or np.ndarray.")

    if not indices_in_monitor_to_plot and num_actually_recorded_neurons > 0:
        print("Warning: No specific neuron indices selected for plotting Vm.")
    elif num_actually_recorded_neurons == 0:
        print("Warning: StateMonitor recorded no data or no neurons.")

    for monitor_idx_to_plot in indices_in_monitor_to_plot:
        original_neuron_label = "" # (Lógica para rótulo como antes)
        if isinstance(state_monitor.record, (list, np.ndarray)): original_neuron_label = f"Neuron {state_monitor.record[monitor_idx_to_plot]}"
        elif isinstance(state_monitor.record, slice):
            start = state_monitor.record.start if state_monitor.record.start is not None else 0
            step = state_monitor.record.step if state_monitor.record.step is not None else 1
            original_neuron_label = f"Neuron {start + monitor_idx_to_plot * step}"
        elif state_monitor.record is True: original_neuron_label = f"Neuron {monitor_idx_to_plot}"
        else: original_neuron_label = f"Trace {monitor_idx_to_plot}"
        ax.plot(times_val, voltages_val[monitor_idx_to_plot, :], label=original_neuron_label, alpha=alpha)

    ax.set_title(title)
    ax.set_xlabel(xlabel if xlabel is not None else f"Time ({time_unit_display!s})")
    ax.set_ylabel(ylabel if ylabel is not None else f"Vm ({voltage_var_name_recorded} in {voltage_unit_display!s})") # More specific ylabel

    if legend_loc and len(indices_in_monitor_to_plot) > 0:
        ax.legend(loc=legend_loc, fontsize='small')

    ax.grid(True, linestyle=':', alpha=0.7)
    return ax