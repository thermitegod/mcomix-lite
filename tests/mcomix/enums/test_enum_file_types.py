from mcomix.enums import FileTypes


def test_file_types():
    for f in FileTypes:
        assert isinstance(f.value, int)
