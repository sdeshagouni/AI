import json
import requests
import ollama

# Load API details from JSON file
def load_api_details(filename="apis.json"):
    with open(filename, "r") as file:
        return json.load(file)

# Use LLM to extract parameters from user request
def extract_params_with_llm(user_request, api):
    print(f"{type(api)}")
    prompt = f"""
    You are a smart AI that extracts API parameters from user requests.

    API Name: {api['name']}
    API Description: {api['description']}
    Required Parameters: {json.dumps(api['parameters'], indent=2)}

    Extract as many parameters as possible from this user request:
    "{user_request}"

    Return ONLY a valid JSON object like this:
    {{"param1": "value1", "param2": "value2"}}
    If no parameters are found, return an empty JSON: {{}}
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])

    try:
        return json.loads(response["message"]["content"])
    except json.JSONDecodeError:
        print("❌ LLM failed to extract parameters. Falling back to manual input.")
        return {}

# Find the best matching API using LLM
def find_matching_api(user_request, api_data):
    prompt = f"""
    You are an API assistant. You have access to the following APIs:
    
    {json.dumps(api_data, indent=2)}

    Based on the user request, find the most relevant API and return all details **ONLY as JSON**.
    If no API matches, return: {{"error": "No matching API found"}}
    
    User request: "{user_request}"
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])

    try:
        response_json = json.loads(response["message"]["content"])
        
        if "error" in response_json:
            print("❌ No matching API found. Try rephrasing your request.")
            return None
        
        return response_json

    except json.JSONDecodeError:
        print("\n❌ Error: Could not parse LLM response. Showing raw response for debugging:\n")
        print(response["message"]["content"])  
        return None

# Get missing parameters from user
def get_missing_params(api, extracted_params):
    required_params = api["parameters"]
    params = extracted_params.copy()

    for param in required_params:
        if param not in params:
            value = input(f"Enter value for {param}: ")
            params[param] = value

    return params

# Make the API call
def call_api(server_url, api, params):
    url = f"{server_url}{api['endpoint']}"  
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
    print(f"{api_data}")

    while True:
        user_request = input("\nWhat would you like to do? (or type 'exit' to quit): ").strip()

        if user_request.lower() in ["exit", "quit"]:
            print("Goodbye! Have a great day. 👋")
            break  

        matched_api = find_matching_api(user_request, api_data)

        if not matched_api:
            continue  

        print(f"\n✅ Selected API: {matched_api}")

        # Use LLM to extract parameters
        extracted_params = extract_params_with_llm(user_request, matched_api)
        if extracted_params:
            print(f"🔹 Extracted Parameters: {extracted_params}")

        # Get remaining missing parameters
        params = get_missing_params(matched_api, extracted_params)

        # Call the API
        response = call_api(server_url, matched_api, params)

        print("\n📌 API Response:", response)

if __name__ == "__main__":
    main()
