import os
import json
import urllib.request
import urllib.error

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable is not set.")
        return

    # Use a basic URL and model that we know has hit 429s
    url = f"https://generativelanguage.googleapis.com/v1alpha/models/gemini-2.5-pro:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Minimal payload for "hello"
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "hello"}]
            }
        ]
    }
    
    req = urllib.request.Request(
        url=url,
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
        method="POST"
    )
    
    try:
        print("Sending request to Gemini API...")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            print("\nSUCCESS! Response:")
            print(json.dumps(result, indent=2))
            
    except urllib.error.HTTPError as e:
        print(f"\nHTTP Error {e.code}: {e.reason}")
        print("Response Body:")
        body = e.read().decode("utf-8")
        try:
            print(json.dumps(json.loads(body), indent=2))
        except:
            print(body)
            
        print("\nHeaders:")
        for k, v in e.headers.items():
            print(f"{k}: {v}")
            
    except Exception as e:
        print(f"Other Error: {e}")

if __name__ == "__main__":
    main()
