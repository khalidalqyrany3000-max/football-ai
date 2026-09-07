from dotenv import load_dotenv
load_dotenv()

import os
import base64
import requests


# ============================================================
# CONFIG
# ============================================================

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY")
SYSTEM_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")

GRAPH_API = "https://graph.facebook.com/v23.0"


# ============================================================
# GET PAGE TOKEN
# ============================================================

def get_page_token():

    response = requests.get(
        f"{GRAPH_API}/{FACEBOOK_PAGE_ID}",
        params={
            "fields": "access_token",
            "access_token": SYSTEM_TOKEN
        },
        timeout=30
    )

    token = response.json().get("access_token")

    if not token:
        raise RuntimeError(
            f"Failed to get Page Token: {response.json()}"
        )

    return token


# ============================================================
# GET INSTAGRAM USER ID
# ============================================================

def get_instagram_user_id(page_token):

    response = requests.get(
        f"{GRAPH_API}/{FACEBOOK_PAGE_ID}",
        params={
            "fields": "instagram_business_account",
            "access_token": page_token
        },
        timeout=30
    )

    ig_id = response.json().get(
        "instagram_business_account", {}
    ).get("id")

    if not ig_id:
        raise RuntimeError(
            f"Failed to get Instagram User ID: {response.json()}"
        )

    return ig_id


# ============================================================
# UPLOAD IMAGE TO GITHUB
# ============================================================

def upload_image_to_github(image_path):

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    filename = os.path.basename(image_path)
    github_path = f"published_images/{filename}"

    check = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/{github_path}",
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        },
        timeout=30
    )

    sha = check.json().get("sha") if check.status_code == 200 else None

    payload = {
        "message": f"Add image: {filename}",
        "content": image_data
    }

    if sha:
        payload["sha"] = sha

    response = requests.put(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/{github_path}",
        json=payload,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        },
        timeout=60
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"GitHub upload failed: {response.status_code} - {response.json()}"
        )

    image_url = response.json()["content"]["download_url"].split("?")[0]

    return image_url


# ============================================================
# PUBLISH TO FACEBOOK
# ============================================================

def publish_to_facebook(page_token, image_url, caption):

    response = requests.post(
        f"{GRAPH_API}/{FACEBOOK_PAGE_ID}/photos",
        data={
            "url": image_url,
            "caption": caption,
            "access_token": page_token
        },
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Facebook publish failed: {response.status_code} - {response.json()}"
        )

    result = response.json()

    print("✅ Facebook published:", result.get("post_id"))

    return result


# ============================================================
# PUBLISH TO INSTAGRAM
# ============================================================

def publish_to_instagram(page_token, ig_user_id, image_url, caption):

    media_response = requests.post(
        f"{GRAPH_API}/{ig_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": page_token
        },
        timeout=30
    )

    if media_response.status_code != 200:
        raise RuntimeError(
            f"Instagram media creation failed: {media_response.status_code} - {media_response.json()}"
        )

    creation_id = media_response.json().get("id")

    if not creation_id:
        raise RuntimeError(
            f"Instagram did not return creation ID: {media_response.json()}"
        )

    publish_response = requests.post(
        f"{GRAPH_API}/{ig_user_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": page_token
        },
        timeout=30
    )

    if publish_response.status_code != 200:
        raise RuntimeError(
            f"Instagram publish failed: {publish_response.status_code} - {publish_response.json()}"
        )

    result = publish_response.json()

    print("✅ Instagram published:", result.get("id"))

    return result


# ============================================================
# PUBLISH TO BOTH
# ============================================================

def publish(image_path, caption):

    results = {
        "facebook": None,
        "instagram": None,
        "image_url": None
    }

    # ----------------------------------------------------
    # GET TOKENS
    # ----------------------------------------------------

    print("🔑 Getting Page Token...")

    try:
        page_token = get_page_token()
    except Exception as e:
        print(f"❌ Page Token error: {e}")
        return results

    print("🔑 Getting Instagram User ID...")

    try:
        ig_user_id = get_instagram_user_id(page_token)
    except Exception as e:
        print(f"❌ Instagram ID error: {e}")
        return results

    # ----------------------------------------------------
    # UPLOAD IMAGE
    # ----------------------------------------------------

    print("📤 Uploading image to GitHub...")

    try:
        image_url = upload_image_to_github(image_path)
        results["image_url"] = image_url
        print("✅ Image URL:", image_url)
    except Exception as e:
        print(f"❌ GitHub upload error: {e}")
        return results

    # ----------------------------------------------------
    # FACEBOOK
    # ----------------------------------------------------

    print("📘 Publishing to Facebook...")

    try:
        results["facebook"] = publish_to_facebook(
            page_token=page_token,
            image_url=image_url,
            caption=caption
        )
    except Exception as e:
        print(f"❌ Facebook error: {e}")

    # ----------------------------------------------------
    # INSTAGRAM
    # ----------------------------------------------------

    print("📸 Publishing to Instagram...")

    try:
        results["instagram"] = publish_to_instagram(
            page_token=page_token,
            ig_user_id=ig_user_id,
            image_url=image_url,
            caption=caption
        )
    except Exception as e:
        print(f"❌ Instagram error: {e}")

    return results