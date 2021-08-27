from typing import Optional

import click

from scripts.client import TC
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
