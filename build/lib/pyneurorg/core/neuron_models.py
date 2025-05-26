# pyneurorg/core/neuron_models.py

"""
Collection of predefined neuron models for use with Brian2 in pyneurorg simulations.

Each function in this module returns a dictionary containing the necessary
components (equations, parameters, threshold, reset conditions, refractory period,
and integration method) to define a `brian2.NeuronGroup`.
"""

import brian2 as b2

def LIFNeuron(tau_m=10*b2.ms, v_rest=0*b2.mV, v_reset=0*b2.mV,
              v_thresh=20*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
              refractory_period=2*b2.ms):
    """
    Defines a Leaky Integrate-and-Fire (LIF) neuron model.

    Parameters
    ----------
    tau_m : brian2.units.fundamentalunits.Quantity, optional
        Membrane time constant (default: 10 ms).
    v_rest : brian2.units.fundamentalunits.Quantity, optional
        Resting membrane potential (default: 0 mV).
    v_reset : brian2.units.fundamentalunits.Quantity, optional
        Reset potential after a spike (default: 0 mV).
    v_thresh : brian2.units.fundamentalunits.Quantity, optional
        Spike threshold (default: 20 mV).
    R_m : brian2.units.fundamentalunits.Quantity, optional
        Membrane resistance (default: 100 MOhm).
    I_tonic : brian2.units.fundamentalunits.Quantity, optional
        Constant tonic current injected into the neuron (default: 0 nA).
    refractory_period : brian2.units.fundamentalunits.Quantity, optional
        Absolute refractory period after a spike (default: 2 ms).

    Returns
    -------
    dict
        A dictionary containing:
        - 'model' (str): The differential equations for the model.
        - 'threshold' (str): The condition for spiking.
        - 'reset' (str): The actions to take after a spike.
        - 'refractory' (brian2.units.fundamentalunits.Quantity): Refractory period.
        - 'namespace' (dict): Default parameters for the model.
        - 'method' (str): Suggested integration method.
    """
    eqs = """
    dv/dt = (-(v - v_rest_val) + R_m_val * I_input + R_m_val * I_tonic_val) / tau_m_val : volt (unless refractory)
    I_input : amp # Input current, to be driven by synapses or external sources
    """
    return {
        'model': eqs,
        'threshold': f'v > {v_thresh!r}',
        'reset': f'v = {v_reset!r}',
        'refractory': refractory_period,
        'namespace': {
            'tau_m_val': tau_m,
            'v_rest_val': v_rest,
            'R_m_val': R_m,
            'I_tonic_val': I_tonic,
        },
        'method': 'exact'
    }


