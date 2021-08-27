import pytest

from scripts.utils.trigger_helpers import trigger_tests


def test_smth():
    with pytest.raises(TypeError):
        trigger_tests()
