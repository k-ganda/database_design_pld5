import requests
import json

# Define the API endpoint and any required parameters
api_url = 'http://localhost:8000/users'  


# Send a GET request to the API
response = requests.get(api_url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON data from the response
    data = response.json()  # Converts the response JSON to a Python dictionary or list

    # Save the data or use it for further processing
    # Print the fetched data
    print("Fetched Data:", json.dumps(data, indent=4))

    with open('fetched_data.json', 'w') as f:
        json.dump(data, f, indent=4)  
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
