import sys
from pathlib import Path

import click

from scripts.pr_check.pr_check import verify_user_can_trigger_build
from scripts.trigger_auto_tests.main import main
from scripts.trigger_auto_tests.utils.cli_helpers import PathPath


@click.group()
def cli():
    pass


@cli.command(
    "trigger-auto-tests",
    help="Trigger Automated Tests on TeamCity for specified Shells and changed package",
)
@click.option(
    "--supported-shells",
    required=True,
    help='Specify as Shell names divided by ";"',
)
@click.option(
    "--automation-project-id",
    required=True,
    help="Project id for the Automated tests",
)
@click.option("--package-name", required=True, help="Updated package name")
@click.option(
    "--package-path",
    required=True,
    type=PathPath(exists=True, file_okay=False),
    help="Path to the updated package",
)
@click.option(
    "--package-vcs-url",
    required=True,
    help="URL of the updated package VCS",
)
@click.option(
    "--package-commit-id",
    required=True,
    help="Commit id of the updated package that would be used",
)
@click.option("--tc-url", required=True, help="TeamCity URL")
@click.option("--tc-user", required=True, help="TeamCity User")
@click.option("--tc-password", required=True, help="TeamCity Password")
def trigger_auto_tests(
    supported_shells: str,
    automation_project_id: str,
    package_name: str,
    package_path: Path,
    package_vcs_url: str,
    package_commit_id: str,
    tc_url: str,
    tc_user: str,
    tc_password: str,
) -> bool:
    supported_shells = list(map(str.strip, supported_shells.split(";")))
    is_success = main(
        supported_shells=supported_shells,
        automation_project_id=automation_project_id,
        package_name=package_name,
        package_path=package_path,
        package_vcs_url=package_vcs_url,
        package_commit_id=package_commit_id,
        tc_url=tc_url,
        tc_user=tc_user,
        tc_password=tc_password,
    )
    if not is_success:
        sys.exit(1)
    return is_success


@cli.command(
    "verify-user-can-trigger-build",
    help=(
        "Check that target branch of the PR is in the valid branches and that "
        "author of the PR is a member of the repo organization"
    ),
)
@click.option("--vcs-root-url", required=True, help="VCS URL")
@click.option(
    "--branch-name",
    required=True,
    help="The branch name. Branch contains pull request id or branch name",
)
@click.option(
    "--valid-branches",
    default="master",
    show_default=True,
    help=(
        "The target branches for which could be triggered builds. "
        "<branch-name>,<branch-name>"
    ),
)
@click.option(
    "--token",
    required=True,
    help=(
        "Token of the user that is a member of the organization, "
        "should be permission 'read:org'"
    ),
)
def verify_user_can_trigger(
    vcs_root_url: str,
    branch_name: str,
    valid_branches: str,
    token: str,
):
    verify_user_can_trigger_build(
        vcs_root_url=vcs_root_url,
        branch_name=branch_name,
        valid_branches=valid_branches.split(","),
        token=token,
    )


if __name__ == "__main__":
    cli()
