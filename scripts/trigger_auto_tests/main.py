import time

import click
from dohq_teamcity import TeamCity

from scripts.trigger_auto_tests.utils.helpers import (
    AutoTestsInfo,
    is_build_finished,
    is_build_success,
    is_shell_uses_package,
    trigger_auto_tests_build2,
)

TC_URL = "http://tc"
BUILDS_CHECK_DELAY = 10


def main(tc_user: str, tc_password: str):
    triggered_builds: dict[str, int] = {}
    builds_statuses: dict[str, bool] = {}
    errors = []
    tc = TeamCity(TC_URL, auth=(tc_user, tc_password))
    tests_info = AutoTestsInfo.get_current(tc)

    for shell_name in tests_info.supported_shells:
        try:
            if is_shell_uses_package(shell_name, tests_info):
                click.echo(f"{shell_name} Automation tests build triggering")
                build_id = trigger_auto_tests_build2(tc, shell_name, tests_info)
                triggered_builds[shell_name] = build_id
            else:
                click.echo(f"{shell_name} skipped tests")
        except Exception as e:
            errors.append(e)
            click.echo(e, err=True)

    while triggered_builds:
        time.sleep(BUILDS_CHECK_DELAY)
        for shell_name, build_id in triggered_builds.copy().items():
            build = tc.builds.get(f"id:{build_id}")
            if is_build_finished(build):
                builds_statuses[shell_name] = is_build_success(build)
                triggered_builds.pop(shell_name)

    if errors:
        raise Exception("There were errors running automation tests.")
