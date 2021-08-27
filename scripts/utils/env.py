from pydantic import BaseSettings, Field

ENV_TC_URL_NAME = "TC_URL"
ENV_TC_USER_NAME = "TC_USER"
ENV_TC_PASSWORD_NAME = "TC_PASSWORD"
DEFAULT_TC_URL = "http://tc"


class BuildEnv(BaseSettings):
    bt_name: str = Field(..., env="TEAMCITY_BUILDCONF_NAME")
    project_name: str = Field(..., env="TEAMCITY_PROJECT_NAME")
    build_num: int = Field(..., env="BUILD_NUMBER")


class TcScriptEnv(BaseSettings):
    tc_url: str = Field("http://tc", env="TC_URL")
    tc_user: str = Field(..., env="TC_USER")
    tc_password: str = Field(..., env="TC_PASSWORD")
