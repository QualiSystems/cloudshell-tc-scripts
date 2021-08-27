from typing import Optional

from dohq_teamcity import TeamCity

from scripts.utils.models import TcScriptEnv


def get_tc_client(
    url: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
) -> TeamCity:
    script_kwargs = {"tc_url": url, "tc_user": user, "tc_password": password}
    script_kwargs = {k: v for k, v in script_kwargs.items() if v}
    params = TcScriptEnv(**script_kwargs)
    return TeamCity(params.tc_url, auth=(params.tc_user, params.tc_password))
