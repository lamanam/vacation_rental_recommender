
from __future__ import annotations
from user_property import User, Property
from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple, List, Optional, Dict, Any
import numpy as np
import pandas as pd
import re
import random

# 这个不要动( 因为是默认的参数)
DEFAULT_WEIGHTS = (0.45, 0.20, 0.15, 0.20)  # (价格, 环境, 功能, 入住人数差)
DEFAULT_MMR_LAMBDA = 0.7
DEFAULT_PARTY_METHOD = "expo"  # "expo" 或 "linear"
DEFAULT_PARTY_K = 1.2  # expo 上升速度（越大越快到 1）
DEFAULT_PARTY_RSAT = 3.0  # linear 满分阈值：cap/gs >= r_sat 视为 1
ADD_TIE_BREAK_NOISE = True  # 是否注入极小噪声打破并列（关闭则完全可复现）


def _to_df(Property) -> pd.DataFrame: # where property 是一个list of Property

    rows = []
    for p in Property:
        features = list(getattr(p, "features", []) or [])
        tags = list(getattr(p, "tags", []) or [])
        cap = getattr(p, "allowed_number_check_in", None)
        rows.append(
            {
                #"property_obj": p,
                "property_id": getattr(p, "property_id", None),
                "location": getattr(p, "location", None),
                "type": getattr(p, "type", None),
                "price_per_night": float(getattr(p, "price_per_night", 0.0) or 0.0),
                "features": features,
                "tags": tags,
                "allowed_number_check_in": int(cap or 0),
            }
        )
    df = pd.DataFrame.from_records(rows)

def _party_score(capacity: np.ndarray, group_size: int,
                 #function的目的： 返回 np.ndarray 其目的是得到一些数用来代表user的checkin人数和property的许可人数 如果property的人数远远的大于， 那么数就应该是大的 【0，1】
                 method: str = DEFAULT_PARTY_METHOD,
                 *, k: float = DEFAULT_PARTY_K, r_sat: float = DEFAULT_PARTY_RSAT) -> np.ndarray:
    gs = max(int(group_size or 1), 1)
    cap = np.maximum(capacity.astype(float), 0.0)
    r = cap / gs
    x = np.maximum(r - 1.0, 0.0)  # 仅计算超过部分

    if method == "linear":
        s = x / max(r_sat - 1.0, 1e-9)
    else:  # expo
        s = 1.0 - np.exp(-k * x)

    return np.clip(s, 0.0, 1.0)



def score_properties(
    df: pd.DataFrame,
    User,
    *,
    weights: Tuple[float, float, float, float] = DEFAULT_WEIGHTS,
    party_method: str = DEFAULT_PARTY_METHOD,
    party_k: float = DEFAULT_PARTY_K,
    party_rsat: float = DEFAULT_PARTY_RSAT,
    random_seed: Optional[int] = None,
) -> pd.DataFrame:
    df = df.copy()

    budget = float(getattr(User, "budget", 0.0) or 0.0) # 应该和TUT的那个user.budget是一样的
    preferred_environment = getattr(User, "preferred_environment", None) # 应该和TUT的那个user.preferred_environment是一样的
    must_have_features = getattr(User, "must_have_features", None) # 应该和TUT的那个user.must_have_features是一样的
    group_size = int(
        getattr(User, "group_size", 0) # 应该和TUT的那个user.group_size是一样的
        or 1
    )


    w_afford, w_env, w_feat, w_party = weights  # 这个肯定是要改的， 因为这个应该对象是user吧
    total = w_afford + w_env + w_feat + w_party
    if total == 0:
        w_afford, w_env, w_feat, w_party = DEFAULT_WEIGHTS
    else:
        w_afford /= total
        w_env /= total
        w_feat /= total
        w_party /= total

    prices = df["price_per_night"].to_numpy(dtype=float)
    afford = np.clip((budget - prices) / max(budget, 0.001), 0.0, 1.0)

    if preferred_environment:
        env = np.array(
            [1.0 if preferred_environment in (tags or []) else 0.0 for tags in df["tags"]],
            dtype=float,
        )
    else:
        env = np.zeros(len(df), dtype=float)


    if must_have_features:
        mh = {str(f).lower() for f in must_have_features}
        mh_len = max(len(mh), 1)
        feat = np.array(
            [
                len(mh.intersection([str(f).lower() for f in (fs or [])])) / mh_len
                for fs in df["features"]
            ],
            dtype=float,
        )
    else:
        feat = np.zeros(len(df), dtype=float)

    # -------- 入住人数差分（party_score）--------
    cap_arr = df.get("allowed_number_check_in", pd.Series(0, index=df.index)).to_numpy(dtype=float)
    party = np.where(
        cap_arr > 0.0,
        _party_score(cap_arr, group_size, method=party_method, k=party_k, r_sat=party_rsat),
        0.0,
    )

    df["afford_score"] = afford
    df["env_score"] = env
    df["feat_score"] = feat
    df["party_score"] = party
    df["match_score"] = (
        w_afford * df["afford_score"]
        + w_env    * df["env_score"]
        + w_feat   * df["feat_score"]
        + w_party  * df["party_score"]
    )
    if random_seed is not None:
        rng = np.random.default_rng(random_seed)
        noise = rng.uniform(0, 1e-9, size=len(df))
        df["match_score"] = df["match_score"] + noise
    elif ADD_TIE_BREAK_NOISE:
        df["match_score"] = df["match_score"] + np.random.uniform(0, 1e-9, size=len(df))

    # -------- 稳定排序：先分数降序，再 property_id 升序 --------
    df = df.sort_values(by=["match_score"], ascending=[False, True], kind="mergesort")
    return df





#