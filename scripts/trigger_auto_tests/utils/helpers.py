from pathlib import Path

from github import Github, Repository, UnknownObjectException
from pip_download import PipDownloader

from scripts.trigger_auto_tests.utils.tc_api import TeamCityAPI

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


def trigger_auto_tests_build(
    tc_api: TeamCityAPI,
    shell_name: str,
    automation_project_id: str,
    package_vcs_url: str,
    package_commit_id: str,
) -> int:
    locator_data = {
        "name": shell_name,
        "project": automation_project_id,
    }
    additional_data = {
        "triggeringOptions": {"queueAtTop": True},
        "properties": {
            "property": [
                {"name": "conf.triggered_by_project.url", "value": package_vcs_url},
                {
                    "name": "conf.triggered_by_project.commit_id",
                    "value": package_commit_id,
                },
            ]
        },
    }
    data = tc_api.trigger_builds(locator_data, additional_data=additional_data)
    return data.id
