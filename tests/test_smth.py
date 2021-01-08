import pytest

from scripts.pr_check.pr_check import validate_pr_target_branch_in_valid_branches


def test_smth():
    with pytest.raises(TypeError):
        validate_pr_target_branch_in_valid_branches()
