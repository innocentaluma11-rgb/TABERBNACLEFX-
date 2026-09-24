from __future__ import annotations

import argparse
import json
import os
from typing import Any

from composio import Composio
from dotenv import load_dotenv

load_dotenv()

PLATFORMS = ("instagram", "tiktok", "youtube")


def get_client() -> Composio:
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError("Set COMPOSIO_API_KEY in .env before running this command.")
    return Composio(api_key=api_key)


def get_user_id() -> str:
    return os.getenv("COMPOSIO_USER_ID", "user-123")


def toolkit_name(platform: str) -> str:
    return os.getenv(f"COMPOSIO_{platform.upper()}_TOOLKIT", platform).lower()


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, default=str))


def connect(platform: str, wait: bool = True) -> Any:
    composio = get_client()
    accounts = getattr(composio, "connected_accounts", None)
    initiate = getattr(accounts, "initiate", None)
    if initiate is None:
        raise RuntimeError("Upgrade the Composio SDK: python -m pip install --upgrade composio")

    try:
        request = initiate(user_id=get_user_id(), toolkit=toolkit_name(platform))
    except TypeError:
        request = initiate(get_user_id(), toolkit_name(platform))

    redirect_url = getattr(request, "redirect_url", None)
    if redirect_url:
        print(f"Authorize {platform} here:\n{redirect_url}")

    waiter = getattr(request, "wait_for_connection", None)
    if wait and callable(waiter):
        print_json(waiter())
    return request


def discover(platform: str) -> Any:
    return get_client().tools.get(get_user_id(), toolkits=[toolkit_name(platform)])


def publish(platform: str, text: str, media_url: str | None = None, confirm: bool = False) -> Any:
    if not confirm:
        raise RuntimeError("Publishing is blocked unless --confirm is supplied.")

    slug = os.getenv(f"COMPOSIO_{platform.upper()}_PUBLISH_TOOL", "")
    if not slug:
        raise RuntimeError(
            f"Set COMPOSIO_{platform.upper()}_PUBLISH_TOOL after running `python social_workflow.py discover --platform {platform}`."
        )

    arguments: dict[str, Any] = {"text": text, "caption": text}
    if media_url:
        arguments.update({"media_url": media_url, "video_url": media_url})
    return get_client().tools.execute(slug, arguments=arguments, user_id=get_user_id())


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
        print_json(discover(args.platform))
    else:
        if not args.text:
            parser.error("--text is required for publish")
        print_json(publish(args.platform, args.text, args.media_url, confirm=args.confirm))


if __name__ == "__main__":
    main()
