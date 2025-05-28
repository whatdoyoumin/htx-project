# # elastic-backend/cv-index.py
# import pandas as pd
# import requests
# import json
# import os
# import time


# # Use environment variable for host, fallback to docker-compose default
# ELASTIC_HOST = os.environ.get("ELASTIC_HOST", "http://elasticsearch1:9200")

# #ELASTIC_HOST    = "http://127.0.0.1:9200" removed this trying to do docker-compose properly, this is hardcoded
# INDEX_NAME      = "cv-transcriptions"
# CSV_FILE_PATH   = "../common_voice/cv-valid-dev_transcribed.csv"

# def test_connection():
#     try:
#         resp = requests.get(ELASTIC_HOST, timeout=5)
#         resp.raise_for_status()
#         info = resp.json()
#         print(f"✓ Connected to ES {info['version']['number']} on cluster {info['cluster_name']}")
#         return True
#     except Exception as e:
#         print(f"✗ ES connection failed: {e}")
#         return False

# def create_index_and_mapping():
#     mapping = {
#         "mappings": {
#             "properties": {
#                 "filename":       {"type": "keyword"},
#                 "text":           {"type": "text"},
#                 "up_votes":       {"type": "integer"},
#                 "down_votes":     {"type": "integer"},
#                 "age":            {"type": "keyword"},
#                 "gender":         {"type": "keyword"},
#                 "accent":         {"type": "keyword"},
#                 "duration":       {"type": "float"},
#                 "generated_text": {"type": "text"}
#             }
#         }
#     }

#     url = f"{ELASTIC_HOST}/{INDEX_NAME}"
#     # delete if exists
#     if requests.head(url).status_code == 200:
#         requests.delete(url).raise_for_status()
#         print(f"✓ Deleted existing index `{INDEX_NAME}`")
#     # create fresh index
#     resp = requests.put(url, json=mapping)
#     resp.raise_for_status()
#     print(f"✓ Created index `{INDEX_NAME}`")
#     return True

# def load_and_index_data():
#     if not os.path.exists(CSV_FILE_PATH):
#         print(f"✗ CSV not found at {CSV_FILE_PATH}")
#         return False

#     df = pd.read_csv(CSV_FILE_PATH)
#     df['duration'] = pd.to_numeric(df['duration'], errors='coerce').fillna(0.0)
#     df.fillna("", inplace=True)

#     print(f"✓ Loaded {len(df)} records. Columns: {list(df.columns)}")

#     # Prepare bulk payload
#     bulk_lines = []
#     for idx, row in df.iterrows():
#         doc_id = row['filename']  # or: f"{idx}"
#         action = {"index": {"_index": INDEX_NAME, "_id": doc_id}}
#         source = {
#             "filename":       row['filename'],
#             "text":           row['text'],
#             "up_votes":       int(row['up_votes']),
#             "down_votes":     int(row['down_votes']),
#             "age":            row['age'],
#             "gender":         row['gender'],
#             "accent":         row['accent'],
#             "duration":       float(row['duration']),
#             "generated_text": row['generated_text']
#         }
#         bulk_lines.append(json.dumps(action))
#         bulk_lines.append(json.dumps(source))

#     bulk_body = "\n".join(bulk_lines) + "\n"
#     resp = requests.post(f"{ELASTIC_HOST}/_bulk", 
#                          headers={"Content-Type": "application/x-ndjson"},
#                          data=bulk_body)
#     resp.raise_for_status()
#     result = resp.json()

#     errors = [item for item in result['items'] if item['index'].get('error')]
#     success = len(result['items']) - len(errors)
#     print(f"✓ Indexed {success} docs with {len(errors)} errors")
#     if errors:
#         print("First few errors:", errors[:2])
#     return True

# def verify_index():
#     resp = requests.get(f"{ELASTIC_HOST}/{INDEX_NAME}/_count")
#     resp.raise_for_status()
#     count = resp.json().get('count', 0)
#     print(f"✓ ES index contains {count} docs")
#     return True

