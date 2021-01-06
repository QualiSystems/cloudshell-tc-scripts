from collections.abc import Iterator
from typing import Optional

import requests

from scripts.trigger_auto_tests.utils.tc_api_models import (
    BuildConfLocator,
    BuildConfOutputModel,
    QueuedBuildDetailsModel,
)


class TeamCityBaseError(Exception):
    pass


class TeamCityRequestError(TeamCityBaseError):
    def __init__(self, tc_msg: str):
        self.tc_msg = tc_msg


class TeamCityAPI:
    def __init__(self, tc_url: str, user: str, password: str):
        self._tc_api_url = f"{tc_url}/app/rest"
        self._user = user
        self._password = password

        self._default_headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        self._build_queue_api_url = f"{self._tc_api_url}/buildQueue"
        self._build_template_api_url = f"{self._tc_api_url}/buildTypes"

    def _request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        try:
            fn = {"get": requests.get, "post": requests.post}[method.lower()]
        except KeyError:
            raise TeamCityBaseError(f"Unsupported request method {method}")

        headers = {**self._default_headers, **(headers or {})}

        resp = fn(
            url, json=data or {}, auth=(self._user, self._password), headers=headers
        )
        if not resp.ok:
            raise TeamCityRequestError(resp.content.decode())

        return resp.json()

    def _get(self, url: str, headers: Optional[dict] = None) -> dict:
        return self._request("get", url, headers)

    def _post(
        self, url: str, headers: Optional[dict] = None, data: Optional[dict] = None
    ) -> dict:
        return self._request("post", url, headers, data)

    def get_build_templates(
        self, locator_data: dict[str, str] = None, headers: Optional[dict] = None
    ) -> Iterator[BuildConfOutputModel]:
        url = self._build_template_api_url
        if locator_data:
            locator = BuildConfLocator.parse_obj(locator_data)
            url += f"?locator={locator}"

        data_map = self._get(url, headers=headers)
        return map(BuildConfOutputModel.parse_obj, data_map["buildType"])

    def get_triggered_build_details(
        self, build_id: int, headers: Optional[dict] = None
    ) -> QueuedBuildDetailsModel:
        url = f"{self._build_queue_api_url}/id:{build_id}"
        data_map = self._get(url, headers=headers)
        return QueuedBuildDetailsModel.parse_obj(data_map)

    def trigger_builds(
        self,
        locator_data: dict,
        branch: str = "master",
        headers: Optional[dict] = None,
        additional_data: Optional[dict] = None,
    ) -> QueuedBuildDetailsModel:
        # locator can include name, project, template keys it should be str type
        url = self._build_queue_api_url
        locator = BuildConfLocator.parse_obj(locator_data)
        data = {
            "buildType": {"locator": str(locator)},
            "branch": branch,
            **(additional_data or {}),
        }

        data_map = self._post(url, headers=headers, data=data)
        return QueuedBuildDetailsModel.parse_obj(data_map)
