# property & user defs

class Property:
    def __init__(self, name, property_id, location, allowed_number_check_in,  type_, price_per_night, features, tags):
        self.property_id = property_id
        self.name = name
        self.location = location
        self.allowed_number_check_in = allowed_number_check_in  # 新增的一个属性
        self.type = type_
        self.price_per_night = price_per_night
        self.features = features
        self.tags = tags

    def to_dict(self):
        return {
            "property_id": self.property_id,
            "name": self.name,
            "location": self.location,
            "allowed_number_check_in": self.allowed_number_check_in,
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
            d["allowed_number_check_in"],
            d["location"],
            d["type"],
            d["price_per_night"],
            d["features"],
            d["tags"]
        )



class User:
    def __init__(self, user_id, name, group_size, preferred_environment, must_have_feature, budget):
        self.user_id = user_id
        self.name = name
        self.group_size = group_size # 新增的一个属性
        self.preferred_environment = preferred_environment
        self.must_have_feature = must_have_feature
        self.budget = budget

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "group_size": self.group_size,
            "preferred_environment": self.preferred_environment,
            "budget": self.budget,
            "must_have_feature": self.must_have_feature
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["user_id"],
            d["name"],
            d["group_size"],
            d["preferred_environment"],
            d["budget"],
            d["must_have_feature"]
        )
