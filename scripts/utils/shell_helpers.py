from typing import TYPE_CHECKING

from pip_download import PipDownloader

from scripts.utils.github_helpers import get_file_content_from_github

if TYPE_CHECKING:
    from pathlib import Path

    from scripts.utils.models import AutoTestsInfo


def is_shell_uses_package(shell_name: str, tests_info: "AutoTestsInfo") -> bool:
    requirements = get_file_content_from_github(
        shell_name, "src/requirements.txt"
    ).splitlines()
    package_version = get_package_version(tests_info.path)
    return is_package_in_requirements(requirements, tests_info.bt_name, package_version)


def get_package_version(package_path: "Path") -> str:
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
