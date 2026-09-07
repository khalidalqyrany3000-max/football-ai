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
INSTAGRAM_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")

IMAGE_PATH = "generated_images/Arteta__Alonso_and_Iraola__One_tiny_Basque_club_shaped_Premier_League_s_top_boss.jpg"
POST_TEXT = "Test post from Football AI ⚽ #Football #FootballNews #Soccer"


# ============================================================
# STEP 1 - GET PAGE ACCESS TOKEN
# ============================================================

print()
print("====================================")
print("STEP 1: Getting Page Access Token")
print("====================================")

page_token_response = requests.get(
    f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}",
    params={
        "fields": "access_token",
        "access_token": SYSTEM_TOKEN
    }
)

print("Response:", page_token_response.status_code)

PAGE_TOKEN = page_token_response.json().get("access_token")

if not PAGE_TOKEN:
    print("Failed to get Page Token")
    print(page_token_response.json())
    exit()

print("Page Token obtained successfully")


# ============================================================
# STEP 2 - GET INSTAGRAM USER ID
# ============================================================

print()
print("====================================")
print("STEP 2: Getting Instagram User ID")
print("====================================")

ig_id_response = requests.get(
    f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}",
    params={
        "fields": "instagram_business_account",
        "access_token": PAGE_TOKEN
    }
)

INSTAGRAM_USER_ID = ig_id_response.json().get(
    "instagram_business_account", {}
).get("id")

print("Instagram User ID:", INSTAGRAM_USER_ID)

if not INSTAGRAM_USER_ID:
    print("Failed to get Instagram User ID")
    exit()


# ============================================================
# STEP 3 - UPLOAD IMAGE TO GITHUB
# ============================================================

print()
print("====================================")
print("STEP 3: Uploading image to GitHub")
print("====================================")

with open(IMAGE_PATH, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

filename = os.path.basename(IMAGE_PATH)
github_path = f"published_images/{filename}"

check = requests.get(
    f"https://api.github.com/repos/{GITHUB_REPO}/contents/{github_path}",
    headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
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
    }
)

print("GitHub response:", response.status_code)

if response.status_code not in (200, 201):
    print("GitHub error:", response.json())
    exit()

image_url = response.json()["content"]["download_url"].split("?")[0]
print("Image URL:", image_url)


# ============================================================
# STEP 4 - PUBLISH TO FACEBOOK
# ============================================================

print()
print("====================================")
print("STEP 4: Publishing to Facebook")
print("====================================")

fb_response = requests.post(
    f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}/photos",
    data={
        "url": image_url,
        "caption": POST_TEXT,
        "access_token": PAGE_TOKEN
    }
)

print("Facebook response:", fb_response.status_code)
print(fb_response.json())


# ============================================================
# STEP 5 - PUBLISH TO INSTAGRAM
# ============================================================

print()
print("====================================")
print("STEP 5: Publishing to Instagram")
print("====================================")

ig_media = requests.post(
    f"https://graph.facebook.com/v23.0/{INSTAGRAM_USER_ID}/media",
    data={
        "image_url": image_url,
        "caption": POST_TEXT,
        "access_token": PAGE_TOKEN
    }
)

print("Instagram media response:", ig_media.status_code)
print(ig_media.json())

creation_id = ig_media.json().get("id")

if not creation_id:
    print("Instagram media creation failed")
    exit()

ig_publish = requests.post(
    f"https://graph.facebook.com/v23.0/{INSTAGRAM_USER_ID}/media_publish",
    data={
        "creation_id": creation_id,
        "access_token": PAGE_TOKEN
    }
)

print("Instagram publish response:", ig_publish.status_code)
print(ig_publish.json())
