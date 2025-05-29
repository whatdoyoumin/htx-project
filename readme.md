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

## Setup Instructions to run locally

### 1. Clone the Repository

```
git clone https://github.com/whatdoyoumin/htx-project.git
cd htx-project
```

### 2. Assumptions

Make sure both Docker and the Compose plugin are installed.

```
docker -v
docker compose version
```

This instructions assume that Docker Desktop, FFMPEG and Python are installed in the user's environment

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

Open Docker Desktop
```
docker compose up -d --build
```

Optional - set up virtual environment

```
python -m venv venv
source ./venv/Scripts/activate

```

Install required libraries

```
pip install -r requirements.txt

```

### 2. Transcribe Dataset

Run the ASR microservice

In another terminal ,navigate to the htx-project folder.

( if having ffmpeg issues, install ffmpeg to path and run from command prompt instead of bash)

```
source ./venv/Scripts/activate # if using virtual environment
cd asr
python cv-decode.py

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)

Ensure your ASR microservice is running at: http://localhost:8001/asr

if using SEED laptop , please disable cloudflare. this will output the transcribed file under the common_voice.


I have already included the transcribed file in common voice folder for convenience, so you may skip this step.


### 3. To build the Docker Images and run all the containers
```
docker compose up -d --build
```

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

May run this command to create index before running docker compose, if want to manage 1 less container.

```
python elastic-backend/cv-index.py
```


## Deployment Architecture

The application was split into four different EC2 instances, with Search UI, ASR API, and Elasticsearch nodes split into different instances. This ensures high availability of the application. To reduce complexity and deployment time, a single docker-compose.yml is reused across 3 EC2 instances. Each machine only runs the services it needs via docker compose up service-name. 

This approach simplifies deployment by maintaining a single configuration file, optimizes resource usage by running only necessary services per instance, improves fault isolation to minimize downtime, and enables independent scaling and easier debugging of each component.

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

- http://ec2-54-255-152-4.ap-southeast-1.compute.amazonaws.com:3000/

## License

By 
provided by HTX for technical assessment purposes.