def IzhikevichNeuron(a=0.02/b2.ms, b=0.2*b2.nS, c=-65*b2.mV, d=2*b2.pA,
                     v_init=-70*b2.mV, u_init=None, C_m=100*b2.pF,
                     k=0.7*b2.nS/b2.mV, v_rest_iz=-60*b2.mV, v_thresh_iz=-40*b2.mV,
                     v_peak=30*b2.mV, I_tonic=0*b2.pA):
    """
    Defines an Izhikevich neuron model.

    Parameters are chosen such that `u` is a current (in Amps).

    Parameters
    ----------
    a : brian2.units.fundamentalunits.Quantity, optional
        Timescale of the recovery variable `u` (default: 0.02/ms).
    b : brian2.units.fundamentalunits.Quantity, optional
        Sensitivity of `u` to `v`. `b*(v - v_rest_iz)` is a current. (default: 0.2 nS).
    c : brian2.units.fundamentalunits.Quantity, optional
        After-spike reset value of `v` (default: -65 mV).
    d : brian2.units.fundamentalunits.Quantity, optional
        After-spike reset increment for `u` (a current) (default: 2 pA).
    v_init : brian2.units.fundamentalunits.Quantity, optional
        Initial membrane potential (default: -70 mV).
    u_init : brian2.units.fundamentalunits.Quantity, optional
        Initial recovery variable (current). If None, set to `b * (v_init - v_rest_iz)`
        (default: None).
    C_m : brian2.units.fundamentalunits.Quantity, optional
        Membrane capacitance (default: 100 pF).
    k : brian2.units.fundamentalunits.Quantity, optional
        Scaling factor for the quadratic term, (nS/mV) or (A/V^2) (default: 0.7 nS/mV).
    v_rest_iz : brian2.units.fundamentalunits.Quantity, optional
        Resting potential used in the quadratic term (default: -60 mV).
    v_thresh_iz : brian2.units.fundamentalunits.Quantity, optional
        Instantaneous threshold potential used in the quadratic term (default: -40 mV).
    v_peak : brian2.units.fundamentalunits.Quantity, optional
        Spike cutoff value (threshold for reset condition) (default: 30 mV).
    I_tonic : brian2.units.fundamentalunits.Quantity, optional
        Constant tonic current injected into the neuron (default: 0 pA).

    Returns
    -------
    dict
        A dictionary for `brian2.NeuronGroup` definition.
    """
    if u_init is None:
        u_init_val = b * (v_init - v_rest_iz)
    else:
        u_init_val = u_init

    eqs = """
    dv/dt = (k_val * (v - v_rest_iz_val) * (v - v_thresh_iz_val) - u + I_input + I_tonic_val) / C_m_val : volt
    du/dt = a_val * (b_val * (v - v_rest_iz_val) - u) : amp / second
    I_input : amp
    """
    return {
        'model': eqs,
        'threshold': f'v >= {v_peak!r}',
        'reset': f'v = {c!r}; u += {d!r}',
        'namespace': {
            'a_val': a,
            'b_val': b,
            'k_val': k,
            'C_m_val': C_m,
            'v_rest_iz_val': v_rest_iz,
            'v_thresh_iz_val': v_thresh_iz,
            'I_tonic_val': I_tonic,
            'v_default_init': v_init, # For NeuronGroup initialization
            'u_default_init': u_init_val, # For NeuronGroup initialization
        },
        'method': 'euler'
    }


def AdExNeuron(C_m=281*b2.pF, g_L=30*b2.nS, E_L=-70.6*b2.mV,
               V_T=-50.4*b2.mV, Delta_T=2*b2.mV, tau_w=144*b2.ms,
               a=4*b2.nS, b=0.0805*b2.nA, V_reset=-70.6*b2.mV,
               V_peak=0*b2.mV, I_tonic=0*b2.nA, refractory_period=0*b2.ms):
    """
    Defines an Adaptive Exponential Integrate-and-Fire (AdEx) neuron model.

    Based on Brette and Gerstner (2005).

    Parameters
    ----------
    C_m : brian2.units.fundamentalunits.Quantity, optional
        Membrane capacitance (default: 281 pF).
    g_L : brian2.units.fundamentalunits.Quantity, optional
        Leak conductance (default: 30 nS).
    E_L : brian2.units.fundamentalunits.Quantity, optional
        Leak reversal potential (equilibrium potential) (default: -70.6 mV).
    V_T : brian2.units.fundamentalunits.Quantity, optional
        Spike initiation threshold (default: -50.4 mV).
    Delta_T : brian2.units.fundamentalunits.Quantity, optional
        Sharpness of spike initiation (default: 2 mV).
    tau_w : brian2.units.fundamentalunits.Quantity, optional
        Time constant of the adaptation variable `w` (default: 144 ms).
    a : brian2.units.fundamentalunits.Quantity, optional
        Subthreshold adaptation coupling parameter (conductance) (default: 4 nS).
    b : brian2.units.fundamentalunits.Quantity, optional
        Spike-triggered adaptation increment (current) (default: 0.0805 nA).
    V_reset : brian2.units.fundamentalunits.Quantity, optional
        Reset potential after a spike (default: -70.6 mV).
    V_peak : brian2.units.fundamentalunits.Quantity, optional
        Voltage at which a spike is considered to have occurred for reset purposes
        (often set higher than V_T, e.g., 0 mV or 20 mV). (default: 0mV)
    I_tonic : brian2.units.fundamentalunits.Quantity, optional
        Constant tonic current (default: 0 nA).
    refractory_period : brian2.units.fundamentalunits.Quantity, optional
        Absolute refractory period (default: 0 ms, AdEx often handles this implicitly
        or a small value can be added if explicit refractoriness is desired).

    Returns
    -------
    dict
        A dictionary for `brian2.NeuronGroup` definition.
    """
    eqs = """
    dv/dt = (g_L_val * (E_L_val - v) + g_L_val * Delta_T_val * exp((v - V_T_val)/Delta_T_val) - w + I_input + I_tonic_val) / C_m_val : volt (unless refractory)
    dw/dt = (a_val * (v - E_L_val) - w) / tau_w_val : amp (unless refractory)
    I_input : amp
    """
    # Note on w units: dw/dt = (a*(v-EL) - w)/tau_w.
    # If a is conductance (S), a*(v-EL) is current (A). So w must be current (A).
    # tau_w is time (s). So dw/dt is A/s. This is consistent.

    return {
        'model': eqs,
        'threshold': f'v > {V_peak!r}', # V_peak acts as the numerical threshold for spike detection
        'reset': f'v = {V_reset!r}; w += {b!r}',
        'refractory': refractory_period,
        'namespace': {
            'C_m_val': C_m,
            'g_L_val': g_L,
            'E_L_val': E_L,
            'V_T_val': V_T,
            'Delta_T_val': Delta_T,
            'tau_w_val': tau_w,
            'a_val': a,
            # b, V_reset, V_peak are in reset/threshold strings
            'I_tonic_val': I_tonic,
            # Default initial values (can be overridden in NeuronGroup)
            'v_default_init': E_L, # Often start at resting potential
            'w_default_init': 0*b2.nA, # Often start w at 0 or a_val * (E_L_val - E_L_val)
        },
        'method': 'euler' # AdEx often requires a numerical solver like Euler or RK
    }


