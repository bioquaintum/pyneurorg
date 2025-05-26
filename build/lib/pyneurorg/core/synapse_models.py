# pyneurorg/core/synapse_models.py

"""
Collection of predefined synapse models for use with Brian2 in pyneurorg simulations.

Each function in this module returns a dictionary containing the necessary
components (model equations, on_pre/on_post actions, namespace) to define
a `brian2.Synapses` object.

These models are typically conductance-based, meaning they modulate a conductance
in the postsynaptic neuron, which then drives a current based on the reversal
potential and the postsynaptic membrane potential. The postsynaptic neuron model
is expected to have a current term like `g_syn_type * (E_rev_syn_type - v_post)`,
where `g_syn_type` is the target conductance variable (e.g., `g_exc`, `g_inh`)
modified by these synapses.
"""

import brian2 as b2

def StaticConductanceSynapse(weight=1.0*b2.nS, target_conductance_var='g_exc'):
    """
    Defines a static, instantaneous conductance-based synapse.

    A presynaptic spike causes an immediate, fixed increase in the target
    conductance variable of the postsynaptic neuron. This conductance does not
    decay over time unless explicitly reset by other mechanisms in the
    postsynaptic neuron (which is not typical for this simple model; usually
    the impact is considered part of the neuron's integration over a time step).

    To have a decaying effect, use `ExponentialConductanceSynapse`.

    Parameters
    ----------
    weight : brian2.units.fundamentalunits.Quantity, optional
        The amount of conductance to add to the postsynaptic neuron upon
        a presynaptic spike (default: 1.0 nS). This is the synaptic weight.
    target_conductance_var : str, optional
        The name of the conductance variable in the postsynaptic neuron's model
        that this synapse will modify (e.g., 'g_exc' for excitatory,
        'g_inh' for inhibitory). (default: 'g_exc').

    Returns
    -------
    dict
        A dictionary containing:
        - 'model' (str): Equations for synaptic variables (empty for this model).
        - 'on_pre' (str): Action to take on a presynaptic spike.
        - 'namespace' (dict): Default parameters for the synapse model.

    Notes
    -----
    The postsynaptic neuron model should include a term that uses this
    `target_conductance_var`, for example:
    `I_syn = g_exc * (E_exc - v)`
    `dv/dt = (... - I_syn ... ) / C_m`
    The weight `w_syn` is defined per-synapse and can be heterogeneous.
    """
    # The model itself has no differential equations for the synapse state.
    # The 'weight' is a parameter of the Synapses object.
    # We define 'w_syn' as a per-synapse parameter.
    model_eqs = """
    w_syn : siemens (constant) # Synaptic weight
    """

    on_pre_action = f'{target_conductance_var}_post += w_syn'

    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {
            # Default weight value if not set per synapse during connection
            # However, Brian2 Synapses usually expects weights to be set during
            # connect or via S.w_syn = ...
            # This namespace is more for parameters within the equations.
            # The 'w_syn' in model_eqs declares it as a parameter.
            # Let's assume the weight will be assigned during S.connect() or S.w_syn = ...
            # For clarity, we can provide a default for w_syn if it were a global param,
            # but as a per-synapse variable, it's better set individually.
            # For now, the namespace can be empty or hold other global params if any.
        },
        # 'parameters': {'w_syn': weight} # Brian2 handles this differently.
                                        # w_syn will be a parameter of the Synapses instance.
                                        # The `weight` argument to this function can be used
                                        # by the NetworkBuilder when setting up S.w_syn.
    }


