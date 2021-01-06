from github import Github


def is_author_pr_is_member_of_org(
    vcs_root_url: str, pr_number: str, token: str
) -> bool:
    _, owner, repo_name = vcs_root_url.removesuffix(".git").rsplit("/", 2)
    github = Github(token)
    repo = github.get_repo(f"{owner}/{repo_name}")
    pull = repo.get_pull(int(pr_number))
    org_login = repo.organization.login
    org = github.get_organization(org_login)
    token_user = github.get_user(github.get_user().login)
    if not org.has_in_members(token_user):
        raise ValueError(
            f"{token_user.login} is not the member of the {org.login} or doesn't have"
            f"rights 'read:org' so cannot check members of the organization"
        )
    # repo.organization.has_in_members(user) always returns false ¯\_(ツ)_/¯
    return org.has_in_members(pull.user)


def is_pr_target_branch_in_valid_branches(target_branch: str, valid_branches: str):
    return target_branch in map(str.strip, valid_branches.split(","))


def verify_user_can_trigger_build(
    vcs_root_url: str,
    pr_number: str,
    target_branch: str,
    valid_branches: str,
    token: str,
):
    if not is_pr_target_branch_in_valid_branches(target_branch, valid_branches):
        raise ValueError(
            f"Target branch {target_branch} is not in valid branches {valid_branches}"
        )
    if not is_author_pr_is_member_of_org(vcs_root_url, pr_number, token):
        raise ValueError(
            f"PR {pr_number} was created by user that is not a member of the "
            f"repo organization"
        )