def QIFNeuron(tau_m=20*b2.ms, v_rest=0*b2.mV, v_c=10*b2.mV,
              v_reset=-10*b2.mV, v_peak=30*b2.mV, R_m=100*b2.Mohm,
              I_tonic=0*b2.nA, refractory_period=1*b2.ms):
    """
    Defines a Quadratic Integrate-and-Fire (QIF) neuron model.

    A canonical model for Type I excitability.
    dv/dt = ( (v - v_rest)^2 / (v_c - v_rest) + R_m * I_input ) / tau_m
    This form is from Gerstner et al., Neuronal Dynamics (Chapter 4.2).
    Alternatively, dv/dt = k*(v - v_rest)*(v - v_thresh) + I_eff (like Izhikevich without 'u').
    Let's use a common simpler form: dv/dt = v^2 + I_eff (after normalization).
    For Brian2 with units: C dv/dt = alpha * (v - v_rest)^2 + I_input
    Or, dv/dt = (alpha_norm * (v - v_rest_val)^2 + I_input_norm_or_current*R) / tau_m

    Let's use a form dv/dt = ( (v-v_rest_val)*(v-v_critical_val) + R_m_val * (I_input + I_tonic_val) ) / tau_m_val
    where v_critical_val is another parameter.
    If v_critical_val = v_rest_val, it's like v^2 + I.

    Parameters
    ----------
    tau_m : brian2.units.fundamentalunits.Quantity, optional
        Membrane time constant (default: 20 ms).
    v_rest : brian2.units.fundamentalunits.Quantity, optional
        Effective resting potential or one root of the quadratic (default: 0 mV).
    v_c : brian2.units.fundamentalunits.Quantity, optional
        Critical voltage or second root of the quadratic, where dv/dt slope changes.
        Acts like an effective threshold (default: 10 mV).
        If I_input is zero, for v between v_rest and v_c, dv/dt can be negative.
        For v > v_c, dv/dt becomes positive and grows quadratically.
    v_reset : brian2.units.fundamentalunits.Quantity, optional
        Reset potential after a spike (default: -10 mV).
    v_peak : brian2.units.fundamentalunits.Quantity, optional
        Spike cutoff value (default: 30 mV).
    R_m : brian2.units.fundamentalunits.Quantity, optional
        Membrane resistance, scales input current (default: 100 MOhm).
    I_tonic : brian2.units.fundamentalunits.Quantity, optional
        Constant tonic current (default: 0 nA).
    refractory_period : brian2.units.fundamentalunits.Quantity, optional
        Absolute refractory period (default: 1 ms).

    Returns
    -------
    dict
        A dictionary for `brian2.NeuronGroup` definition.
    """
    # The term (v-v_rest)*(v-v_c) needs a scaling factor with units of 1/volt
    # to make the whole term a voltage, then divide by tau_m to get V/s.
    # So, dv/dt = (k_q * (v-v_rest_val)*(v-v_critical_val) + R_m_val * (I_input + I_tonic_val) ) / tau_m_val
    # where k_q has units of 1 (dimensionless) if (v-vr)(v-vc) is considered a current scaled by R_m.
    # Or more directly: dv/dt = ( (v-v_rest_val)*(v-v_critical_val)/some_volt_scale + R_m_val * (I_input + I_tonic_val) ) / tau_m_val
    # Let's set some_volt_scale = 1*b2.volt for simplicity for now. The user can adjust parameters.
    # A common form is C dv/dt = I_rh + I_0 + k(v-v_rh)^2
    # Or dv/dt = A*(v-v_rest)^2 + B*I_input
    # Let's use: C dv/dt = g_q * (v - v_rest_val) * (v - v_critical_val) + I_input + I_tonic_val
    # where g_q would have units of S/V or A/V^2 (like 'k' in Izhikevich).
    # Or tau_m dv/dt = (v - v_rest_val) * (v - v_critical_val) / (1*volt) + R_m_val * (I_input + I_tonic_val)
    # This makes the quadratic term dimensionless * volt.

    # Using scaling_factor_qif (dimensionless) to adjust magnitude of quadratic term
    # scaling_factor_qif = 1.0 as default
    # dv/dt = ( scaling_factor_qif * (v - v_rest_val) * (v - v_critical_val) / (1*b2.volt) + R_m_val * (I_input + I_tonic_val) ) / tau_m_val
    # This makes (v-vr)(v-vc)/(1V) effectively dimensionless, then *1V for the term, then /tau_m.

    eqs = """
    dv/dt = ( (v - v_rest_val) * (v - v_critical_val) / (1*volt) + R_m_val * (I_input + I_tonic_val) ) / tau_m_val : volt (unless refractory)
    I_input : amp
    """
    # The 1*volt term is a common way to normalize the quadratic part.
    # Effectively, if v is in mV, then (v-vr)(v-vc) is mV^2. Dividing by 1V (1000mV) scales it down.
    # This makes the quadratic term (unitless_value * mV). Then the whole numerator is mV.

    return {
        'model': eqs,
        'threshold': f'v >= {v_peak!r}',
        'reset': f'v = {v_reset!r}',
        'refractory': refractory_period,
        'namespace': {
            'tau_m_val': tau_m,
            'v_rest_val': v_rest,
            'v_critical_val': v_c,
            'R_m_val': R_m,
            'I_tonic_val': I_tonic,
            'v_default_init': v_rest,
        },
        'method': 'euler' # QIF typically requires numerical integration
    }


