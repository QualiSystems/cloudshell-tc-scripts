import time
from typing import Optional

import click
from dohq_teamcity import TeamCity
from teamcity.messages import TeamcityServiceMessages

from scripts.trigger_auto_tests.utils.helpers import (
    AutoTestsInfo,
    is_build_finished,
    is_build_success,
    is_last_build_successful,
    is_shell_uses_package,
    trigger_auto_tests_build2,
)

TC_URL = "http://tc"
BUILDS_CHECK_DELAY = 10


def main(tc_user: str, tc_password: str):
    errors = []
    triggered_builds: dict[str, int] = {}
    tc = TeamCity(TC_URL, auth=(tc_user, tc_password))
    tests_info = AutoTestsInfo.get_current(tc)
    tc_msg = TeamcityServiceMessages()
    if tests_info.re_run_builds:
        click.echo("Re run failed builds")
    else:
        click.echo("Run automated tests")

    tc_msg.testCount(len(tests_info.supported_shells))
    with tc_msg.testSuite("Automation tests"):
        for shell_name in tests_info.supported_shells:
            try:
                build_id = _run_tests_for_shell(tc, tc_msg, shell_name, tests_info)
                triggered_builds[shell_name] = build_id
            except Exception as e:
                errors.append(e)
                click.echo(e, err=True)

        builds_statuses, new_errors = _wait_build_finish(tc, tc_msg, triggered_builds)
        errors.extend(new_errors)

        if errors:
            raise Exception("There were errors running automation tests.")
    return all(builds_statuses.values())


def _run_tests_for_shell(
    tc: TeamCity,
    tc_msg: TeamcityServiceMessages,
    shell_name: str,
    tests_info: AutoTestsInfo,
) -> Optional[int]:
    build_id = None
    if is_shell_uses_package(shell_name, tests_info):
        if tests_info.re_run_builds:
            if is_last_build_successful(tc, shell_name, tests_info):
                tc_msg.testIgnored(
                    shell_name,
                    f"{shell_name} last auto tests for this package and commit "
                    f"id was successful, skip it",
                )
            else:
                click.echo(f"{shell_name} Re run automation tests")
                build_id = trigger_auto_tests_build2(tc, shell_name, tests_info)
        else:
            click.echo(f"{shell_name} Automation tests build triggering")
            build_id = trigger_auto_tests_build2(tc, shell_name, tests_info)
    else:
        tc_msg.testIgnored(
            shell_name,
            f"{shell_name} is not uses package with this version, skipped tests",
        )
    return build_id


def _wait_build_finish(
    tc: TeamCity, tc_msg: TeamcityServiceMessages, triggered_builds: dict[str, int]
) -> tuple[dict[str, bool], list[Exception]]:
    builds_statuses = {}
    errors = []
    start_time = time.time()
    while triggered_builds:
        time.sleep(BUILDS_CHECK_DELAY)
        for shell_name, build_id in triggered_builds.copy().items():
            try:
                build = tc.builds.get(f"id:{build_id}")
                if is_build_finished(build):
                    with tc_msg.test(shell_name, testDuration=time.time() - start_time):
                        is_success = is_build_success(build)
                        builds_statuses[shell_name] = is_success
                        triggered_builds.pop(shell_name)
                        if not is_success:
                            tc_msg.testFailed(
                                shell_name,
                                f"{shell_name} Automation tests is finished"
                                f" with status {build.status}",
                            )
            except Exception as e:
                errors.append(e)
                click.echo(e, err=True)
    return builds_statuses, errors
