from dotenv import load_dotenv
load_dotenv()

import os
import requests

PAGE_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")

r = requests.get(
    f"https://graph.facebook.com/v23.0/{PAGE_ID}",
    params={
        "fields": "instagram_business_account",
        "access_token": PAGE_TOKEN
    }
)

print(r.json())
