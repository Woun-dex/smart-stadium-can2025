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
    
    NEW REALISTIC FEATURES:
    - Staff fatigue (efficiency degrades over time)
    - Shift changes (temporary capacity reduction)
    - Break schedules (some lanes close periodically)
    - Equipment malfunctions (random temporary closures)
    """
    
    def __init__(self, env):
        self.env = env
        
        # Staff efficiency (degrades with fatigue)
        self.staff_efficiency = 1.0
        self.last_break_time = 0

        # -------------------------
        # SECURITY SCREENING
        # -------------------------
        self.MAX_SECURITY = 80
        self.active_security = 60
        self.security = simpy.Resource(env, capacity=self.active_security)
        self.security_on_break = 0

        # -------------------------
        # TURNSTILES (ENTRY GATES)
        # -------------------------
        self.MAX_TURNSTILES = 60
        self.active_turnstiles = 40
        self.turnstile_service_factor = 1.0
        self.turnstiles = simpy.Resource(env, capacity=self.active_turnstiles)
        self.turnstiles_malfunctioning = 0

        # -------------------------
        # VENDORS (CONCESSIONS)
        # -------------------------
        self.MAX_VENDORS = 150
        self.active_vendors = 120
        self.vendors = simpy.Resource(env, capacity=self.active_vendors)
        self.vendors_on_break = 0

        # -------------------------
        # EXIT GATES
        # -------------------------
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
        
        # Start staff management processes
        self.env.process(self.staff_fatigue_process())
        self.env.process(self.equipment_malfunction_process())
        self.env.process(self.break_schedule_process())
    
    def staff_fatigue_process(self):
        """Simulate staff fatigue over time - efficiency degrades."""
        while True:
            yield self.env.timeout(30)  # Check every 30 minutes
            
            # Fatigue builds up
            self.staff_efficiency = max(0.75, self.staff_efficiency - 0.03)
            
            # Service times increase with fatigue
            if self.staff_efficiency < 0.9:
                self.turnstile_service_factor = max(0.85, 1.0 / self.staff_efficiency)
    
    def equipment_malfunction_process(self):
        """Random equipment malfunctions temporarily reduce capacity."""
        import random
        while True:
            yield self.env.timeout(random.uniform(40, 80))  # Random intervals
            
            # Random malfunction
            malfunction_type = random.choice(['turnstile', 'security', 'none', 'none'])
            
            if malfunction_type == 'turnstile' and self.turnstiles_malfunctioning == 0:
                # 1-2 turnstiles malfunction
                affected = random.randint(1, 2)
                self.turnstiles_malfunctioning = affected
                old_capacity = self.active_turnstiles
                self.active_turnstiles = max(10, self.active_turnstiles - affected)
                self.turnstiles = simpy.Resource(self.env, capacity=self.active_turnstiles)
                
                # Repair after 15-30 minutes
                yield self.env.timeout(random.uniform(15, 30))
                self.active_turnstiles = old_capacity
                self.turnstiles = simpy.Resource(self.env, capacity=self.active_turnstiles)
                self.turnstiles_malfunctioning = 0
            
            elif malfunction_type == 'security' and self.security_on_break == 0:
                # 1-3 security lanes have technical issues
                affected = random.randint(1, 3)
                old_capacity = self.active_security
                self.active_security = max(15, self.active_security - affected)
                self.security = simpy.Resource(self.env, capacity=self.active_security)
                
                # Fix after 10-20 minutes
                yield self.env.timeout(random.uniform(10, 20))
                self.active_security = old_capacity
                self.security = simpy.Resource(self.env, capacity=self.active_security)
    
    def break_schedule_process(self):
        """Staff take breaks periodically (realistic workforce management)."""
        import random
        while True:
            yield self.env.timeout(60)  # Every hour
            
            # Vendors take staggered breaks (10-15% at a time)
            if self.vendors_on_break == 0 and self.env.now < 280:  # Not during match
                break_count = max(5, int(self.active_vendors * 0.12))
                self.vendors_on_break = break_count
                old_capacity = self.active_vendors
                self.active_vendors = max(20, self.active_vendors - break_count)
                self.vendors = simpy.Resource(self.env, capacity=self.active_vendors)
                
                # Break duration: 15 minutes
                yield self.env.timeout(15)
                self.active_vendors = old_capacity
                self.vendors = simpy.Resource(self.env, capacity=self.active_vendors)
                self.vendors_on_break = 0
                
                # Restore some efficiency after break
                self.staff_efficiency = min(1.0, self.staff_efficiency + 0.05)
            
            yield self.env.timeout(random.uniform(20, 40))  # Variable between breaks

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