def SimpleHHNeuron(C_m=1*b2.uF/b2.cm**2, E_Na=50*b2.mV, E_K=-77*b2.mV, E_L=-54.4*b2.mV,
                   g_Na_bar=120*b2.mS/b2.cm**2, g_K_bar=36*b2.mS/b2.cm**2, g_L_bar=0.3*b2.mS/b2.cm**2,
                   V_T_hh=-60*b2.mV, I_tonic=0*b2.uA/b2.cm**2, refractory_period=0*b2.ms):
    """
    Defines a simplified Hodgkin-Huxley (HH) type neuron model.

    Focuses on Na and K currents for spike generation and a leak current.
    Uses area-normalized parameters (e.g., uF/cm^2, mS/cm^2, uA/cm^2).
    The user needs to provide `I_input` as current density (A/cm^2).

    Parameters
    ----------
    C_m : brian2.units.fundamentalunits.Quantity, optional
        Membrane capacitance per unit area (default: 1 uF/cm^2).
    E_Na : brian2.units.fundamentalunits.Quantity, optional
        Sodium reversal potential (default: 50 mV).
    E_K : brian2.units.fundamentalunits.Quantity, optional
        Potassium reversal potential (default: -77 mV).
    E_L : brian2.units.fundamentalunits.Quantity, optional
        Leak reversal potential (default: -54.4 mV).
    g_Na_bar : brian2.units.fundamentalunits.Quantity, optional
        Maximal sodium conductance per unit area (default: 120 mS/cm^2).
    g_K_bar : brian2.units.fundamentalunits.Quantity, optional
        Maximal potassium conductance per unit area (default: 36 mS/cm^2).
    g_L_bar : brian2.units.fundamentalunits.Quantity, optional
        Leak conductance per unit area (default: 0.3 mS/cm^2).
    V_T_hh : brian2.units.fundamentalunits.Quantity, optional
        A reference voltage, often used in the alpha/beta functions (default: -60mV).
        Can be adjusted to shift activation curves if needed.
    I_tonic : brian2.units.fundamentalunits.Quantity, optional
        Constant tonic current density (default: 0 uA/cm^2).
    refractory_period : brian2.units.fundamentalunits.Quantity, optional
        Explicit refractory period (default: 0 ms, HH dynamics usually handle this).

    Returns
    -------
    dict
        A dictionary for `brian2.NeuronGroup` definition.
    """
    # Note: V_T_hh is a general threshold-like parameter for the rate functions.
    # It's not a hard spike threshold like in LIF.
    # The spike "threshold" in HH is emergent from the dynamics.
    # We need a numerical threshold for Brian2's spike detection.
    numerical_spike_threshold = 0*b2.mV # A common value to detect the peak of AP

    eqs = """
    # Membrane potential
    dv/dt = (I_Na + I_K + I_L + I_input + I_tonic_val) / C_m_val : volt (unless refractory)

    # Sodium current
    I_Na = g_Na_bar_val * m**3 * h * (E_Na_val - v) : amp/meter**2
    dm/dt = alpha_m * (1-m) - beta_m * m : 1
    dh/dt = alpha_h * (1-h) - beta_h * h : 1
    alpha_m = (0.1/mV) * (v - (V_T_hh_val + 25*mV)) / (1 - exp(-(v - (V_T_hh_val + 25*mV))/(10*mV))) / ms : Hz
    beta_m = (4.0) * exp(-(v - (V_T_hh_val + 0*mV))/(18*mV)) / ms : Hz
    alpha_h = (0.07) * exp(-(v - (V_T_hh_val + 0*mV))/(20*mV)) / ms : Hz
    beta_h = (1.0) / (1 + exp(-(v - (V_T_hh_val + 30*mV))/(10*mV))) / ms : Hz

    # Potassium current
    I_K = g_K_bar_val * n**4 * (E_K_val - v) : amp/meter**2
    dn/dt = alpha_n * (1-n) - beta_n * n : 1
    alpha_n = (0.01/mV) * (v - (V_T_hh_val + 10*mV)) / (1 - exp(-(v - (V_T_hh_val + 10*mV))/(10*mV))) / ms : Hz
    beta_n = (0.125) * exp(-(v - (V_T_hh_val + 0*mV))/(80*mV)) / ms : Hz

    # Leak current
    I_L = g_L_bar_val * (E_L_val - v) : amp/meter**2

    # Input current density
    I_input : amp/meter**2
    """

    return {
        'model': eqs,
        'threshold': f'v > {numerical_spike_threshold!r}', # Numerical threshold for Brian2
        'reset': '', # HH model resets dynamically, no explicit v/u reset needed for spike event.
                     # If an explicit reset IS desired after the numerical threshold, it can be added.
                     # e.g. 'v = -70*mV' but this would override HH dynamics.
        'refractory': refractory_period, # Can be used if an explicit absolute refractory period is needed
                                         # on top of the relative refractoriness from h-gate inactivation.
        'namespace': {
            'C_m_val': C_m,
            'E_Na_val': E_Na,
            'E_K_val': E_K,
            'E_L_val': E_L,
            'g_Na_bar_val': g_Na_bar,
            'g_K_bar_val': g_K_bar,
            'g_L_bar_val': g_L_bar,
            'V_T_hh_val': V_T_hh,
            'I_tonic_val': I_tonic,
            # Initial values (can be overridden in NeuronGroup)
            # Typically, start near resting potential, and m,h,n at their steady-state values for that V.
            'v_default_init': E_L,
            'm_default_init': 0.05, # Approx. steady state for E_L (e.g. alpha_m / (alpha_m + beta_m) at E_L)
            'h_default_init': 0.6,  # Approx. steady state for E_L
            'n_default_init': 0.32, # Approx. steady state for E_L
        },
        'method': ('exponential_euler', {'simplify': True, 'split_వ': True}) # Good method for HH
        # Alternative: 'rk4' or 'heun' for more accuracy if needed.
    }
