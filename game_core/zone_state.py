class ZoneState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        self.zones = []  # List of (zone_id, left, top, w, h, zone_type)
        self._initialized = True

    def add_zone(self, zone):
        self.zones.append(zone)

    def remove_zone_by_id(self, zone_id):
        self.zones = [z for z in self.zones if z[0] != zone_id]

    def get_zones(self):
        return list(self.zones)

    def clear(self):
        self.zones.clear()

# Singleton accessor
zone_state = ZoneState()
