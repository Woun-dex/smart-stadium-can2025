"""
Stadium Control Policies for ML-Driven Operations.

This module provides the decision logic and action execution
for dynamic stadium resource management.
"""

LOW_RISK = 0.6
HIGH_RISK = 0.8


def decide_action(predicted_risk):
    """
    Decide control action based on predicted congestion risk.
    
    Parameters:
    -----------
    predicted_risk : float
        Normalized risk score (0-1), where 1 = critical congestion
        
    Returns:
    --------
    str : Action level ("NONE", "MODERATE", or "STRONG")
    """
    if predicted_risk > HIGH_RISK:
        return "STRONG"
    elif predicted_risk >= LOW_RISK:
        return "MODERATE"
    else:
        return "NONE"
    

def apply_action(action, resources, risk_type="ENTRY"):
    """
    Apply control action to stadium resources.
    
    Parameters:
    -----------
    action : str
        Action level from decide_action()
    resources : StadiumResources
        Stadium resources object to modify
    risk_type : str
        "ENTRY" for entry congestion, "EXIT" for exit congestion
    """
    if risk_type == "EXIT":
        # Exit congestion management
        if action == "MODERATE":
            resources.open_extra_exit_gates(5)
        elif action == "STRONG":
            resources.open_extra_exit_gates(10)
            resources.enable_exit_redirection()
    else:
        # Entry congestion management
        if action == "MODERATE":
            resources.open_extra_vendors(5)
            resources.open_extra_security(3)
        elif action == "STRONG":
            resources.open_extra_vendors(10)
            resources.open_extra_security(5)
            resources.throttle_turnstiles(0.9)
            resources.enable_redirection()


def apply_action_with_details(action, resources, risk_type="ENTRY"):

    details = []
    
    if risk_type == "EXIT":
        # Exit congestion management
        if action == "MODERATE":
            old_exits = resources.active_exit_gates
            resources.open_extra_exit_gates(5)
            details.append(f"Opened +5 exit gates ({old_exits}→{resources.active_exit_gates})")
        elif action == "STRONG":
            old_exits = resources.active_exit_gates
            resources.open_extra_exit_gates(10)
            details.append(f"Opened +10 exit gates ({old_exits}→{resources.active_exit_gates})")
            resources.enable_exit_redirection()
            details.append("Enabled exit redirection to less crowded gates")
    else:
        # Entry congestion management  
        if action == "MODERATE":
            old_vendors = resources.active_vendors
            old_security = resources.active_security
            resources.open_extra_vendors(5)
            resources.open_extra_security(3)
            details.append(f"Opened +5 vendors ({old_vendors}→{resources.active_vendors})")
            details.append(f"Opened +3 security lanes ({old_security}→{resources.active_security})")
        elif action == "STRONG":
            old_vendors = resources.active_vendors
            old_security = resources.active_security
            resources.open_extra_vendors(10)
            resources.open_extra_security(5)
            details.append(f"Opened +10 vendors ({old_vendors}→{resources.active_vendors})")
            details.append(f"Opened +5 security lanes ({old_security}→{resources.active_security})")
            resources.throttle_turnstiles(0.9)
            details.append("Throttled turnstiles to 90% speed")
            resources.enable_redirection()
            details.append("Enabled queue redirection")
    
    return " | ".join(details) if details else "No action"


def get_control_state(resources):
    """
    Get current control state for monitoring.
    
    Parameters:
    -----------
    resources : StadiumResources
        Stadium resources object
        
    Returns:
    --------
    dict : Current control state
    """
    return {
        'active_turnstiles': resources.active_turnstiles,
        'turnstile_service_factor': resources.turnstile_service_factor,
        'active_vendors': resources.active_vendors,
        'max_vendors': resources.MAX_VENDORS,
        'redirection_enabled': resources.redirection_enabled,
        'parking_available': resources.parking.level,
    }


def reset_control_state(resources):
    """
    Reset control state to defaults.
    
    Parameters:
    -----------
    resources : StadiumResources
        Stadium resources object
    """
    resources.turnstile_service_factor = 1.0
    resources.active_vendors = 80
    resources.redirection_enabled = False
    resources.normalize_turnstiles()