![logo](logo.png) 

**pyneurorg** is a Python module designed for simulating neural (brain) organoids, leveraging the power and flexibility of the Brian2 spiking neural network simulator. It provides a structured framework to model neurons and synapses within organoids, simulate their development and activity, and interact with them using simulated Microelectrode Arrays (MEAs) and calcium imaging techniques.

## Objective

The primary goal of `pyneurorg` is to provide researchers with an accessible, modular, and extensible in-silico platform to:
*   Model the formation and maturation of neural networks in neural organoids.
*   Simulate electrophysiological experiments, including MEA-based stimulation and recording.
*   Simulate calcium imaging experiments to observe network activity with high spatial resolution.
*   Investigate the effects of various stimuli, genetic modifications, or disease states on organoid network dynamics.
*   Facilitate the exploration of structural and synaptic plasticity mechanisms.

## Key Features

*   **Brian2-Powered Core:** Utilizes Brian2 for efficient and accurate simulation of spiking neuron and synapse models.
*   **Organoid Construction:** Flexible tools to create 3D organoid structures with defined neuronal populations and spatial arrangements.
*   **MEA Integration:**
    *   Model MEA geometries.
    *   Simulate targeted electrical stimulation of organoids via MEA electrodes.
    *   Record spike activity and Local Field Potential (LFP) proxies from MEA electrodes.
