import requests
import time

ELASTIC_HOST = "http://127.0.0.1:9200" # Ensure you're using 127.0.0.1 here

print(f"Attempting to connect to Elasticsearch at {ELASTIC_HOST}...")
try:
    response = requests.get(ELASTIC_HOST, timeout=5) # 5-second timeout
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    print("Successfully connected to Elasticsearch!")
    print("Response:", response.json())
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: Could not connect to Elasticsearch. Error: {e}")
    print("Please ensure Elasticsearch is running and accessible at this address.")
except requests.exceptions.Timeout as e:
    print(f"Timeout error: Elasticsearch did not respond in time. Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"An unexpected request error occurred: {e}")