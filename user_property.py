# property & user defs

class Property:
    def __init__(self, property_id, location, type_, price_per_night, features, tags):
        self.property_id = property_id
        self.location = location
        self.type = type_
        self.price_per_night = price_per_night
        self.features = features
        self.tags = tags

    def to_dict(self):
        return {
            "property_id": self.property_id,
            "location": self.location,
            "type": self.type,
            "price_per_night": self.price_per_night,
            "features": self.features,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["property_id"],
            d["location"],
            d["type"],
            d["price_per_night"],
            d["features"],
            d["tags"]
        )


class User:
    def __init__(self, user_id, name, group_size, preferred_environment, budget):
        self.user_id = user_id
        self.name = name
        self.group_size = group_size
        self.preferred_environment = preferred_environment
        self.budget = budget

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "group_size": self.group_size,
            "preferred_environment": self.preferred_environment,
            "budget": self.budget
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["user_id"],
            d["name"],
            d["group_size"],
            d["preferred_environment"],
            d["budget"]
        )
