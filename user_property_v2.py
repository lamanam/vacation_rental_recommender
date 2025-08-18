

# property & user defs

class Property:
    def __init__(self, property_id, name, location, type_, price_per_night, features, tags):
        self.property_id = property_id
        self.name = name
        self.location = location
        self.type = type_
        self.price_per_night = price_per_night
        self.features = features
        self.tags = tags

    def to_dict(self):
        return {
            "property_id": self.property_id,
            "name":self.name,
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
            d["name"],
            d["location"],
            d["type"],
            d["price_per_night"],
            d["features"],
            d["tags"]
        )


class User:
    def __init__(self, user_id, name, group_size, preferred_environment, budget_range, travel_dates):
        self.user_id = user_id
        self.name = name
        self.group_size = group_size
        self.preferred_environment = preferred_environment
        self.budget_range = budget_range
        self.travel_dates = travel_dates

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "group_size": self.group_size,
            "preferred_environment": self.preferred_environment,
            "budget_range": self.budget_range,
            "travel_dates": self.travel_dates
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["user_id"],
            d["name"],
            d["group_size"],
            d["preferred_environment"],
            d["budget_range"],
            d["travel_dates"]
        )
