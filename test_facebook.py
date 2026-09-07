import requests

TOKEN = "EAA7jTJNwUroBSQ1aeFWIb9wG9MgHn8qC4vC7iuf3aDrwrm6wSNvJrikJnusgJDgBnEzl6ZAkTIv58QcuBvrAvVeaKMJoRrxNV7DeKtEngZABAypu8YbnMXxVxAnbOz8jcLHzTZAktUub8tuSrpbpAw3XPG5hQy3BhWOf3hGqrYNbnZCe2MusCUUIxvQa9DqG80vNJ9RXsxKc3cA3ps9jY4N5e4LAhewxBOxht6LTP2UMh6ZB5ijA0iyIZD"
PAGE_ID = "1183775391493528"

r = requests.get(
    f"https://graph.facebook.com/v23.0/{PAGE_ID}",
    params={
        "fields": "id,name",
        "access_token": TOKEN
    }
)

print(r.json())