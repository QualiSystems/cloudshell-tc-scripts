from typing import Generator, Optional

from dohq_teamcity import Build, BuildType, ModelProperty, Properties
from dohq_teamcity.rest import RESTClientObject

from scripts.utils.models import BuildEnv
from scripts.utils.tc_helpers import get_tc_client


class TC:
    def __init__(
        self,
        url: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self._tc_client = get_tc_client(url, user, password)

    def get_current_build(self) -> "Build":
        env = BuildEnv()
        bt = self.get_build_type(env.bt_name, project_name=env.project_name)
        build = self.get_build_from_bt(bt, build_num=env.build_num)
        return build

    def get_build_commits(self, build: "Build") -> list[str]:
        changes = self._tc_client.changes.get_changes(build=build.id)
        return [change.version for change in changes]

    def get_build_type(
        self,
        name: str,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None,
    ) -> "BuildType":
        if project_id:
            project_locator = f"id:{project_id}"
        elif project_name:
            project_locator = f"name:{project_name}"
        else:
            raise ValueError("You have to specified project_id or project_name")

        return self._tc_client.projects.get_build_type(
            project_locator=project_locator,
            bt_locator=f"name:{name}",
        )

    @staticmethod
    def get_build_params(build: "Build") -> dict:
        return {pr.name: pr.value for pr in build.get_build_actual_parameters()}

    @staticmethod
    def is_build_success(build: "Build") -> bool:
        return build.status.lower() == "success"

    @staticmethod
    def is_build_finished(build: "Build") -> bool:
        return build.state.lower() == "finished"

    def yield_builds_from_bt(
        self,
        build_type: "BuildType",
        build_num: Optional[str] = None,
        param_filter: Optional[dict[str, str]] = None,
    ) -> Generator["Build", None, None]:
        kwargs = {}
        if build_num:
            locator = f"number:{build_num}," f"branch:(unspecified:any)," f"running:any"
            kwargs["locator"] = locator

        builds = build_type.get_builds(**kwargs)

        if param_filter:
            param_filter_set = set(param_filter.items())
            builds = (
                build
                for build in builds
                if param_filter_set.issuperset(self.get_build_params(build).items())
            )

        yield from builds

    def get_build_from_bt(
        self,
        build_type: "BuildType",
        build_num: Optional[str] = None,
        param_filter: Optional[dict[str, str]] = None,
    ) -> "Build":
        try:
            build = next(self.yield_builds_from_bt(build_type, build_num, param_filter))
        except StopIteration:
            raise ValueError(
                f"Build in {build_type.name} BT for params {build_num=}, "
                f"{param_filter=} not found"
            )
        return build

    def get_build(self, build_id: int) -> "Build":
        return self._tc_client.builds.get(f"id:{build_id}")

    def trigger_build(
        self,
        bt_id: str,
        properties: Optional[dict[str, str]] = None,
        move_to_top: bool = True,
    ) -> "Build":
        kwargs = {"build_type_id": bt_id}
        if properties:
            kwargs["properties"] = Properties(
                _property=[ModelProperty(k, v) for k, v in properties.items()],
            )
        new_build = Build(**kwargs)
        self.update_tc_csrf()
        build = self._tc_client.build_queues.queue_new_build(
            body=new_build, move_to_top=move_to_top
        )
        return build

    def update_tc_csrf(self):
        # if not do this before triggering build it fails with 403: CSRF =/
        # https://github.com/devopshq/teamcity/issues/24
        self._tc_client.rest_client = RESTClientObject(self._tc_client.configuration)
