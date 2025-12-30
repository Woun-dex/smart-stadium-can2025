"""
Stadium Resources - SimPy resources for stadium simulation
===========================================================
Realistic capacity constraints to generate proper queuing.
"""
import simpy


class StadiumResources:
    """
    Stadium resources with realistic capacities that create queues.
    
    Key insight: To see wait times > 0, arrival rate must exceed service rate
    at some point. We model:
    - Security screening (major bottleneck)
    - Turnstile entry (ticket scanning)
    - Vendors (concessions)
    - Exit gates (separate from entry)
    - Parking
    """
    
    def __init__(self, env):
        self.env = env

        # -------------------------
        # SECURITY SCREENING
        # -------------------------
        # Walk-through metal detectors: 5-10 sec per person
        # 60 lanes × 6 fans/min avg = 360 fans/min throughput
        # NOT the main bottleneck - turnstiles are
        self.MAX_SECURITY = 80
        self.active_security = 60
        self.security = simpy.Resource(env, capacity=self.active_security)

        # -------------------------
        # TURNSTILES (ENTRY GATES)
        # -------------------------
        # After security, fans scan tickets at turnstiles
        # Each turnstile: ~10-15 fans/min (4-6 sec per scan)
        # 40 turnstiles = 400-600 fans/min MAX
        # Peak arrival ~500 fans/min, so some queuing expected
        self.MAX_TURNSTILES = 60
        self.active_turnstiles = 40
        self.turnstile_service_factor = 1.0
        self.turnstiles = simpy.Resource(env, capacity=self.active_turnstiles)

        # -------------------------
        # VENDORS (CONCESSIONS)
        # -------------------------
        # Each vendor serves ~40 customers/hour = 0.67/min
        # 120 vendors = ~80 customers/min
        # With 20% of 68k fans = 13,600 wanting food spread over time
        self.MAX_VENDORS = 150
        self.active_vendors = 120
        self.vendors = simpy.Resource(env, capacity=self.active_vendors)

        # -------------------------
        # EXIT GATES
        # -------------------------
        # Separate from entry - exits are wider/faster
        # Each exit gate: ~30-50 fans/min
        # 40 gates = 1200-2000 fans/min
        # This handles exit surge better
        self.MAX_EXIT_GATES = 60
        self.active_exit_gates = 40
        self.exit_gates = simpy.Resource(env, capacity=self.active_exit_gates)

        # -------------------------
        # PARKING
        # -------------------------
        self.MAX_PARKING = 6000
        self.parking = simpy.Container(env, init=self.MAX_PARKING, capacity=self.MAX_PARKING)

        # -------------------------
        # CONTROL FLAGS
        # -------------------------
        self.redirection_enabled = False
        self.exit_redirection_enabled = False

    def open_extra_security(self, n):
        """Open additional security lanes."""
        new_capacity = min(self.active_security + n, self.MAX_SECURITY)
        if new_capacity != self.active_security:
            self.active_security = new_capacity
            # Create new resource with updated capacity
            self.security = simpy.Resource(self.env, capacity=self.active_security)

    def open_extra_turnstiles(self, n):
        """Open additional turnstiles."""
        new_capacity = min(self.active_turnstiles + n, self.MAX_TURNSTILES)
        if new_capacity != self.active_turnstiles:
            self.active_turnstiles = new_capacity
            self.turnstiles = simpy.Resource(self.env, capacity=self.active_turnstiles)

    def open_extra_vendors(self, n):
        """Open additional vendor stations."""
        new_capacity = min(self.active_vendors + n, self.MAX_VENDORS)
        if new_capacity != self.active_vendors:
            self.active_vendors = new_capacity
            self.vendors = simpy.Resource(self.env, capacity=self.active_vendors)

    def open_extra_exits(self, n):
        """Open additional exit gates."""
        new_capacity = min(self.active_exit_gates + n, self.MAX_EXIT_GATES)
        if new_capacity != self.active_exit_gates:
            self.active_exit_gates = new_capacity
            self.exit_gates = simpy.Resource(self.env, capacity=self.active_exit_gates)
    
    def open_extra_exit_gates(self, n):
        """Alias for open_extra_exits - Open additional exit gates."""
        self.open_extra_exits(n)
    
    def enable_exit_redirection(self):
        """Enable exit queue redirection to less congested gates."""
        self.exit_redirection_enabled = True
    
    def disable_exit_redirection(self):
        """Disable exit redirection."""
        self.exit_redirection_enabled = False
    
    def throttle_turnstiles(self, factor):
        """Slow down turnstile processing (e.g., extra checks)."""
        self.turnstile_service_factor *= factor
        self.turnstile_service_factor = max(0.5, self.turnstile_service_factor)

    def normalize_turnstiles(self):
        """Gradually return turnstile speed to normal."""
        self.turnstile_service_factor = min(1.0, self.turnstile_service_factor + 0.1)
        
    def enable_redirection(self):
        """Enable queue redirection."""
        self.redirection_enabled = True

    def disable_redirection(self):
        """Disable queue redirection."""
        self.redirection_enabled = False

    def get_status(self):
        """Get current resource status."""
        return {
            'security_queue': len(self.security.queue),
            'security_utilization': self.security.count / self.active_security,
            'turnstile_queue': len(self.turnstiles.queue),
            'turnstile_utilization': self.turnstiles.count / self.active_turnstiles,
            'vendor_queue': len(self.vendors.queue),
            'vendor_utilization': self.vendors.count / self.active_vendors,
            'exit_queue': len(self.exit_gates.queue),
            'exit_utilization': self.exit_gates.count / self.active_exit_gates,
            'parking_available': self.parking.level,
            'parking_utilization': 1 - (self.parking.level / self.MAX_PARKING),
        }