def ExponentialConductanceSynapse(tau_syn=5*b2.ms, weight_increment=0.5*b2.nS,
                                  target_conductance_var='g_exc'):
    """
    Defines a conductance-based synapse with exponential decay.

    A presynaptic spike causes an instantaneous increase in the target
    conductance of the postsynaptic neuron by `weight_increment`. This
    conductance then decays exponentially back to zero with a time
    constant `tau_syn`.

    Parameters
    ----------
    tau_syn : brian2.units.fundamentalunits.Quantity, optional
        The decay time constant of the synaptic conductance (default: 5 ms).
    weight_increment : brian2.units.fundamentalunits.Quantity, optional
        The amount of conductance added to `target_conductance_var` upon
        a presynaptic spike. This acts as the synaptic strength for a single event.
        (default: 0.5 nS).
    target_conductance_var : str, optional
        The name of the conductance variable in the postsynaptic neuron's model
        that this synapse will represent and modify. This variable will have its
        own differential equation. (e.g., 'g_exc' for excitatory,
        'g_inh' for inhibitory). (default: 'g_exc').

    Returns
    -------
    dict
        A dictionary containing:
        - 'model' (str): Equations for synaptic variables.
        - 'on_pre' (str): Action to take on a presynaptic spike.
        - 'namespace' (dict): Default parameters for the synapse model.
        - 'method' (str): Suggested integration method for synaptic equations.

    Notes
    -----
    The `model` string defines the differential equation for the
    `target_conductance_var` itself within the Synapses object.
    The postsynaptic neuron's equations should then simply use this variable,
    e.g., `I_syn = g_exc_total * (E_exc - v)`.
    The `target_conductance_var` specified here will become a summed
    postsynaptic variable.
    The `w_inc` is defined as a per-synapse parameter for the increment.
    """
    # The target_conductance_var is a postsynaptic variable summed from all incoming synapses.
    # Its dynamics are defined here.
    model_eqs = f"""
    d{target_conductance_var}_syn_total/dt = -{target_conductance_var}_syn_total / tau_syn_val : siemens (clock-driven)
    w_inc : siemens (constant) # Weight increment per spike for this specific synapse
    """
    # The _post suffix is not needed here as target_conductance_var_syn_total is a postsynaptic variable
    # managed by the Synapses object. Brian2 handles linking it.

    on_pre_action = f'{target_conductance_var}_syn_total += w_inc'
    # In the postsynaptic neuron, you'd use target_conductance_var_syn_total.
    # For example, if target_conductance_var='g_exc', the neuron model uses 'g_exc_syn_total'.
    # The NetworkBuilder or Organoid class will need to ensure the postsynaptic neuron
    # has a variable like `g_exc_summed : siemens` and the Synapses object maps
    # `g_exc_syn_total` to `g_exc_summed_post`.
    #
    # A more direct way for Brian2 to handle summed variables:
    # If target_conductance_var is 'g_exc', the Synapses object can define:
    # dg_exc_syn/dt = -g_exc_syn / tau_syn_val : siemens (summed)
    # on_pre = 'g_exc_syn_post += w_inc'
    # And the postsynaptic neuron has 'g_exc_syn : siemens' in its equations.
    #
    # Let's adopt this simpler approach for Brian2.
    # The variable defined in the synapse model is directly linked to the postsynaptic neuron.
    # The `(summed)` keyword tells Brian2 to sum inputs from multiple synapses.

    model_eqs_revised = f"""
    d{target_conductance_var}/dt = -{target_conductance_var} / tau_syn_val : siemens (summed)
    w_inc : siemens (constant) # Weight increment per spike for this specific synapse
    """
    on_pre_action_revised = f'{target_conductance_var}_post += w_inc'
    # The postsynaptic neuron should then have a variable named exactly `target_conductance_var` (e.g., `g_exc : siemens`).

    return {
        'model': model_eqs_revised,
        'on_pre': on_pre_action_revised,
        'namespace': {
            'tau_syn_val': tau_syn,
            # w_inc is a per-synapse parameter.
            # The `weight_increment` arg can be used as a default when creating connections.
        },
        'method': 'exact' # Exponential decay can be solved exactly
    }

# You can add more synapse models here, e.g., for short-term plasticity (STP)
# or more complex dynamics.
