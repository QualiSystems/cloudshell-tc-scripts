from github import Github, Repository, UnknownObjectException

REPOS_OWNER = "QualiSystems"


def get_file_content_from_github(
    repo_name: str, file_path: str, repo_owner: str = REPOS_OWNER
) -> str:
    try:
        repo: Repository = Github().get_repo(f"{repo_owner}/{repo_name}")
    except UnknownObjectException as e:
        raise ValueError(f"Cannot find repo {repo_owner}/{repo_name}") from e
    return repo.get_contents(file_path, "master").decoded_content.decode()
