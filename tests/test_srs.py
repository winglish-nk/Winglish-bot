"""
SRS（Spaced Repetition System）のテスト
"""
from datetime import date

from srs import update_srs


class TestUpdateSRS:
    """update_srs関数のテスト"""

    def test_update_srs_known_word(self):
        """覚えた単語（q=5）のSRS更新をテスト"""
        e, i, c, next_review = update_srs(2.5, 0, 0, 5)
        
        assert e > 2.5, "easinessは増加するべき"
        assert i > 0, "interval_daysは増加するべき"
        assert c == 1, "consecutive_correctは1になるべき"
        assert isinstance(next_review, date), "next_reviewはdate型であるべき"
        assert next_review > date.today(), "next_reviewは未来の日付であるべき"

    def test_update_srs_forgotten_word(self):
        """忘れた単語（q=2）のSRS更新をテスト"""
        e, i, c, next_review = update_srs(2.5, 10, 5, 2)
        
        assert c == 0, "忘れた場合はconsecutive_correctが0にリセットされるべき"
        assert i == 1, "忘れた場合はinterval_daysが1にリセットされるべき"
        assert isinstance(next_review, date), "next_reviewはdate型であるべき"

    def test_update_srs_easiness_minimum(self):
        """easinessの最小値（1.3）をテスト"""
        e, i, c, next_review = update_srs(1.3, 0, 0, 1)
        
        assert e >= 1.3, "easinessは1.3以上であるべき"
        assert isinstance(next_review, date), "next_reviewはdate型であるべき"

    def test_update_srs_quality_3(self):
        """品質スコア3（最低限の正解）のテスト"""
        e, i, c, next_review = update_srs(2.5, 0, 0, 3)
        
        assert c == 1, "q>=3の場合はconsecutive_correctが増加するべき"
        assert i >= 1, "interval_daysは1以上であるべき"
        assert isinstance(next_review, date), "next_reviewはdate型であるべき"

    def test_update_srs_consecutive_correct(self):
        """連続正解回数の累積をテスト"""
        # 1回目
        e1, i1, c1, _ = update_srs(2.5, 0, 0, 5)
        assert c1 == 1, "1回目の正解"
        
        # 2回目（前回の結果を使って）
        e2, i2, c2, _ = update_srs(e1, i1, c1, 5)
        assert c2 == 2, "2回目の正解で連続回数が増加"
        assert i2 > i1, "連続正解が続くと間隔が広がる"

    def test_update_srs_type_hints(self):
        """戻り値の型をテスト"""
        result = update_srs(2.5, 5, 3, 4)
        e, i, c, next_review = result
        
        assert isinstance(e, float), "easinessはfloat型"
        assert isinstance(i, float), "interval_daysはfloat型"
        assert isinstance(c, int), "consecutive_correctはint型"
        assert isinstance(next_review, date), "next_reviewはdate型"