# if __name__ == "__main__":
#     print("=== CV Transcriptions → Elasticsearch ===\n")
#     if not test_connection():
#         exit(1)
#     create_index_and_mapping()
#     load_and_index_data()
#     verify_index()
#     print("\n🎉 All done!")


import pandas as pd
import requests
import json
import os
import time

# Resolve host + port separately (Docker DNS-compatible)
ELASTIC_HOSTNAME = os.getenv("ELASTICSEARCH_HOST", "elasticsearch1")
ELASTIC_PORT     = os.getenv("ELASTICSEARCH_PORT", "9200")
ELASTIC_HOST     = f"http://{ELASTIC_HOSTNAME}:{ELASTIC_PORT}"

INDEX_NAME       = "cv-transcriptions"

CSV_FILE_PATH = "common_voice/cv-valid-dev_transcribed.csv"


def test_connection(retries=10, delay=3):
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(ELASTIC_HOST, timeout=5)
            resp.raise_for_status()
            info = resp.json()
            print(f"✓ Connected to ES {info['version']['number']} on cluster {info['cluster_name']}")
            return True
        except Exception as e:
            print(f"⏳ [{attempt}/{retries}] Elasticsearch not ready ({e}) — retrying in {delay}s...")
            time.sleep(delay)
    print("✗ Elasticsearch connection failed after retries.")
    return False

def create_index_and_mapping():
    mapping = {
        "mappings": {
            "properties": {
                "filename":       {"type": "keyword"},
                "text":           {"type": "text"},
                "up_votes":       {"type": "integer"},
                "down_votes":     {"type": "integer"},
                "age":            {"type": "keyword"},
                "gender":         {"type": "keyword"},
                "accent":         {"type": "keyword"},
                "duration":       {"type": "float"},
                "generated_text": {"type": "text"}
            }
        }
    }

    url = f"{ELASTIC_HOST}/{INDEX_NAME}"
    if requests.head(url).status_code == 200:
        requests.delete(url).raise_for_status()
        print(f"✓ Deleted existing index `{INDEX_NAME}`")
    resp = requests.put(url, json=mapping)
    resp.raise_for_status()
    print(f"✓ Created index `{INDEX_NAME}`")
    return True

def load_and_index_data():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"✗ CSV not found at {CSV_FILE_PATH}")
        return False

    df = pd.read_csv(CSV_FILE_PATH)
    df['duration'] = pd.to_numeric(df['duration'], errors='coerce').fillna(0.0)
    df.fillna("", inplace=True)

    print(f"✓ Loaded {len(df)} records. Columns: {list(df.columns)}")

    bulk_lines = []
    for idx, row in df.iterrows():
        doc_id = row['filename']
        action = {"index": {"_index": INDEX_NAME, "_id": doc_id}}
        source = {
            "filename":       row['filename'],
            "text":           row['text'],
            "up_votes":       int(row['up_votes']),
            "down_votes":     int(row['down_votes']),
            "age":            row['age'],
            "gender":         row['gender'],
            "accent":         row['accent'],
            "duration":       float(row['duration']),
            "generated_text": row['generated_text']
        }
        bulk_lines.append(json.dumps(action))
        bulk_lines.append(json.dumps(source))

    bulk_body = "\n".join(bulk_lines) + "\n"
    resp = requests.post(f"{ELASTIC_HOST}/_bulk", 
                         headers={"Content-Type": "application/x-ndjson"},
                         data=bulk_body)
    resp.raise_for_status()
    result = resp.json()

    errors = [item for item in result['items'] if item['index'].get('error')]
    success = len(result['items']) - len(errors)
    print(f"✓ Indexed {success} docs with {len(errors)} errors")
    if errors:
        print("First few errors:", errors[:2])
    return True

def verify_index():
    resp = requests.get(f"{ELASTIC_HOST}/{INDEX_NAME}/_count")
    resp.raise_for_status()
    count = resp.json().get('count', 0)
    print(f"✓ ES index contains {count} docs")
    return True

if __name__ == "__main__":
    print("=== CV Transcriptions → Elasticsearch ===\n")
    if not test_connection():
        exit(1)
    create_index_and_mapping()
    load_and_index_data()
    verify_index()
    print("\n🎉 All done!")