*   **Calcium Imaging Simulation:**
    *   Neuron models incorporating intracellular calcium dynamics.
    *   Simulation of fluorescent calcium indicator signals (e.g., GCaMP's ΔF/F).
*   **Network Plasticity:** (Module named `plasticity`)
    *   Implement common synaptic plasticity rules (e.g., STDP).
    *   Simulate structural plasticity for activity-dependent network formation and pruning.
*   **Electrophysiology Suite:**
    *   Generate complex stimulus patterns.
    *   Comprehensive data recording capabilities.
    *   Persistent data storage using SQLite for simulation results.
*   **Analysis & Visualization:**
    *   Tools for spike train analysis (firing rates, synchrony, bursting).
    *   Calcium trace analysis (ΔF/F, event detection).
    *   Functional network inference from spike or calcium activity.
    *   Plotting utilities for raster plots, LFP, calcium traces, and connectivity graphs.
*   **Modularity and Extensibility:** Designed to easily add new neuron models, synapse types, plasticity rules, or analysis techniques.
*   **Jupyter Notebook Examples:** A comprehensive suite of examples from basic setup to advanced simulations.

## Installation

There are two primary ways to install `pyneurorg`:

### Option 1: Install from PyPI (Recommended for users)

If `pyneurorg` is published on the Python Package Index (PyPI), you can install it directly using `pip`. This is the simplest method for end-users.

```bash
pip install pyneurorg
```

### Option 2: Install from a local directory (For developers or from source)

If you have cloned the `pyneurorg` repository or have the source code:

1.  **Navigate to the top-level `pyneurorg` project directory in your terminal** (this is the directory that contains the `setup.py` file and the `src/` folder).
    ```bash
    cd path/to/your/pyneurorg_project_root
    ```

2.  **(Recommended) Create and activate a virtual environment:**
    ```bash
    python -m venv venv_pyneurorg
    source venv_pyneurorg/bin/activate  # On macOS/Linux
    # .\venv_pyneurorg\Scripts\activate  # On Windows
    ```

3.  **Install `pyneurorg` in editable mode and its dependencies:**
    The `-e` flag installs the package in "editable" mode. The `.` tells pip to look for `setup.py` in the current directory.
    ```bash
    pip install -e .
    ```
    This command reads `setup.py` (which should be configured for the `src/` layout) and installs dependencies listed in `setup.py` (which ideally reads them from `requirements.txt`).

    For a full development setup, including tools for testing, linting, and documentation:
    ```bash
    pip install -r requirements-dev.txt
    ```
    Or, if you have defined extras in your `setup.py` (e.g., `dev`, `docs`, `test`):
    ```bash
    pip install -e .[dev,docs,test]
   
    ```

## Project Directory Structure

The `pyneurorg` project is organized with a clear separation between the installable package code, documentation, examples, and tests. The main package code resides within the `src/` directory.

```
pyneurorg/
├── docs/
├── examples/
│   ├── 00_Installation_and_Setup.ipynb
│   ├── 01_Creating_Your_First_Organoid.ipynb
│   ├── 02_Running_a_Simple_Simulation_and_Recording_Spikes.ipynb
│   ├── 03_Exploring_Neuron_and_Synapse_Models.ipynb
│   ├── 04_Spatial_Arrangement_and_Connectivity_Rules.ipynb
│   ├── 05_MEA_Stimulation_and_Basic_Recording.ipynb
│   ├── 06_Simulating_Spontaneous_Activity_and_LFP_Proxy.ipynb
│   ├── 07_Patterned_Stimulation_and_Response_Analysis.ipynb
│   ├── 08_Implementing_Synaptic_Plasticity_STDP.ipynb
│   ├── 09_Simulating_Structural_Plasticity_Network_Formation.ipynb
│   ├── 10_Modeling_Calcium_Dynamics_and_Fluorescence_Imaging.ipynb
│   ├── 11_Data_Persistence_Saving_and_Loading_with_SQLite.ipynb
│   ├── 12_Inferring_Functional_Networks_from_Spike_Data.ipynb
│   ├── 13_Inferring_Functional_Networks_from_Calcium_Data.ipynb
│   ├── 14_Advanced_Analysis_Bursting_and_Synchrony.ipynb
│   └── 15_Example_Modeling_a_Simplified_Disease_Phenotype.ipynb
├── src/
│   └── pyneurorg/
│       ├── analysis/
│       ├── core/
│       ├── electrophysiology/
│       ├── mea/
│       ├── organoid/
│       ├── plasticity/
│       ├── simulation/
│       ├── utils/
│       └── visualization/
└── tests/
```

### Description of Top-Level Directories
*   **`docs/`**: Contains files for generating the project's official documentation (e.g., using Sphinx).
*   **`examples/`**: A collection of Jupyter Notebooks providing practical tutorials and demonstrating `pyneurorg` usage.
*   **`src/`**: Houses the source code of the `pyneurorg` Python package. Inside `src/`, the `pyneurorg/` subdirectory is the main package.
*   **`tests/`**: Contains automated tests (unit, integration) for the `pyneurorg` codebase.


## Usage

Refer to the Quick Start Examples or to the Jupyter Notebooks in the `examples/` directory for detailed usage instructions. Start with `00_Installation_and_Setup.ipynb`.


## Quick Start Examples

The following examples demonstrate basic functionalities of `pyneurorg`. Ensure `pyneurorg` is installed before running them.

### Stimulating the Organoid with an MEA

This snippet shows how to set up a simple organoid, an MEA, and stimulate a specific region.

```python
import brian2 as b2
import matplotlib.pyplot as plt
import numpy as np # Often needed with Brian2

# Assuming pyneurorg modules are importable
from pyneurorg.organoid.organoid import Organoid
from pyneurorg.organoid import spatial
from pyneurorg.core import neuron_models
from pyneurorg.mea.mea import MEA
from pyneurorg.simulation.simulator import Simulator
from pyneurorg.electrophysiology import stimulus_generator
from pyneurorg.visualization import spike_plotter

# Ensure reproducible results
b2.seed(423)
b2.prefs.codegen.target = 'numpy'

# 1. Create an Organoid
lif_model_definition = neuron_models.LIFNeuron(
    tau_m=20*b2.ms, v_rest=-65*b2.mV, v_reset=-65*b2.mV,
    v_thresh=-50*b2.mV, R_m=100*b2.Mohm, I_tonic=0.0*b2.nA,
    refractory_period=2*b2.ms
)
my_organoid_stim = Organoid(name="StimulationOrganoid")
neuron_positions_stim = spatial.random_positions_in_sphere(N=100, radius=150*b2.um)
my_organoid_stim.add_neurons(
    name="target_neurons", num_neurons=100, model_name="LIFNeuron",
    model_params={
        'tau_m': 20*b2.ms, 'v_rest': -65*b2.mV, 'v_reset': -65*b2.mV,
        'v_thresh': -50*b2.mV, 'R_m': 100*b2.Mohm, 'I_tonic': 0.0*b2.nA,
        'refractory_period': 2*b2.ms
    },
    positions=neuron_positions_stim, initial_values={'v': -65*b2.mV}
)

# 2. Create an MEA
electrode_coords = [(i*40*b2.um, j*40*b2.um, 0*b2.um) for i in range(4) for j in range(4)]
my_mea_stim = MEA(electrode_positions=electrode_coords)

# 3. Setup the Simulator
sim_stim = Simulator(organoid=my_organoid_stim, mea=my_mea_stim, brian2_dt=0.1*b2.ms)

# 4. Define a stimulus
stimulation_duration = 150*b2.ms
stimulus_waveform = stimulus_generator.create_pulse_train(
    amplitude=0.9*b2.nA, frequency=8*b2.Hz,
    pulse_width=2.5*b2.ms, duration=stimulation_duration,
    dt=sim_stim.brian_dt
)

# 5. Add stimulus to an MEA electrode
sim_stim.add_stimulus(
    electrode_id=0, stimulus_waveform=stimulus_waveform,
    target_group_name="target_neurons", influence_radius=50*b2.um
)

# 6. Add a spike monitor
sim_stim.add_recording(
    monitor_name="stimulation_spikes", monitor_type="spike",
    target_group_name="target_neurons", record=True
)

# 7. Run simulation
print("Running MEA stimulation example...")
sim_stim.run(stimulation_duration, report='text', report_period=50*b2.ms)
print("Stimulation simulation finished.")

# 8. Retrieve and plot data
spike_data = sim_stim.get_data("stimulation_spikes")
print(f"Recorded {len(spike_data.i)} spikes during stimulation.")
if len(spike_data.i) > 0:
    fig, ax = plt.subplots(figsize=(10,5))
    spike_plotter.plot_raster(
        spike_indices=spike_data.i, spike_times=spike_data.t,
        duration=stimulation_duration, ax=ax,
        title="Spikes from MEA Stimulation", marker_size=3
    )
    plt.tight_layout()
    plt.show()
else:
    print("No spikes recorded. Try increasing stimulus amplitude or influence_radius.")
```

### Reading Activity: Spikes and Calcium Imaging (Full Example)

This snippet demonstrates recording spikes and simulated calcium fluorescence from active neurons.

```python
import brian2 as b2
import numpy as np
import matplotlib.pyplot as plt

# Assuming pyneurorg modules are importable
from pyneurorg.organoid.organoid import Organoid
from pyneurorg.organoid import spatial
from pyneurorg.core import neuron_models
from pyneurorg.simulation.simulator import Simulator
from pyneurorg.visualization import spike_plotter, calcium_plotter
from pyneurorg.analysis import calcium_analysis

# Ensure reproducible results
b2.seed(12346) # Different seed
np.random.seed(12346)
b2.prefs.codegen.target = 'numpy'

# 1. Define parameters and get the calcium-enabled neuron model definition
# These parameters should match what your LIFCalciumFluorNeuron function expects
calcium_model_function_params = {
    'tau_m': 15*b2.ms, 'v_rest': -65*b2.mV, 'v_reset': -65*b2.mV, 'v_thresh': -50*b2.mV,
    'R_m': 120*b2.Mohm, 'refractory_period': 3*b2.ms,
    'tau_ca': 80*b2.ms,          # Example calcium decay time constant
    'ca_spike_increment': 0.25, # Example arbitrary unit increment of Ca per spike (unitless or specific based on model)
    'tau_f': 120*b2.ms,          # Example fluorescence decay (related to indicator off-rate)
    'k_f': 0.6,                  # Example scaling factor for fluorescence from Ca (unitless or specific)
    'I_tonic': 0.21*b2.nA        # Tonic current to induce spontaneous spiking
}
try:
    # Fetch the model definition dictionary
    calcium_model_def = neuron_models.LIFCalciumFluorNeuron(**calcium_model_function_params)
    model_name_for_organoid = "LIFCalciumFluorNeuron" # Use the function name string for Organoid
except AttributeError:
    print("CRITICAL ERROR: 'LIFCalciumFluorNeuron' model function not found in pyneurorg.core.neuron_models.")
    print("This example cannot proceed without it for calcium imaging simulation.")
    # To prevent error in a batch run of README, could raise SystemExit or use a fallback
    # For now, let's assume it exists for a "real" example.
    raise SystemExit("LIFCalciumFluorNeuron model is required for this example.")


# 2. Create an Organoid
calcium_activity_organoid = Organoid(name="CalciumActivityOrganoid")
num_activity_neurons = 20 # Smaller number for clearer Vm/Ca plots
activity_positions = spatial.random_positions_in_cube(N=num_activity_neurons, side_length=80*b2.um)

# Initial membrane potentials varied to desynchronize initial firing
initial_v_activity = np.random.uniform(-65, -55, num_activity_neurons) * b2.mV
# Initial calcium and fluorescence (assuming they start at baseline, e.g., 0)
initial_ca = calcium_model_def['namespace'].get('Ca_default_init', 0.0)
initial_f = calcium_model_def['namespace'].get('F_default_init', 0.0)

active_neurons_group = calcium_activity_organoid.add_neurons(
    name="active_ca_neurons",
    num_neurons=num_activity_neurons,
    model_name=model_name_for_organoid, # Pass the string name
    model_params=calcium_model_function_params, # Pass the parameters for the model function
    positions=activity_positions,
    initial_values={
        'v': initial_v_activity,
        'Ca': initial_ca, # Assuming 'Ca' is a state variable in the model
        'F': initial_f    # Assuming 'F' is a state variable in the model
    }
)

# 3. Setup the Simulator
sim_activity = Simulator(organoid=calcium_activity_organoid, brian2_dt=0.1*b2.ms)
# sim_activity.setup_simulation_entry(...) # For SQLite logging

# 4. Add SpikeMonitor for all neurons in the group
sim_activity.add_recording(
    monitor_name="activity_spikes",
    monitor_type="spike",
    target_group_name="active_ca_neurons",
    record=True
)

# 5. Add StateMonitor for Vm, Ca, and F for a subset of neurons
# Record from first few neurons, or all if num_activity_neurons is small
indices_to_record_state = list(range(min(3, num_activity_neurons)))
if indices_to_record_state: # Only add if there are neurons to record
    sim_activity.add_recording(
        monitor_name="activity_states",
        monitor_type="state",
        target_group_name="active_ca_neurons",
        variables_to_record=['v', 'Ca', 'F'], # Must match variables in neuron model
        record_indices=indices_to_record_state,
        dt=0.2*b2.ms # Record states at a slightly lower frequency than simulation dt
    )
else:
    print("No neurons selected for state recording.")


# 6. Run simulation
activity_simulation_duration = 600*b2.ms
print(f"\nRunning activity and calcium imaging example for {activity_simulation_duration}...")
sim_activity.run(activity_simulation_duration, report='text', report_period=100*b2.ms)
print("Activity and calcium simulation finished.")

# 7. Retrieve and Plot Spike Data
spike_data_activity = sim_activity.get_data("activity_spikes")
print(f"Activity example recorded {len(spike_data_activity.i)} spikes.")

if len(spike_data_activity.i) > 0:
    fig_spikes_act, ax_spikes_act = plt.subplots(figsize=(10,4))
    spike_plotter.plot_raster(
        spike_indices=spike_data_activity.i,
        spike_times=spike_data_activity.t,
        duration=activity_simulation_duration,
        ax=ax_spikes_act,
        title="Spikes from Active Calcium-Model Neurons"
    )
    plt.tight_layout()
    plt.show()

# 8. Retrieve, Process, and Plot Vm, Calcium, and Fluorescence Data
if "activity_states" in sim_activity.monitors:
    state_data_activity = sim_activity.get_data("activity_states")
    time_pts_ms = state_data_activity.t / b2.ms

    # Plot Vm
    fig_vm, ax_vm = plt.subplots(figsize=(12,4))
    if hasattr(state_data_activity, 'v'):
        for i in range(state_data_activity.v.shape[0]):
            original_idx = indices_to_record_state[i]
            ax_vm.plot(time_pts_ms, state_data_activity.v[i,:] / b2.mV, label=f"Neuron {original_idx}")
        ax_vm.set_xlabel("Time (ms)"); ax_vm.set_ylabel("Vm (mV)")
        ax_vm.set_title("Membrane Potential (Vm) Traces"); ax_vm.legend(fontsize='small')
        plt.tight_layout(); plt.show()

    # Plot raw Ca and F traces
    if hasattr(state_data_activity, 'Ca') and hasattr(state_data_activity, 'F'):
        fig_ca_f, axes_ca_f = plt.subplots(2, 1, sharex=True, figsize=(12, 6))
        for i in range(state_data_activity.F.shape[0]): # Assuming F and Ca have same shape[0]
            original_idx = indices_to_record_state[i]
            axes_ca_f[0].plot(time_pts_ms, state_data_activity.F[i,:], label=f"Neuron {original_idx}")
            axes_ca_f[1].plot(time_pts_ms, state_data_activity.Ca[i,:], label=f"Neuron {original_idx}")
        axes_ca_f[0].set_ylabel("Fluorescence (F arbitrary units)")
        axes_ca_f[0].set_title("Raw Fluorescence Traces")
        axes_ca_f[0].legend(fontsize='small')
        axes_ca_f[1].set_ylabel("Calcium (Ca arbitrary units)")
        axes_ca_f[1].set_xlabel("Time (ms)")
        axes_ca_f[1].set_title("Raw Intracellular Calcium Traces")
        axes_ca_f[1].legend(fontsize='small')
        plt.tight_layout(); plt.show()

        # Calculate and plot ΔF/F
        try:
            # Using the placeholder ΔF/F calculation from previous response
            F_traces_np = np.array(state_data_activity.F)
            delta_F_F_traces_list = []
            for i_trace in range(F_traces_np.shape[0]):
                f_single_trace = F_traces_np[i_trace,:]
                baseline_end_idx = max(1, int(0.1 * len(f_single_trace))) # Use first 10% as baseline F0
                f0 = np.mean(f_single_trace[:baseline_end_idx])
                if abs(f0) < 1e-9: f0 = 1e-9 # Avoid division by zero or very small F0
                delta_F_F_traces_list.append((f_single_trace - f0) / f0)
            delta_F_F_traces_np = np.array(delta_F_F_traces_list)

            if delta_F_F_traces_np.size > 0:
                fig_dff, ax_dff = plt.subplots(figsize=(12,4))
                traces_dict_for_plotter = {
                    indices_to_record_state[i]: delta_F_F_traces_np[i,:] for i in range(delta_F_F_traces_np.shape[0])
                }
                # Assuming calcium_plotter.plot_calcium_traces can take a dict of traces
                # If not, plot directly:
                for i_plot in range(delta_F_F_traces_np.shape[0]):
                    ax_dff.plot(time_pts_ms, delta_F_F_traces_np[i_plot,:], label=f"Neuron {indices_to_record_state[i_plot]}")
                
                ax_dff.set_xlabel("Time (ms)"); ax_dff.set_ylabel("ΔF/F")
                ax_dff.set_title("Simulated ΔF/F Traces"); ax_dff.legend(fontsize='small')
                plt.tight_layout(); plt.show()

        except AttributeError as e_dff_attr:
            print(f"Note: Could not plot ΔF/F. A required analysis function might be missing: {e_dff_attr}")
        except Exception as e_dff:
            print(f"An error occurred during ΔF/F processing or plotting: {e_dff}")
    else:
        print("Fluorescence (F) or Calcium (Ca) variables not found in recorded states.")
else:
    print("State monitor 'activity_states' not found or no data to plot.")

# if hasattr(sim_activity, 'close'): sim_activity.close()
```


## Overview of Example Notebooks (`examples/`)

The `examples/` directory provides a guided tour through `pyneurorg`'s features:

*   **`00_Installation_and_Setup.ipynb`**: Guides users through the installation process of `pyneurorg` and its dependencies, and includes a basic test to confirm a working setup.
*   **`01_Creating_Your_First_Organoid.ipynb`**: Introduces the `Organoid` class, demonstrating how to define neuronal populations, assign spatial positions, and conceptually add synapses.
*   **`02_Running_a_Simple_Simulation_and_Recording_Spikes.ipynb`**: Shows how to use the `Simulator` class to run a basic simulation of a created organoid and record neuronal spikes and membrane potentials.
*   **`03_Exploring_Neuron_and_Synapse_Models.ipynb`**: Details the various predefined neuron and synapse models available in `pyneurorg.core` and how to customize their parameters.
*   **`04_Spatial_Arrangement_and_Connectivity_Rules.ipynb`**: Focuses on creating 3D spatial layouts for neurons and defining rules for establishing synaptic connections between them (e.g., based on distance or probability).
*   **`05_MEA_Stimulation_and_Basic_Recording.ipynb`**: Demonstrates how to model a Microelectrode Array (MEA), simulate electrical stimulation of the organoid via MEA electrodes, and record activity.
*   **`06_Simulating_Spontaneous_Activity_and_LFP_Proxy.ipynb`**: Illustrates setting up a more complex network (e.g., with excitatory/inhibitory balance) to generate spontaneous activity and compute a proxy for Local Field Potentials (LFP).
*   **`07_Patterned_Stimulation_and_Response_Analysis.ipynb`**: Shows how to use the `stimulus_generator` to create complex temporal patterns of stimulation and analyze the network's response (e.g., PSTH).
*   **`08_Implementing_Synaptic_Plasticity_STDP.ipynb`**: Explains how to incorporate Spike-Timing-Dependent Plasticity (STDP) rules to modify synaptic strengths based on activity.
*   **`09_Simulating_Structural_Plasticity_Network_Formation.ipynb`**: Covers the simulation of structural changes in the network, such as the activity-dependent formation and pruning of synapses.
*   **`10_Modeling_Calcium_Dynamics_and_Fluorescence_Imaging.ipynb`**: Details how to use neuron models that include intracellular calcium dynamics and simulate the corresponding fluorescence signals from indicators like GCaMP.
*   **`11_Data_Persistence_Saving_and_Loading_with_SQLite.ipynb`**: Demonstrates how to save simulation results (metadata, spikes, state variables) to an SQLite database and load them back for later analysis.
*   **`12_Inferring_Functional_Networks_from_Spike_Data.ipynb`**: Shows how to use analysis tools to infer functional connectivity maps from recorded spike train data (e.g., using STTC or cross-correlation).
*   **`13_Inferring_Functional_Networks_from_Calcium_Data.ipynb`**: Similar to the above, but demonstrates inferring functional networks from simulated calcium imaging data.
*   **`14_Advanced_Analysis_Bursting_and_Synchrony.ipynb`**: Covers more advanced analysis techniques, such as detecting bursting patterns in neuronal activity and quantifying network synchrony.
*   **`15_Example_Modeling_a_Simplified_Disease_Phenotype.ipynb`**: Provides an example of how `pyneurorg` can be used to model and investigate network alterations associated with a simplified disease phenotype.


## License

This project is licensed under the MIT License.
