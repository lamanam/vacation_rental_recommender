# recommender.py

import pandas as pd
from user_property import User, Property

# Weights for each scoring factor
W_BUDGET = 0.35
W_PREF = 0.2
W_MUST_HAVE = 0.45

#Convert a list of Property objects into a Pandas DataFrame
def properties_to_df(properties: list[Property]) -> pd.DataFrame:
    return pd.DataFrame([p.to_dict() for p in properties])
    
#Split a string or list into clean tokens
def clean_split(text, delimiter=","):
    """
    Splits a string or list into clean tokens.
    """
    if isinstance(text, list):  
        return [str(part).strip() for part in text if str(part).strip()]
    elif isinstance(text, str):  
        return [part.strip() for part in text.split(delimiter) if part.strip()]
    else:
        return []
        
# Score each property in the DataFrame for a given user
def score_property(user: User, prop_df: pd.DataFrame) -> pd.DataFrame:

    #get must have feature score
    #Count how many features each property has
    prop_df["feature_count"] = prop_df["features"].apply(lambda feats: len(clean_split(feats)))
    #Count how many of those features match the user's must-have features
    prop_df["feature_match"] = prop_df["features"].apply(lambda feats: len(set(clean_split(feats)) & set(clean_split(user.must_have_feature))))
    #Compute feature score = number of (matched features/ total features), rounded to 2 decimals. If no features listed, score = 0
    prop_df["feature_score"] = prop_df.apply(lambda row: 0 if row['feature_count']==0 else (round(row['feature_match']/row['feature_count'],2)), axis=1)

    #get prefered env score
    #Count how many tags each property has
    prop_df["tags_count"] = prop_df["tags"].apply(lambda tags: len(clean_split(tags)))
    #Count how many tags overlap with user’s preferred environment
    prop_df["tags_match"] = prop_df["tags"].apply(lambda tags: len(set(clean_split(tags)) & set(clean_split(user.preferred_environment))))
    #Compute env score = matches tags/total tags, rounded to 2 decimals. If no tags listed, score = 0
    prop_df["tags_score"] = prop_df.apply(lambda row: 0 if row['tags_count'] == 0 else (round(row['tags_match'] / row['tags_count'], 2)), axis=1)

    #get affordability score
    #(budget - price) / budget  ->(normalized)
    prop_df['affordability_score1'] = prop_df["price_per_night"].apply(lambda p: (user.budget - p) / max(user.budget, 0.001))
    #Final affordability score = affordability_score1 if ≤ 1, otherwise cap at 1
    prop_df['afford_score'] = prop_df['affordability_score1'].apply(lambda a: a if a<=1 else 1.0)

    # get final score (weighted sum — can adjust weights)
    prop_df["final_score"] = (
            W_MUST_HAVE * prop_df["feature_score"] +
            W_PREF * prop_df["tags_score"] +
            W_BUDGET * prop_df["afford_score"]
    )
    prop_df.to_csv('user_results/test_output_user_{}.csv'.format(user.user_id), index=False)
    return prop_df[(prop_df['final_score'] > 0) & (prop_df['feature_score'] > 0)]


def get_recommendations(user: User, properties: list, top_n=5) -> list:

    # convert prop list to df
    property_df = pd.DataFrame([p.to_dict() for p in properties])

    #filter property df to contain relevant rows - fit budget & capacity
    property_df_filtered = property_df[
        (property_df["price_per_night"] <= user.budget) &
        (property_df["allowed_number_check_in"] >= user.group_size)
        ].copy()

    #get scores for each property
    property_df_scored = score_property(user, property_df_filtered)

    # Sort by final_score (descending) and take top N
    top_property_df = property_df_scored.sort_values(by="final_score", ascending=False).head(top_n)

    # Convert rows back to Property objects
    top_properties = [Property.from_dict(row.to_dict()) for _, row in top_property_df.iterrows()]

    return top_properties




