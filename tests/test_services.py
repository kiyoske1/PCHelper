from pc_helper.system import format_size


def test_format_size_bytes():
    assert format_size(0) == "0.0 B"


def test_format_size_megabytes():
    assert format_size(1024 * 1024) == "1.0 MB"
