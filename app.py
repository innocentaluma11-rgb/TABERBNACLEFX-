import argparse
import json
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


def print_result(value: Any) -> None:
    """Print SDK objects in a useful, copy/paste-friendly form."""
    try:
        print(json.dumps(value, indent=2, default=str))
    except TypeError:
        print(value)


def connect_github(client: Composio, user_id: str, wait: bool = True) -> Any:
    """Start GitHub OAuth and optionally wait until the account is connected.

    Composio has exposed this operation through slightly different method
    signatures across SDK releases, so support both the keyword and positional
    forms while keeping the rest of the example version-agnostic.
    """
    accounts = getattr(client, "connected_accounts", None)
    initiate = getattr(accounts, "initiate", None)
    if initiate is None:
        raise RuntimeError(
            "This Composio SDK does not expose connected_accounts.initiate. "
            "Upgrade with `pip install --upgrade composio` and retry."
        )

    try:
        request = initiate(user_id=user_id, toolkit="github")
    except TypeError:
        request = initiate(user_id, "github")

    redirect_url = getattr(request, "redirect_url", None)
    if redirect_url:
        print(f"Open this URL to connect GitHub:\n{redirect_url}")

    if wait:
        wait_for_connection = getattr(request, "wait_for_connection", None)
        if callable(wait_for_connection):
            print_result(wait_for_connection())
        else:
            print("Finish the browser authorization, then run `python app.py repo`.")
    return request


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
        "Run `python app.py tools` and use the slug returned by Composio. "
        "If the account is not connected, run `python app.py connect` first."
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
        "action", choices=["connect", "tools", "repo", "issue"], nargs="?", default="repo"
    )
    parser.add_argument("--title", help="Issue title (required for issue action)")
    parser.add_argument("--body", default="Created with Composio.")
    parser.add_argument(
        "--no-wait", action="store_true", help="Print the OAuth URL without waiting"
    )
    args = parser.parse_args()

    user_id = os.getenv("COMPOSIO_USER_ID", "user-123")
    owner = os.getenv("GITHUB_OWNER", "innocentaluma11-rgb")
    repo = os.getenv("GITHUB_REPO", "TABERBNACLEFX-")
    client = get_client()

    if args.action == "connect":
        connect_github(client, user_id, wait=not args.no_wait)
    elif args.action == "tools":
        print_result(list_github_tools(client, user_id))
    elif args.action == "repo":
        print_result(get_repo_metadata(client, user_id, owner, repo))
    else:
        if not args.title:
            parser.error("--title is required when action is 'issue'")
        print_result(create_issue(client, user_id, owner, repo, args.title, args.body))


if __name__ == "__main__":
    main()
