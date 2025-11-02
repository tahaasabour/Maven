def test_length_budget(sample_output):
    assert len(sample_output["body"].split()) <= 120