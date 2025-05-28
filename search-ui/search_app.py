# search-ui/search_app.py
from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
import os

app = Flask(__name__)


ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch1')
ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT', '9200')


es = Elasticsearch(
    f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}",
    headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=8"}
)


@app.route('/')
def index():
    return render_template('search.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    age_filter = request.args.get('age', '')
    gender_filter = request.args.get('gender', '')
    accent_filter = request.args.get('accent', '')
    
    # Build Elasticsearch query
    body = {
        "query": {
            "bool": {
                "must": []
            }
        },
        "aggs": {
            "ages": {"terms": {"field": "age.keyword"}},
            "genders": {"terms": {"field": "gender.keyword"}},
            "accents": {"terms": {"field": "accent.keyword"}}
        }
    }
    
    # Add text search if query provided
    if query:
        body["query"]["bool"]["must"].append({
            "multi_match": {
                "query": query,
                "fields": ["generated_text", "text"]
            }
        })
    else:
        body["query"] = {"match_all": {}}
    
    # Add filters
    filters = []
    if age_filter:
        filters.append({"term": {"age.keyword": age_filter}})
    if gender_filter:
        filters.append({"term": {"gender.keyword": gender_filter}})
    if accent_filter:
        filters.append({"term": {"accent.keyword": accent_filter}})
    
    if filters:
        body["query"]["bool"]["filter"] = filters
    
    try:
        response = es.search(
            index=os.getenv('ELASTICSEARCH_INDEX', 'cv-transcriptions'),
            body=body,
            size=20
        )
        return jsonify({
            'hits': response['hits']['hits'],
            'total': response['hits']['total']['value'],
            'aggregations': response.get('aggregations', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)