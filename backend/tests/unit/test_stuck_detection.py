from backend.src.services.guards import check_stuck, hash_args


def test_stuck_detection_three_repeats():
    steps = [("search_docs", "abc123"), ("search_docs", "abc123"), ("search_docs", "abc123")]
    terminated, reason = check_stuck(steps)
    assert terminated is True
    assert reason == "stuck"


def test_stuck_detection_non_repeating():
    steps = [("search_docs", "abc123"), ("search_web", "def456"), ("calculate", "ghi789")]
    terminated, reason = check_stuck(steps)
    assert terminated is False
    assert reason is None


def test_stuck_detection_two_repeats_not_enough():
    steps = [("search_docs", "abc123"), ("search_docs", "abc123")]
    terminated, reason = check_stuck(steps)
    assert terminated is False
    assert reason is None


def test_stuck_detection_interrupted_sequence():
    steps = [("search_docs", "abc123"), ("search_docs", "abc123"), ("search_web", "def456"), ("search_docs", "abc123")]
    terminated, reason = check_stuck(steps)
    assert terminated is False
    assert reason is None


def test_stuck_detection_different_args():
    steps = [("search_docs", "abc123"), ("search_docs", "def456"), ("search_docs", "ghi789")]
    terminated, reason = check_stuck(steps)
    assert terminated is False
    assert reason is None


def test_stuck_detection_empty():
    terminated, reason = check_stuck([])
    assert terminated is False
    assert reason is None


def test_stuck_detection_single():
    terminated, reason = check_stuck([("search_docs", "abc123")])
    assert terminated is False
    assert reason is None


def test_hash_args_consistent():
    args = {"query": "test", "limit": 10}
    h1 = hash_args(args)
    h2 = hash_args(args)
    assert h1 == h2
    assert len(h1) == 16


def test_hash_args_none():
    assert hash_args(None) == ""


def test_hash_args_different():
    h1 = hash_args({"query": "a"})
    h2 = hash_args({"query": "b"})
    assert h1 != h2
