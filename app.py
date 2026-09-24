import argparse
import os
from typing import Any

from dotenv import load_dotenv
from composio import Composio

load_dotenv()


def get_client() -> Composio:
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError(
            "Set COMPOSIO_API_KEY in .env before running this example."
        )
    return Composio(api_key=api_key)


def list_github_tools(client: Composio, user_id: str) -> Any:
    return client.tools.get(user_id, toolkits=["github"])


def execute_first_available(
    client: Composio,
    user_id: str,
    slugs: list[str],
    arguments: dict[str, Any],
) -> Any:
    """Execute the first slug supported by the installed Composio catalog."""
    last_error: Exception | None = None
    for slug in slugs:
        try:
            return client.tools.execute(slug, arguments=arguments, user_id=user_id)
        except Exception as exc:
            last_error = exc
    raise RuntimeError(
        f"None of these GitHub tools worked: {', '.join(slugs)}. "
        "Run `python app.py tools` and use the slug returned by Composio."
    ) from last_error


def get_repo_metadata(client: Composio, user_id: str, owner: str, repo: str) -> Any:
    return execute_first_available(
        client,
        user_id,
        ["GITHUB_GET_REPOSITORY", "GITHUB_GET_REPO", "GITHUB_GET_REPOS"],
        {"owner": owner, "repo": repo},
    )


def create_issue(
    client: Composio,
    user_id: str,
    owner: str,
    repo: str,
    title: str,
    body: str,
) -> Any:
    return execute_first_available(
        client,
        user_id,
        ["GITHUB_CREATE_ISSUE", "GITHUB_CREATE_AN_ISSUE"],
        {"owner": owner, "repo": repo, "title": title, "body": body},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Composio GitHub integration demo")
    parser.add_argument(
        "action", choices=["tools", "repo", "issue"], nargs="?", default="repo"
    )
    parser.add_argument("--title", help="Issue title (required for issue action)")
    parser.add_argument("--body", default="Created with Composio.")
    args = parser.parse_args()

    user_id = os.getenv("COMPOSIO_USER_ID", "user-123")
    owner = os.getenv("GITHUB_OWNER", "innocentaluma11-rgb")
    repo = os.getenv("GITHUB_REPO", "TABERBNACLEFX-")
    client = get_client()

    if args.action == "tools":
        print(list_github_tools(client, user_id))
    elif args.action == "repo":
        print(get_repo_metadata(client, user_id, owner, repo))
    else:
        if not args.title:
            parser.error("--title is required when action is 'issue'")
        print(create_issue(client, user_id, owner, repo, args.title, args.body))


if __name__ == "__main__":
    main()
