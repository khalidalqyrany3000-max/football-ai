import os
import base64
import requests


# ============================================================
# META CONFIG
# ============================================================

META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID")

GRAPH_API_VERSION = "v23.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


# ============================================================
# GITHUB IMAGE HOST CONFIG
# ============================================================

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
GITHUB_BRANCH = os.environ.get(
    "GITHUB_BRANCH",
    "main"
)

GITHUB_IMAGE_DIRECTORY = "generated_images"


# ============================================================
# CONFIG CHECK
# ============================================================

def check_meta_config():

    missing = []

    if not META_ACCESS_TOKEN:
        missing.append(
            "META_ACCESS_TOKEN"
        )

    if not FACEBOOK_PAGE_ID:
        missing.append(
            "FACEBOOK_PAGE_ID"
        )

    if not INSTAGRAM_ACCOUNT_ID:
        missing.append(
            "INSTAGRAM_ACCOUNT_ID"
        )

    if missing:

        raise ValueError(
            "Missing Meta environment variables: "
            + ", ".join(missing)
        )


# ============================================================
# GITHUB CONFIG CHECK
# ============================================================

def check_github_config():

    missing = []

    if not GITHUB_TOKEN:
        missing.append(
            "GITHUB_TOKEN"
        )

    if not GITHUB_REPOSITORY:
        missing.append(
            "GITHUB_REPOSITORY"
        )

    if missing:

        raise ValueError(
            "Missing GitHub environment variables: "
            + ", ".join(missing)
        )


# ============================================================
# FACEBOOK PAGE PHOTO
# ============================================================

def publish_to_facebook(
    message,
    image_path
):

    check_meta_config()

    if not image_path:

        raise ValueError(
            "Facebook requires an image path."
        )

    if not os.path.isfile(
        image_path
    ):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    endpoint = (
        f"{GRAPH_API_URL}/"
        f"{FACEBOOK_PAGE_ID}/photos"
    )

    try:

        with open(
            image_path,
            "rb"
        ) as image_file:

            files = {
                "source": (
                    os.path.basename(
                        image_path
                    ),
                    image_file,
                    "image/jpeg"
                )
            }

            data = {
                "caption": message,
                "access_token": META_ACCESS_TOKEN
            }

            response = requests.post(
                endpoint,
                data=data,
                files=files,
                timeout=60
            )

    except Exception as error:

        raise RuntimeError(
            f"Facebook request failed: {error}"
        ) from error

    if not response.ok:

        raise RuntimeError(
            "Facebook publishing failed: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    result = response.json()

    print(
        "✅ Facebook post published."
    )

    return result


# ============================================================
# GITHUB IMAGE UPLOAD
# ============================================================

def upload_image_to_github(
    image_path
):

    check_github_config()

    if not os.path.isfile(
        image_path
    ):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    filename = os.path.basename(
        image_path
    )

    github_path = (
        f"{GITHUB_IMAGE_DIRECTORY}/"
        f"{filename}"
    )

    api_url = (
        "https://api.github.com/repos/"
        f"{GITHUB_REPOSITORY}/contents/"
        f"{github_path}"
    )

    with open(
        image_path,
        "rb"
    ) as image_file:

        encoded_content = base64.b64encode(
            image_file.read()
        ).decode(
            "utf-8"
        )

    headers = {
        "Authorization": (
            f"Bearer {GITHUB_TOKEN}"
        ),
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # --------------------------------------------------------
    # Check if file already exists
    # --------------------------------------------------------

    existing_response = requests.get(
        api_url,
        headers=headers,
        params={
            "ref": GITHUB_BRANCH
        },
        timeout=30
    )

    payload = {
        "message": (
            f"Add generated image: "
            f"{filename}"
        ),
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    if existing_response.ok:

        existing_data = existing_response.json()

        sha = existing_data.get(
            "sha"
        )

        if sha:

            payload["sha"] = sha

    # --------------------------------------------------------
    # Upload
    # --------------------------------------------------------

    response = requests.put(
        api_url,
        headers=headers,
        json=payload,
        timeout=60
    )

    if not response.ok:

        raise RuntimeError(
            "GitHub image upload failed: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    # --------------------------------------------------------
    # Public raw URL
    # --------------------------------------------------------

    raw_url = (
        "https://raw.githubusercontent.com/"
        f"{GITHUB_REPOSITORY}/"
        f"{GITHUB_BRANCH}/"
        f"{github_path}"
    )

    print(
        "✅ Image uploaded to GitHub."
    )

    print(
        "Public image URL:",
        raw_url
    )

    return raw_url


# ============================================================
# INSTAGRAM CREATE MEDIA
# ============================================================

def create_instagram_media(
    image_url,
    caption
):

    check_meta_config()

    if not image_url:

        raise ValueError(
            "Instagram requires a public image URL."
        )

    endpoint = (
        f"{GRAPH_API_URL}/"
        f"{INSTAGRAM_ACCOUNT_ID}/media"
    )

    data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }

    response = requests.post(
        endpoint,
        data=data,
        timeout=60
    )

    if not response.ok:

        raise RuntimeError(
            "Instagram media creation failed: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    result = response.json()

    creation_id = result.get(
        "id"
    )

    if not creation_id:

        raise RuntimeError(
            "Instagram did not return "
            f"a creation ID: {result}"
        )

    print(
        "✅ Instagram media container created."
    )

    return creation_id


# ============================================================
# INSTAGRAM PUBLISH
# ============================================================

def publish_instagram_media(
    creation_id
):

    check_meta_config()

    endpoint = (
        f"{GRAPH_API_URL}/"
        f"{INSTAGRAM_ACCOUNT_ID}/media_publish"
    )

    data = {
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }

    response = requests.post(
        endpoint,
        data=data,
        timeout=60
    )

    if not response.ok:

        raise RuntimeError(
            "Instagram publishing failed: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    result = response.json()

    print(
        "✅ Instagram post published."
    )

    return result


# ============================================================
# INSTAGRAM FULL PUBLISH
# ============================================================

def publish_to_instagram(
    image_url,
    caption
):

    creation_id = create_instagram_media(
        image_url=image_url,
        caption=caption
    )

    return publish_instagram_media(
        creation_id=creation_id
    )


# ============================================================
# PUBLISH TO FACEBOOK + INSTAGRAM
# ============================================================

def publish_to_meta(
    message,
    image_path
):

    results = {
        "facebook": None,
        "instagram": None,
        "image_url": None
    }

    # ========================================================
    # FACEBOOK
    # ========================================================

    try:

        results["facebook"] = publish_to_facebook(
            message=message,
            image_path=image_path
        )

    except Exception as error:

        print(
            "❌ Facebook publishing error:"
        )

        print(
            error
        )

    # ========================================================
    # GITHUB IMAGE
    # ========================================================

    try:

        image_url = upload_image_to_github(
            image_path=image_path
        )

        results["image_url"] = image_url

    except Exception as error:

        print(
            "❌ GitHub image upload error:"
        )

        print(
            error
        )

        return results

    # ========================================================
    # INSTAGRAM
    # ========================================================

    try:

        results["instagram"] = publish_to_instagram(
            image_url=image_url,
            caption=message
        )

    except Exception as error:

        print(
            "❌ Instagram publishing error:"
        )

        print(
            error
        )

    return results