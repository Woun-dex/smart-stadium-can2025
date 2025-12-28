import simpy

class StadiumResources:
    def __init__(self, env):
        # Gates: 92 individual biometric turnstiles (each acts as a single lane/server)
        self.turnstiles = simpy.Resource(env, capacity=92)

        # Vendors: ~40+ concession points (model as shared servers; adjust for staff per stand)
        self.vendors = simpy.Resource(env, capacity=120)  # Allows multiple fans served simultaneously

        # Parking: ~5,200 structured spaces + additional surface/VIP lots
        self.parking = simpy.Container(env, init=6000, capacity=6000)  # "Spaces" as units; fans "put" 1 per car