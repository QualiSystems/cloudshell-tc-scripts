from typing import Optional

from dohq_teamcity import Build

from scripts.utils.env import BuildEnv
from scripts.utils.tc_helpers import get_tc_client


class TC:
    def __init__(
        self,
        url: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self._tc_client = get_tc_client(url, user, password)

    def get_current_build(self) -> Build:
        build_env = BuildEnv()
        bt = self._tc_client.projects.get_build_type(
            project_locator=f"name:{build_env.project_name}",
            bt_locator=f"name:{build_env.bt_name}",
        )
        build = bt.get_builds(
            locator=(
                f"number:{build_env.build_num},"
                f"branch:(unspecified:any),"
                f"running:any"
            )
        )[0]
        return build

    def get_build_commits(self, build: Build) -> list[str]:
        changes = self._tc_client.changes.get_changes(build=build.id)
        return [change.version for change in changes]
