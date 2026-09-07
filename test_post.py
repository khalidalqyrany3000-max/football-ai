import requests

TOKEN = "EAA7jTJNwUroBSRPSLLCagZCoc6DNvnxRXHpzZB0P98mSCukJI6pg0YfZAj2SgjlN0xQ7erdKwSGx9t5ZBz7kNm6YS08ZBKYzEhNwABNbizySWiybetoJT6ir3qjwGwNWDxyqZAx0QRpcvUl7cWDiCSSF5vmKm1OqYhgyJFrkniZC6Tmb0Aj5d5ZBF0LTyjUfxkG7DQZDZD"
PAGE_ID = "1183775391493528"

r = requests.post(
    f"https://graph.facebook.com/v23.0/{PAGE_ID}/feed",
    data={
        "message": "test post - سيتم حذفه",
        "access_token": TOKEN
    }
)

print(r.json())