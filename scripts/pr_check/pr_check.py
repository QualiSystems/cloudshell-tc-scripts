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
            f"PR {pull.number} was created by user that is not a member of the "
            f"repo organization"
        )


def validate_pr_target_branch_in_valid_branches(pull: PullRequest, valid_branches: str):
    target_branch = pull.base.ref
    if target_branch not in map(str.strip, valid_branches.split(",")):
        raise ValueError(
            f"Target branch {target_branch} is not in valid branches {valid_branches}"
        )


def verify_user_can_trigger_build(
    vcs_root_url: str,
    pr_number: str,
    valid_branches: str,
    token: str,
):
    _, owner, repo_name = vcs_root_url.removesuffix(".git").rsplit("/", 2)
    github = Github(token)
    repo = github.get_repo(f"{owner}/{repo_name}")
    pull = repo.get_pull(int(pr_number))

    validate_pr_target_branch_in_valid_branches(pull, valid_branches)
    validate_author_pr_is_member_of_org(repo, github, pull)
