from app.ui import load_tipo_options


def test_load_tipo_options_contains_bebida():
    opts = load_tipo_options()
    assert isinstance(opts, list)
    assert any(o.startswith('Bebida') for o in opts)


def test_all_start_with_uppercase():
    opts = load_tipo_options()
    assert all(o and o[0].isupper() for o in opts)