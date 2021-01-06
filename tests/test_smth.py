import pytest

from scripts.pr_check.pr_check import is_pr_target_branch_in_valid_branches


def test_smth():
    with pytest.raises(TypeError):
        is_pr_target_branch_in_valid_branches()
