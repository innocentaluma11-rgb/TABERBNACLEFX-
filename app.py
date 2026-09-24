import os
from typing import Any

from dotenv import load_dotenv

from composio import Composio

load_dotenv()


def get_client() -> Composio:
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key:
        raise RuntimeError(
            "COMPOSIO_API_KEY is missing. Add it to your environment or .env file."
        )
    return Composio(api_key=api_key)


def list_github_tools(user_id: str) -> Any:
    client = get_client()
    return client.tools.get(user_id, toolkits=["github"])


def get_repo_metadata(user_id: str, owner: str, repo: str) -> Any:
    client = get_client()
    candidates = ["GITHUB_GET_REPO", "GITHUB_GET_REPOS"]
    last_error: Exception | None = None

    for slug in candidates:
        try:
            return client.tools.execute(
                slug,
                arguments={"owner": owner, "repo": repo},
                user_id=user_id,
            )
        except Exception as exc:  # pragma: no cover - tool slug availability varies by SDK version
            last_error = exc

    if last_error is not None:
        raise last_error

    raise RuntimeError("No GitHub repo tool was available from Composio.")


def main() -> None:
    user_id = os.getenv("COMPOSIO_USER_ID", "user-123")
    owner = os.getenv("GITHUB_OWNER", "innocentaluma11-rgb")
    repo = os.getenv("GITHUB_REPO", "TABERBNACLEFX-")

    print(f"Listing GitHub tools for user ID: {user_id}")
    tools = list_github_tools(user_id)
    print(tools)

    print(f"\nMaking a real GitHub tool call for {owner}/{repo}")
    result = get_repo_metadata(user_id, owner, repo)
    print(result)


if __name__ == "__main__":
    main()
