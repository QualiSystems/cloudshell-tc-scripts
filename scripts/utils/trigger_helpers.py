import time
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import click
from teamcity.messages import TeamcityServiceMessages

if TYPE_CHECKING:
    from scripts.client import TC
    from scripts.utils.models import AutoTestsInfo

BUILDS_CHECK_DELAY = 10
PARAM_TRIGGERED_BY_URL = "conf.triggered_by_project.url"
PARAM_TRIGGERED_BY_COMMIT = "conf.triggered_by_project.commit_id"
PARAM_QUALIX_HOST = "conf.triggered_by_project.qualix_ip"


def trigger_tests(tests_info: "AutoTestsInfo", tc: "TC"):
    errors: list[Exception] = []
    triggered_builds: dict[str, int] = {}  # {shell_name: build_id}

    tc_msg = TeamcityServiceMessages()
    msg = "Re run failed builds" if tests_info.re_run_builds else "Run automated tests"
    click.echo(msg)

    with tc_msg.testSuite("Automation tests"):
        tc_msg.testCount(len(tests_info.supported_shells))
        for shell_name in tests_info.supported_shells:
            try:
                build_id = _run_tests_for_shell(tc, tc_msg, shell_name, tests_info)
                if build_id:
                    triggered_builds[shell_name] = build_id
            except Exception as e:
                errors.append(e)
                click.echo(e, err=True)

        builds_statuses, new_errors = _wait_build_finish(tc, tc_msg, triggered_builds)
        errors.extend(new_errors)

        if errors:
            raise Exception("There were errors running automation tests.")


def _run_tests_for_shell(
    tc: "TC",
    tc_msg: "TeamcityServiceMessages",
    shell_name: str,
    tests_info: "AutoTestsInfo",
) -> Optional[int]:
    if tests_info.re_run_builds and _is_last_build_successful(
        tc, tc_msg, shell_name, tests_info
    ):
        return

    build_id, build_url = _trigger_auto_tests_build(tc, shell_name, tests_info)
    if tests_info.re_run_builds:
        msg = f"{shell_name} Re run automation tests. {build_url}"
    else:
        msg = f"{shell_name} Automation tests build triggered. {build_url}"
    click.echo(msg)
    return build_id


def _wait_build_finish(
    tc: "TC", tc_msg: "TeamcityServiceMessages", triggered_builds: dict[str, int]
) -> tuple[dict[str, bool], list[Exception]]:
    builds_statuses: dict[str, bool] = {}
    errors: list[Exception] = []
    start_time = datetime.now()
    while triggered_builds:
        time.sleep(BUILDS_CHECK_DELAY)
        for shell_name, build_id in triggered_builds.copy().items():
            try:
                if (
                    is_success := _check_build(tc, tc_msg, shell_name, build_id)
                ) is not None:
                    builds_statuses[shell_name] = is_success
                    triggered_builds.pop(shell_name)
                    tc_msg.testFinished(
                        shell_name, testDuration=datetime.now() - start_time
                    )
            except Exception as e:
                errors.append(e)
                click.echo(e, err=True)
    return builds_statuses, errors


def _check_build(
    tc: "TC", tc_msg: "TeamcityServiceMessages", shell_name: str, build_id: int
) -> Optional[bool]:
    build = tc.get_build(build_id)
    if tc.is_build_finished(build):
        tc_msg.testStarted(shell_name)
        is_success = tc.is_build_success(build)
        if not is_success:
            tc_msg.testFailed(
                shell_name,
                f"{shell_name} Automation tests is finished with status {build.status}",
            )
        return is_success


def _trigger_auto_tests_build(
    tc: "TC",
    shell_name: str,
    tests_info: "AutoTestsInfo",
) -> tuple[int, str]:
    bt = tc.get_build_type(shell_name, project_id=tests_info.automation_project_id)
    prop = {
        PARAM_TRIGGERED_BY_URL: tests_info.vcs_url,
        PARAM_TRIGGERED_BY_COMMIT: tests_info.commit_id,
    }
    if tests_info.qualix_host is not None:
        prop[PARAM_QUALIX_HOST] = tests_info.qualix_host

    build = tc.trigger_build(
        bt.id,
        prop,
    )
    return build.id, build.web_url


def _is_last_build_successful(
    tc: "TC",
    tc_msg: "TeamcityServiceMessages",
    shell_name: str,
    tests_info: "AutoTestsInfo",
) -> bool:
    bt = tc.get_build_type(shell_name, project_id=tests_info.automation_project_id)
    try:
        build = tc.get_build_from_bt(
            bt,
            param_filter={
                PARAM_TRIGGERED_BY_URL: tests_info.vcs_url,
                PARAM_TRIGGERED_BY_COMMIT: tests_info.commit_id,
            },
        )
    except ValueError as e:
        click.echo(str(e))
        return False
    else:
        if is_success := tc.is_build_success(build):
            tc_msg.testIgnored(
                shell_name,
                f"{shell_name} last auto tests for this package and commit "
                f"id was successful, skip it. {build.web_url}",
            )
    return is_success
