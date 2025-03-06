import json
import requests
import ollama

# Load API details from JSON file
def load_api_details(filename="apis.json"):
    with open(filename, "r") as file:
        return json.load(file)

# Find the best matching API using Ollama LLM
def find_matching_api(user_request, api_data):
    prompt = f"""
    You are an API assistant. You have access to the following APIs:
    
    {json.dumps(api_data, indent=2)}

    Based on the user request, find the most relevant API and return its details **ONLY as JSON**.
    If no API matches, return: {{"error": "No matching API found"}}
    
    User request: "{user_request}"
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])

    try:
        # Attempt to parse response as JSON
        response_json = json.loads(response["message"]["content"])
        
        if "error" in response_json:
            print("❌ No matching API found. Try rephrasing your request.")
            return None
        
        return response_json  # Return matched API details

    except json.JSONDecodeError:
        print("\n❌ Error: Could not parse LLM response. Showing raw response for debugging:\n")
        print(response["message"]["content"])  # Show raw response for debugging
        return None

# Get required parameters from user
def get_missing_params(api):
    required_params = api["parameters"]
    params = {}

    for param in required_params:
        value = input(f"Enter value for {param}: ")
        params[param] = value

    return params

# Make the API call
def call_api(server_url, api, params):
    url = f"{server_url}{api['endpoint']}"  # Append endpoint to base URL
    method = api["method"].upper()

    try:
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, json=params)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Main function
def main():
    print("Welcome to the AI Assistant!")
    server_url = "http://localhost:8909"

    api_data = load_api_details()

    while True:
        user_request = input("\nWhat would you like to do? (or type 'exit' to quit): ").strip()

        if user_request.lower() in ["exit", "quit"]:
            print("Goodbye! Have a great day. 👋")
            break  # Exit the loop

        matched_api = find_matching_api(user_request, api_data)

        if not matched_api:
            continue  # Skip and ask the user again

        print(f"\n✅ Selected API: {matched_api}")

        # Get missing parameters
        params = get_missing_params(matched_api)

        # Call the API
        response = call_api(server_url, matched_api, params)

        print("\n📌 API Response:", response)

if __name__ == "__main__":
    main()
