from pathlib import PosixPath
from typing import Optional

from dohq_teamcity import Build
from pydantic import BaseSettings, Field

ENV_TC_URL_NAME = "TC_URL"
ENV_TC_USER_NAME = "TC_USER"
ENV_TC_PASSWORD_NAME = "TC_PASSWORD"
DEFAULT_TC_URL = "http://tc"


class BuildEnv(BaseSettings):
    bt_name: str = Field(..., env="TEAMCITY_BUILDCONF_NAME")
    project_name: str = Field(..., env="TEAMCITY_PROJECT_NAME")
    build_num: str = Field(..., env="BUILD_NUMBER")
    commit_id: str = Field(..., env="BUILD_VCS_NUMBER")


class TcScriptEnv(BaseSettings):
    tc_url: str = Field("http://tc", env="TC_URL")
    tc_user: str = Field(..., env="TC_USER")
    tc_password: str = Field(..., env="TC_PASSWORD")


class AutoTestsInfo(BuildEnv):
    supported_shells: list[str]
    automation_project_id: str
    re_run_builds: bool
    vcs_url: str
    path: PosixPath
    qualix_host: Optional[str] = None

    @classmethod
    def from_current_build(cls, build: "Build") -> "AutoTestsInfo":
        from scripts.client import TC

        params = TC.get_build_params(build)
        return cls(
            supported_shells=list(
                filter(bool, map(str.strip, params["conf.shells"].split(";")))
            ),
            automation_project_id=params["automation.project.id"],
            re_run_builds=params["re-run-builds"],
            vcs_url=params.get("vcsroot.url", "empty"),
            path=PosixPath(params["teamcity.build.checkoutDir"]),
        )
