def test_witty_marketer_heuristic(sample_output):
    if sample_output["style"]=="witty_marketer":
        witty_markers = ["wink","clever","pun","you'll love","boost"]
        assert any(w in sample_output["body"].lower() for w in witty_markers)