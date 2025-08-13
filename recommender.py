# recommender.py

from models import User, Property


def score_property(user: User, prop: Property):
    """
    Simple scoring based on budget and tag matches.
    Higher score = better fit.
    """
    if prop.price_per_night > user.budget:
        return 0  # over budget, no fit

    # Score: number of matched tags + features
    score = 0
    if user.preferred_environment in prop.tags:
        score += 1  # environment match is important

    return score


def get_recommendations(user: User, properties: list, top_n=5):
    scored = [(prop, score_property(user, prop)) for prop in properties]
    # Sort descending by score
    scored = [x for x in scored if x[1] > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [prop for prop, score in scored[:top_n]]
