from __future__ import annotations

import datetime
from typing import Tuple, Union


def update_srs(
    easiness: Union[float, int],
    interval_days: Union[float, int],
    consecutive_correct: Union[int, None],
    q: Union[int, float]
) -> Tuple[float, float, int, datetime.date]:
    """
    SM-2アルゴリズムに基づいてSRS（Spaced Repetition System）の状態を更新する
    
    Args:
        easiness: 現在の容易度係数（デフォルト: 2.5）
        interval_days: 現在の復習間隔（日数）
        consecutive_correct: 連続正解回数（Noneの場合は0として扱う）
        q: 品質スコア（0-5、5が最も良い）
    
    Returns:
        (新しいeasiness, 新しいinterval_days, 新しいconsecutive_correct, 次の復習日)のタプル
    
    Note:
        - q < 3 の場合、復習間隔が1日にリセットされ、連続正解回数が0にリセットされる
        - q >= 3 の場合、easinessが更新され、復習間隔が計算される
    """
    e = float(easiness)
    i = float(interval_days)
    c = int(consecutive_correct or 0)
    q = int(q)

    # SM-2 由来の更新
    e = e + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if e < 1.3:
        e = 1.3

    if q < 3:
        c = 0
        i = 1
    else:
        c += 1
        i = 1 if c == 1 else round(i * e)

    next_review = datetime.date.today() + datetime.timedelta(days=int(i))
    return float(e), float(i), int(c), next_review