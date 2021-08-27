from typing import Optional

import click

from scripts.client import TC
from scripts.pr_check.pr_check import verify_user_can_trigger_build
from scripts.trigger_auto_tests.main import main


@click.group()
def cli():
    pass


@cli.command(
    "trigger-auto-tests",
    help="Trigger Automated Tests on TeamCity for specified Shells and changed package",
)
@click.option("--tc-user", required=True, help="TeamCity User")
@click.option("--tc-password", required=True, help="TeamCity Password")
def trigger_auto_tests(tc_user: str, tc_password: str):
    main(tc_user, tc_password)


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


@cli.command("get-commits-from-changes", help="Return commits from the VCS changes.")
@click.option("--tc-url", required=False, help="TeamCity URL")
@click.option("--tc-user", required=False, help="TeamCity User")
@click.option("--tc-password", required=False, help="TeamCity Password")
def get_commits_from_changes(
    tc_url: Optional[str], tc_user: Optional[str], tc_password: Optional[str]
):
    tc = TC(tc_url, tc_user, tc_password)
    current_build = tc.get_current_build()
    commits = tc.get_build_commits(current_build)
    click.echo(" ".join(commits))


if __name__ == "__main__":
    cli()
