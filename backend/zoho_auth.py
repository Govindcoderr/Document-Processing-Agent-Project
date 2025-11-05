import requests

def get_zoho_access_token():
    try:
        # --- Zoho Credentials (for testing only — not for production) ---
        ZOHO_CLIENT_ID="1000.Q2YK2OYSFT2C1L7LYS481VMDRJFR0J"
        ZOHO_CLIENT_SECRET="13a0e6857af71ace8682325dfa0b36b8492cd2a3a4"
        ZOHO_REFRESH_TOKEN="1000.f016c31dd97dbb865725deb5ef124f6b.70ec271982faba306c0bc7ef3f5f3814"
        ZOHO_ORG_ID="60057165181"

        # Validate required values
        if not all([ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN]):
            raise ValueError("Missing one or more Zoho credentials.")

        # --- API URL and parameters ---
        token_url = "https://accounts.zoho.in/oauth/v2/token"
        params = {
            "refresh_token": ZOHO_REFRESH_TOKEN,
            "client_id": ZOHO_CLIENT_ID,
            "client_secret": ZOHO_CLIENT_SECRET,
            "grant_type": "refresh_token"
        }

        # --- Send POST request ---
        response = requests.post(token_url, params=params, timeout=10)
        response.raise_for_status()  # Raise error for bad HTTP status codes

        # --- Parse response ---
        data = response.json()
        access_token = data.get("access_token")

        if not access_token:
            raise ValueError(f" Failed to fetch access token. Full response: {data}")

        # ---  Print and return token ---
        print(f"\nAccess Token: {access_token}")
        print(f"🔹 Status Code: {response.status_code}\n")

        return access_token

    except requests.exceptions.Timeout:
        print(" Error: Request to Zoho timed out.")
    except requests.exceptions.ConnectionError:
        print(" Error: Network connection failed.")
    except requests.exceptions.HTTPError as e:
        print(f" HTTP Error: {e.response.status_code} - {e.response.text}")
    except ValueError as e:
        print(f"{e}")
    except Exception as e:
        print(f" Unexpected Error: {e}")
    finally:
        print("Execution completed.\n")

    return None


#  Run the function directly 

# if __name__ == "__main__":
#     token = get_zoho_access_token()
#     print(f"Result from function: {token}")
