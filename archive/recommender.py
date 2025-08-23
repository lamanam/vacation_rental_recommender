# recommender.py

import pandas as pd
from user_property import User, Property

W_BUDGET = 0.35
W_PREF = 0.2
W_MUST_HAVE = 0.45

def properties_to_df(properties: list[Property]) -> pd.DataFrame:
    return pd.DataFrame([p.to_dict() for p in properties])

def score_property(user: User, prop_df: pd.DataFrame) -> pd.DataFrame:

    #get must have feature score
    prop_df["feature_count"] = prop_df["features"].apply(lambda feats: len(feats.split(",")))
    prop_df["feature_match"] = prop_df["features"].apply(lambda feats: len(set(feats.split(",")) & set(user.must_have_feature.split(","))))
    prop_df["feature_score"] = prop_df.apply(lambda row: 0 if row['feature_count']==0 else (round(row['feature_match']/row['feature_count'],2)), axis=1)

    #get prefered env score
    prop_df["tags_count"] = prop_df["tags"].apply(lambda feats: len(feats.split(",")))
    prop_df["tags_match"] = prop_df["tags"].apply(lambda tags: len(set(tags.split(",")) & set(user.preferred_environment.split(","))))
    prop_df["tags_score"] = prop_df.apply(lambda row: 0 if row['tags_count'] == 0 else (round(row['tags_match'] / row['tags_count'], 2)), axis=1)

    #get affordability score
    prop_df['affordability_score1'] = prop_df["price_per_night"].apply(lambda p: (user.budget - p) / max(user.budget, 0.001))
    prop_df['afford_score'] = prop_df['affordability_score1'].apply(lambda a: a if a<=1 else 1.0)

    # get final score (weighted sum — can adjust weights)
    prop_df["final_score_v1"] = (
            W_MUST_HAVE * prop_df["feature_score"] +
            W_PREF * prop_df["tags_score"] +
            W_BUDGET * prop_df["afford_score"]
    )
    prop_df["final_score"] = prop_df.apply(
        lambda row: 0 if row['feature_match'] == 0 else row['final_score_v1'], axis=1)
    # prop_df.to_csv('test_output.csv', index=False)
    return prop_df[prop_df['final_score']>0]


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