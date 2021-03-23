import time
from pathlib import Path

import click

from scripts.trigger_auto_tests.utils.helpers import (
    get_file_content_from_github,
    get_package_version,
    is_package_in_requirements,
    trigger_auto_tests_build,
)

from .utils.tc_api import TeamCityAPI

BUILDS_CHECK_DELAY = 30


def main(
    supported_shells: list[str],
    automation_project_id: str,
    package_name: str,
    package_path: Path,
    package_vcs_url: str,
    package_commit_id: str,
    tc_url: str,
    tc_user: str,
    tc_password: str,
):
    triggered_builds = {}
    builds_statuses = {}
    tc_api = TeamCityAPI(tc_url, tc_user, tc_password)

    for shell_name in supported_shells:
        requirements = get_file_content_from_github(
            shell_name, "src/requirements.txt"
        ).splitlines()
        package_version = get_package_version(package_path)
        if is_package_in_requirements(requirements, package_name, package_version):
            click.echo(f"{shell_name} Automation tests build triggering")
            build_queue_id = trigger_auto_tests_build(
                tc_api,
                shell_name,
                automation_project_id=automation_project_id,
                package_vcs_url=package_vcs_url,
                package_commit_id=package_commit_id,
            )
            triggered_builds[shell_name] = build_queue_id
        else:
            click.echo(f"{shell_name} skipped tests")

    while triggered_builds:
        time.sleep(BUILDS_CHECK_DELAY)

        for shell_name, build_queue_id in triggered_builds.copy().items():
            data = tc_api.get_triggered_build_details(build_queue_id)
            if data.state == data.state.FINISHED:
                click.echo(
                    f"{shell_name} Automation tests is finished "
                    f"with status {data.status.value}"
                )
                triggered_builds.pop(shell_name)
                builds_statuses[shell_name] = data.status == data.status.SUCCESS

    return all(builds_statuses.values())
