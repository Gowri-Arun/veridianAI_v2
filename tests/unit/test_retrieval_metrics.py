from app.evaluation.retrieval_metrics import (
    expected_doc_coverage,
    hit_at_k,
    mean_reciprocal_rank,
    recall_at_k,
    reciprocal_rank,
)


class TestRecallAtK:
    def test_perfect_match(self):
        result = recall_at_k(["d1", "d2", "d3"], ["d1", "d2", "d3"], 3)
        assert result == 1.0

    def test_partial_match(self):
        result = recall_at_k(["d1", "d2", "d3"], ["d1", "d4"], 3)
        assert result == 0.5

    def test_no_match(self):
        result = recall_at_k(["d1", "d2"], ["d3", "d4"], 2)
        assert result == 0.0

    def test_empty_expected(self):
        result = recall_at_k(["d1", "d2"], [], 5)
        assert result == 0.0

    def test_empty_retrieved(self):
        result = recall_at_k([], ["d1", "d2"], 5)
        assert result == 0.0

    def test_duplicates_do_not_inflate(self):
        result = recall_at_k(["d1", "d1", "d1", "d2"], ["d1", "d2"], 4)
        assert result == 1.0

    def test_k_zero(self):
        result = recall_at_k(["d1", "d2"], ["d1"], 0)
        assert result == 0.0

    def test_k_larger_than_retrieved(self):
        result = recall_at_k(["d1"], ["d1", "d2"], 10)
        assert result == 0.5


class TestHitAtK:
    def test_hit_true(self):
        result = hit_at_k(["d1", "d2", "d3"], ["d3", "d4"], 3)
        assert result == 1.0

    def test_hit_false(self):
        result = hit_at_k(["d1", "d2", "d3"], ["d4", "d5"], 3)
        assert result == 0.0

    def test_hit_at_rank_1(self):
        result = hit_at_k(["d1", "d2"], ["d1"], 1)
        assert result == 1.0

    def test_empty_expected(self):
        result = hit_at_k(["d1", "d2"], [], 5)
        assert result == 0.0


class TestReciprocalRank:
    def test_rank_1(self):
        result = reciprocal_rank(["d1", "d2", "d3"], ["d1"])
        assert result == 1.0

    def test_rank_3(self):
        result = reciprocal_rank(["d1", "d2", "d3"], ["d3"])
        assert result == 1.0 / 3.0

    def test_no_relevant_doc(self):
        result = reciprocal_rank(["d1", "d2", "d3"], ["d4"])
        assert result == 0.0

    def test_empty_expected(self):
        result = reciprocal_rank(["d1", "d2"], [])
        assert result == 0.0

    def test_duplicates_do_not_inflate(self):
        result = reciprocal_rank(["d1", "d1", "d2", "d3"], ["d2"])
        assert result == 0.5

    def test_duplicates_do_not_deflate_rank(self):
        result = reciprocal_rank(["d1", "d1", "d1", "d2", "d3"], ["d1"])
        assert result == 1.0

    def test_first_relevant_at_rank_2(self):
        result = reciprocal_rank(["d1", "d2", "d3"], ["d2"])
        assert result == 0.5

    def test_multiple_expected_first_counts(self):
        result = reciprocal_rank(["d1", "d2", "d3"], ["d3", "d1"])
        assert result == 1.0


class TestMeanReciprocalRank:
    def test_average(self):
        result = mean_reciprocal_rank([1.0, 0.5, 0.0])
        assert result == 0.5

    def test_empty_list(self):
        result = mean_reciprocal_rank([])
        assert result == 0.0

    def test_all_perfect(self):
        result = mean_reciprocal_rank([1.0, 1.0, 1.0])
        assert result == 1.0


class TestExpectedDocCoverage:
    def test_basic_coverage(self):
        result = expected_doc_coverage(["d1", "d2", "d3"], ["d1", "d4"], 3)
        assert result == 0.5

    def test_empty_expected(self):
        result = expected_doc_coverage(["d1", "d2"], [], 5)
        assert result == 0.0

    def test_no_overlap(self):
        result = expected_doc_coverage(["d1", "d2"], ["d3"], 2)
        assert result == 0.0

    def test_duplicates_do_not_inflate(self):
        result = expected_doc_coverage(["d1", "d1", "d2"], ["d1", "d2"], 3)
        assert result == 1.0
