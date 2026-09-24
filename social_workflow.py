import argparse
import json
import os
from typing import Any

from dotenv import load_dotenv
from composio import Composio

load_dotenv()

PLATFORMS = ("instagram", "tiktok", "youtube")


def client() -> Composio:
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError("Set COMPOSIO_API_KEY in .env before running this command.")
    return Composio(api_key=api_key)


def user_id() -> str:
    return os.getenv("COMPOSIO_USER_ID", "user-123")


def toolkit(platform: str) -> str:
    value = os.getenv(f"COMPOSIO_{platform.upper()}_TOOLKIT", platform)
    return value.lower()


def print_result(value: Any) -> None:
    print(json.dumps(value, indent=2, default=str))


def connect(platform: str, wait: bool = True) -> Any:
    """Start OAuth for a social toolkit; the user must approve in a browser."""
    composio = client()
    accounts = getattr(composio, "connected_accounts", None)
    initiate = getattr(accounts, "initiate", None)
    if initiate is None:
        raise RuntimeError(
            "Upgrade the Composio SDK: python -m pip install --upgrade composio"
        )
    try:
        request = initiate(user_id=user_id(), toolkit=toolkit(platform))
    except TypeError:
        request = initiate(user_id(), toolkit(platform))

    redirect_url = getattr(request, "redirect_url", None)
    if redirect_url:
        print(f"Authorize {platform} here:\n{redirect_url}")
    waiter = getattr(request, "wait_for_connection", None)
    if wait and callable(waiter):
        print_result(waiter())
    return request


def discover(platform: str) -> Any:
    return client().tools.get(user_id(), toolkits=[toolkit(platform)])


def execute(platform: str, text: str, media_url: str | None) -> Any:
    """Execute a configured publish slug. Never publishes unless called explicitly."""
    slug = os.getenv(f"COMPOSIO_{platform.upper()}_PUBLISH_TOOL")
    if not slug:
        raise RuntimeError(
            f"Set COMPOSIO_{platform.upper()}_PUBLISH_TOOL after running "
            f"`python social_workflow.py discover --platform {platform}`."
        )

    arguments: dict[str, Any] = {"text": text, "caption": text}
    if media_url:
        arguments.update({"media_url": media_url, "video_url": media_url})
    return client().tools.execute(slug, arguments=arguments, user_id=user_id())


def main() -> None:
    parser = argparse.ArgumentParser(description="Composio social publishing workflow")
    parser.add_argument("action", choices=("connect", "discover", "publish"))
    parser.add_argument("--platform", choices=PLATFORMS, required=True)
    parser.add_argument("--text", help="Caption, post text, or video description")
    parser.add_argument("--media-url", help="Public image/video URL when required")
    parser.add_argument("--confirm", action="store_true", help="Allow the real publish call")
    parser.add_argument("--no-wait", action="store_true")
    args = parser.parse_args()

    if args.action == "connect":
        connect(args.platform, wait=not args.no_wait)
    elif args.action == "discover":
        print_result(discover(args.platform))
    else:
        if not args.text:
            parser.error("--text is required for publish")
        if not args.confirm:
            parser.error("Publishing is blocked unless --confirm is supplied")
        print_result(execute(args.platform, args.text, args.media_url))


if __name__ == "__main__":
    main()
