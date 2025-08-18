# recommender.py

from user_property import User, Property



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

def score_property2(user: User, prop: Property):
    """
    Simple scoring based on budget and tag matches.
    Higher score = better fit.
    """

    #assume that this +s to 100 - since we are setting this
    weights = [0.45, 0.20, 0.35] #budget, pref, must have feats

    #budget score (btwn 0 & 1)
    afford1 = (user.budget - prop.price_per_night) / max(user.budget, 0.001)
    afford_score = afford1 if afford1 <= 1 else 1.0

    #pref match (btwn 0 to 1  )
    pref_matches = set(user.preferred_environment.split(",")) & set(prop.tags.split(","))
    pref_match_count = len(pref_matches)
    user_pref_count = len(user.preferred_environment.split(","))
    pref_score = 0 if user_pref_count==0 else pref_match_count/user_pref_count


    #feat_score (num of matching feats - bwtn 0 and 1 )
    feat_matches = set(user.must_have_feature.split(",")) & set(prop.features.split(","))
    feat_match_count = len(feat_matches)
    user_feat_count = len(user.must_have_feature.split(","))
    feat_score = 0 if user_feat_count == 0 else feat_match_count / user_feat_count

    #overall score
    score = afford_score*weights[0] + pref_score*weights[1] + feat_score*weights[2]
    return score


def get_recommendations(user: User, properties: list, top_n=5):

    scored = [(prop, score_property(user, prop)) for prop in properties]
    # Sort descending by score
    scored = [x for x in scored if x[1] > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [prop for prop, score in scored[:top_n]]
