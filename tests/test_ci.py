import pytest

from raiden_synapse_modules import stub


def test_something(true_fixture):
    assert stub.return_true()
    assert true_fixture is True


@pytest.mark.xfail(reason="expected failure")
def test_fail():
    assert not True
