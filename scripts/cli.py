from typing import Optional

import click

from scripts.client import TC
from scripts.utils.models import AutoTestsInfo
from scripts.utils.trigger_helpers import trigger_tests


@click.group()
def cli():
    pass


@cli.command(
    "trigger-auto-tests",
    help="Trigger Automated Tests on TeamCity for specified Shells and changed package",
)
@click.option("--tc-url", required=False, help="TeamCity URL")
@click.option("--tc-user", required=False, help="TeamCity User")
@click.option("--tc-password", required=False, help="TeamCity Password")
def trigger_auto_tests(
    tc_url: Optional[str], tc_user: Optional[str], tc_password: Optional[str]
):
    tc = TC(tc_url, tc_user, tc_password)
    current_build = tc.get_current_build()
    tests_info = AutoTestsInfo.from_current_build(current_build)
    trigger_tests(tests_info, tc)


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


@cli.command(
    "trigger-qualix-auto-tests",
    help="Trigger Qualix Automated Tests on TeamCity for specified qualix ip",
)
@click.option("--tc-url", required=False, help="TeamCity URL")
@click.option("--tc-user", required=False, help="TeamCity User")
@click.option("--tc-password", required=False, help="TeamCity Password")
@click.option("--qualix-host", required=True, help="Tested Qualix host")
def trigger_qualix_auto_tests(
    tc_url: Optional[str],
    tc_user: Optional[str],
    tc_password: Optional[str],
    qualix_host: str,
):
    tc = TC(tc_url, tc_user, tc_password)
    current_build = tc.get_current_build()
    tests_info = AutoTestsInfo.from_current_build(current_build)
    tests_info.qualix_host = qualix_host
    trigger_tests(tests_info, tc)


if __name__ == "__main__":
    cli()
