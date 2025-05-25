# entity_state.py
# Stores and manages the state of all placed entities in the game.

class EntityState:
    def __init__(self, entity):
        self.entity = entity
        # Copy all instance attributes from the entity
        self.__dict__.update(entity.__dict__)
        # Optionally, copy selected class attributes if not present on the instance
        for attr in ['icon', 'type', 'display_name']:
            if not hasattr(self, attr) and hasattr(entity.__class__, attr):
                setattr(self, attr, getattr(entity.__class__, attr))
        # Do NOT set color at all

    def __getattr__(self, name):
        # Proxy attribute access to the real entity
        return getattr(self.entity, name)

    def get_public_attrs(self):
        # Delegate to the real entity's get_public_attrs if available
        if hasattr(self.entity, 'get_public_attrs'):
            return self.entity.get_public_attrs()
        # Fallback: all public instance attributes
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and not callable(v)}

    def to_dict(self):
        # Delegate to the real entity's to_dict for robust serialization
        return self.entity.to_dict()

    @classmethod
    def from_dict(cls, data, entity_class):
        # Create an entity from dict using the entity_class's from_dict
        entity = entity_class.from_dict(data)
        return cls(entity)

class EntityStateList:
    def __init__(self):
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(EntityState(entity))

    def remove_entity_at(self, x, y):
        self.entities = [e for e in self.entities if not (e.x == x and e.y == y)]

    def get_entity_at(self, x, y):
        for e in self.entities:
            if e.x == x and e.y == y:
                return e
        return None

    def to_list(self):
        return [e.to_dict() for e in self.entities]

    def clear(self):
        self.entities.clear()

    @classmethod
    def from_list(cls, data_list, entity_type_map):
        print(f"from_list: got {len(data_list)} items. entity_type_map keys: {list(entity_type_map.keys())}")
        esl = cls()
        for data in data_list:
            entity_type = data.get('type')
            print(f"  loading entity type: {entity_type}")
            entity_class = entity_type_map.get(entity_type)
            if entity_class:
                esl.entities.append(EntityState.from_dict(data, entity_class))
            else:
                print(f"  WARNING: entity_type '{entity_type}' not found in entity_type_map!")
        return esl
