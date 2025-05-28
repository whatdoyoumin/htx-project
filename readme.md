# HTX ASR Project

This repository contains the solution to the HTX Technical Test, focusing on:

- An Automatic Speech Recognition (ASR) microservice using `wav2vec2-large-960h`
- A 2-node Elasticsearch backend for indexing transcripts
- A Search UI for querying and filtering indexed audio metadata
- Fully containerized deployment using Docker Compose

## Project Structure

```
htx-project/
├── docker-compose.yml
├── requirements.txt
├── asr/
│   ├── Dockerfile
│   ├── asr_api.py
│   └── cv-decode.py
├── elastic-backend/
│   ├── Dockerfile
│   └── cv-index.py
├── search-ui/
│   ├── Dockerfile
│   ├── search_app.py
│   └── templates/
│       └── search.html
├── common_voice/
│   └── cv-valid-dev_transcribed.csv
├── deployment-design/
│   └── design.pdf
└── essay.pdf
```

## Features

- ASR API for MP3 file transcription
- Elasticsearch cluster (2-node) for indexing
- Search UI to filter by `generated_text`, `age`, `gender`, `accent`, `duration`
- All services Dockerized and deployable locally or on AWS EC2
- Public web-accessible deployment using `docker-compose`

## Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/whatdoyoumin/htx-project.git
cd htx-project
```

### 2. Install Docker & Docker Compose

Make sure both Docker and the Compose plugin are installed.

```
docker -v
docker compose version
```

### 3. Download Common Voice Dataset

Place the audio and CSV into the `common_voice/` folder:

```
mkdir common_voice
# Download and unzip:
# https://www.dropbox.com/scl/fi/i9yvfqpf7p8uye5o8k1sj/common_voice.zip?rlkey=lz3dtjuhekc3xw4jnoeoqy5yu&dl=0
unzip common_voice.zip -d common_voice
```

## How to Run (Locally via Docker Compose)

### 1. Start All Services

```
docker compose up -d --build
```

### 2. Transcribe Dataset

```
python asr/cv-decode.py
```

### 3. Index Into Elasticsearch

```
python elastic-backend/cv-index.py
```

### 4. To run all the containers
```
$ docker compose up -d
```
docker compose up -d --build

## Endpoints

| Component       | URL                         | Notes                             |
|----------------|------------------------------|------------------------------------|
| ASR Ping        | http://localhost:8001/ping  | Should return `"pong"`             |
| ASR Inference   | http://localhost:8001/asr   | POST with mp3 file                 |
| Elasticsearch   | http://localhost:9200       | Headless API for indexing/search   |
| Search UI       | http://localhost:3000       | Web search interface               |


![alt text](images/ping.png)

![alt text](images/sampleasr.png)

## Example Curl Command

```
curl -X POST      -F "file=@/path/to/sample.mp3"      http://localhost:8001/asr
```

## Deployment Architecture

“To reduce complexity and deployment time, a single `docker-compose.yml` is reused across 3 EC2 instances. Each machine only runs the services it needs via `docker compose up service-name`.”

| EC2 Instance | Role                        | Services                |
|--------------|-----------------------------|-------------------------|
| EC2-A        | Elasticsearch Node 1        | elasticsearch1          |
| EC2-B        | Elasticsearch Node 2        | elasticsearch2          |
| EC2-C        | ASR API + Indexer           | asr, cv-index           |
| EC2-D        | Web Frontend (Search UI)    | search-ui               |

See `deployment-design/design.pdf` for the full AWS diagram.

## Local Testing Tips

- Use `docker compose logs -f` to check logs
- ASR API takes some time to warm up on first boot
- Ensure `cv-valid-dev_transcribed.csv` is generated before indexing

## Public Deployment (Demo)

- http://ec2-54-255-152-4.ap-southeast-1.compute.amazonaws.com

## License

provided by HTX for technical assessment purposes.