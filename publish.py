"""
Publishes the image prepared by generate.py to Instagram (and optionally the Facebook Page).
Runs inside GitHub Actions. Reads secrets from environment variables:

  IG_USER_ID         Instagram business account ID
  PAGE_ACCESS_TOKEN  Facebook Page access token (never-expiring type)
  FB_PAGE_ID         Facebook Page ID (only needed if posting to Facebook too)

Never prints tokens, so it is safe in a public repository.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def call(method, url, **params):
    r = requests.request(method, url, data=params if method == "POST" else None,
                         params=params if method == "GET" else None, timeout=60)
    try:
        data = r.json()
    except ValueError:
        fail(f"Unexpected response ({r.status_code}) from Meta.")
    if "error" in data:
        e = data["error"]
        fail(f"Meta API said: {e.get('message')} (code {e.get('code')})")
    return data


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    meta = json.loads((ROOT / "output" / "next.json").read_text(encoding="utf-8"))
    if meta.get("skip"):
        print("Nothing to publish today.")
        return

    ig_user = os.environ.get("IG_USER_ID")
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    if not ig_user or not token:
        fail("IG_USER_ID or PAGE_ACCESS_TOKEN secret is missing. See SETUP.md step 5.")

    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    image_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{meta['image']}"
    base = f"https://graph.facebook.com/{cfg['graph_api_version']}"
    caption = meta["caption"]

    # Instagram: step 1, create the media container
    container = call("POST", f"{base}/{ig_user}/media",
                     image_url=image_url, caption=caption, access_token=token)
    cid = container["id"]

    # Step 2, wait until Instagram has processed the image
    for _ in range(12):
        status = call("GET", f"{base}/{cid}", fields="status_code", access_token=token)
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") == "ERROR":
            fail("Instagram could not process the image.")
        time.sleep(5)

    # Step 3, publish
    call("POST", f"{base}/{ig_user}/media_publish", creation_id=cid, access_token=token)
    print("Posted to Instagram.")

    # Optional: Facebook Page
    page_id = os.environ.get("FB_PAGE_ID")
    if cfg.get("post_to_facebook_page_too") and page_id:
        call("POST", f"{base}/{page_id}/photos", url=image_url, caption=caption,
             access_token=token)
        print("Posted to Facebook Page.")

    # Move to the next post only after success
    state_path = ROOT / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["next_index"] = meta["index"] + 1
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
