import os
from pathlib import Path, PosixPath

from dohq_teamcity import Build, BuildType, ModelProperty, Properties, TeamCity
from dohq_teamcity.rest import RESTClientObject
from github import Github, Repository, UnknownObjectException
from pip_download import PipDownloader
from pydantic import BaseModel

REPOS_OWNER = "QualiSystems"


def get_file_content_from_github(
    repo_name: str, file_path: str, repo_owner: str = REPOS_OWNER
) -> str:
    try:
        repo: Repository = Github().get_repo(f"{repo_owner}/{repo_name}")
    except UnknownObjectException as e:
        raise ValueError(f"Cannot find repo {repo_owner}/{repo_name}") from e
    return repo.get_contents(file_path, "master").decoded_content.decode()


def get_package_version(package_path: Path) -> str:
    with package_path.joinpath("version.txt").open() as fo:
        return fo.read().strip()


def is_package_in_requirements(
    requirements: list[str], package_name: str, package_version: str
) -> bool:
    pip_downloader = PipDownloader()
    req_lst = pip_downloader.resolve_requirements_range(requirements)
    for req in req_lst:
        if req.name == package_name:
            return req.specifier.contains(package_version)
    return False


def is_shell_uses_package(shell_name: str, tests_info: "AutoTestsInfo") -> bool:
    requirements = get_file_content_from_github(
        shell_name, "src/requirements.txt"
    ).splitlines()
    package_version = get_package_version(tests_info.path)
    return is_package_in_requirements(requirements, tests_info.name, package_version)


def trigger_auto_tests_build(
    tc: TeamCity,
    shell_name: str,
    tests_info: "AutoTestsInfo",
) -> tuple[int, str]:
    bt = tc.projects.get_build_type(
        project_locator=f"id:{tests_info.automation_project_id}",
        bt_locator=f"name:{shell_name}",
    )
    properties = Properties(
        _property=[
            ModelProperty("conf.triggered_by_project.url", tests_info.vcs_url),
            ModelProperty("conf.triggered_by_project.commit_id", tests_info.commit_id),
        ]
    )
    new_build = Build(build_type_id=bt.id, properties=properties)
    update_tc_csrf(tc)
    build = tc.build_queues.queue_new_build(body=new_build, move_to_top=True)
    return build.id, build.web_url


def is_last_build_successful(
    tc: TeamCity, shell_name: str, tests_info: "AutoTestsInfo"
) -> tuple[bool, str]:
    bt: BuildType = tc.projects.get_build_type(
        project_locator=f"id:{tests_info.automation_project_id}",
        bt_locator=f"name:{shell_name}",
    )
    build_url = ""
    for build in bt.get_builds():
        params = get_build_params(build)
        if (
            params["conf.triggered_by_project.url"] == tests_info.vcs_url
            and params["conf.triggered_by_project.commit_id"] == tests_info.commit_id
        ):
            is_success = is_build_success(build)
            build_url = build.web_url
            break
    else:
        is_success = False
    return is_success, build_url


def is_build_finished(build: Build) -> bool:
    return build.state.lower() == "finished"


def is_build_success(build: Build) -> bool:
    return build.status.lower() == "success"


def update_tc_csrf(tc: TeamCity):
    # if not do this before triggering build it fails with 403: CSRF =/
    # https://github.com/devopshq/teamcity/issues/24
    tc.rest_client = RESTClientObject(tc.configuration)


def get_build_params(build: Build) -> dict:
    return {pr.name: pr.value for pr in build.get_build_actual_parameters()}


class AutoTestsInfo(BaseModel):
    number: int
    params: dict
    vcs_url: str
    commit_id: str
    path: Path
    name: str
    supported_shells: list[str]
    automation_project_id: str
    re_run_builds: bool

    @classmethod
    def get_current(cls, tc: TeamCity) -> "AutoTestsInfo":
        number = os.getenv("BUILD_NUMBER")
        name = os.getenv("TEAMCITY_BUILDCONF_NAME")
        commit_id = os.getenv("BUILD_VCS_NUMBER")
        project_name = os.getenv("TEAMCITY_PROJECT_NAME")
        bt_name = os.getenv("TEAMCITY_BUILDCONF_NAME")
        bt = tc.projects.get_build_type(
            project_locator=f"name:{project_name}", bt_locator=f"name:{bt_name}"
        )
        build = bt.get_builds(
            locator=f"number:{number},branch:(unspecified:any),running:true"
        )[0]
        params = get_build_params(build)
        vcs_url = params["vcsroot.url"]
        path = PosixPath(params["teamcity.build.checkoutDir"])
        supported_shells = list(
            filter(bool, map(str.strip, params["conf.shells"].split(";")))
        )
        automation_project_id = params["automation.project.id"]
        re_run_builds = params["re-run-builds"]
        return cls(
            number=int(number),
            params=params,
            vcs_url=vcs_url,
            commit_id=commit_id,
            path=path,
            name=name,
            supported_shells=supported_shells,
            automation_project_id=automation_project_id,
            re_run_builds=re_run_builds,
        )
