from fastapi import FastAPI
import json
import requests

app = FastAPI()

# In-memory file storage (for demo purposes)
file_storage = {}

@app.post("/create-file")
async def create_file(filename: str, content: str):
    """Creates a file with given content."""
    file_storage[filename] = content  # Simulated file storage
    return {"status": "success", "message": f"File '{filename}' created."}

@app.get("/weather")
async def get_weather(city: str):
    """Fetches weather for a given city."""
    return {"city": city, "temperature": "22°C", "condition": "Sunny"}

@app.get("/generate-api-json")
def generate_api_json():
    """Fetches OpenAPI schema and generates 'apis.json' dynamically."""
    openapi_url = "http://localhost:8909/openapi.json"
    
    try:
        response = requests.get(openapi_url)
        openapi_data = response.json()

        # Extract API details
        apis = []
        for path, methods in openapi_data["paths"].items():
            for method, details in methods.items():
                apis.append({
                    "name": details.get("summary", "No name"),
                    "description": details.get("description", ""),
                    "endpoint": path,
                    "method": method.upper(),
                    "parameters": [
                        param["name"] for param in details.get("parameters", [])
                    ],
                })

        # Save to JSON file
        with open("apis.json", "w") as file:
            json.dump(apis, file, indent=4)

        return {"status": "success", "message": "apis.json generated!", "apis": apis}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8909)
