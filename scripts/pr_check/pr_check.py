import click
from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository


def validate_author_pr_is_member_of_org(
    repo: Repository, github: Github, pull: PullRequest
):
    org_login = repo.organization.login
    org = github.get_organization(org_login)
    token_user = github.get_user(github.get_user().login)
    if not org.has_in_members(token_user):
        raise ValueError(
            f"{token_user.login} is not the member of the {org.login} or doesn't have"
            f"rights 'read:org' so cannot check members of the organization"
        )
    # repo.organization.has_in_members(user) always returns false ¯\_(ツ)_/¯
    if not org.has_in_members(pull.user):
        raise ValueError(
            f"PR {pull.number} was created by a user that is not a member of the "
            f"repo organization"
        )


def validate_pr_target_branch_in_valid_branches(
    pull: PullRequest, valid_branches: list[str]
):
    target_branch = pull.base.ref
    if target_branch not in map(str.strip, valid_branches):
        emsg = (
            f"The target branch {target_branch} is not in valid "
            f"branches {valid_branches}"
        )
        raise ValueError(emsg)


def get_pull_request_number(branch_name: str) -> int:
    return int(branch_name.removeprefix("pull/"))


def is_pull_request_branch(branch_name: str) -> bool:
    try:
        get_pull_request_number(branch_name)
    except ValueError:
        result = False
    else:
        result = True
    return result


def get_branch_name(branch_name: str) -> str:
    return branch_name.removeprefix("refs/heads/")


def print_stop_tc_build_msg(comment: str, re_add_to_queue: bool = False):
    str_re_add = str(re_add_to_queue).lower()
    click.echo(f"##teamcity[buildStop comment='{comment}' readdToQueue='{str_re_add}']")


def verify_user_can_trigger_build(
    vcs_root_url: str,
    branch_name: str,
    valid_branches: list[str],
    token: str,
):
    _, owner, repo_name = vcs_root_url.removesuffix(".git").rsplit("/", 2)
    github = Github(token)
    repo = github.get_repo(f"{owner}/{repo_name}")

    if is_pull_request_branch(branch_name):
        pull = repo.get_pull(get_pull_request_number(branch_name))
        try:
            validate_pr_target_branch_in_valid_branches(pull, valid_branches)
            validate_author_pr_is_member_of_org(repo, github, pull)
        except ValueError as e:
            print_stop_tc_build_msg(str(e))
    else:
        if get_branch_name(branch_name) not in valid_branches:
            print_stop_tc_build_msg(
                f"The branch '{branch_name}' is not in valid branches "
                f"'{valid_branches}'"
            )
