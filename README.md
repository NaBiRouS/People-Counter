# People Counter

A computer vision application that detects, tracks, and counts people crossing a defined counting line in video footage.

The project combines object detection, multi-object tracking, event-based counting, a FastAPI backend, a Streamlit interface, Docker containerization, CI/CD, and application monitoring with Prometheus and Grafana.

## Features

* Person detection using YOLO through Ultralytics.
* Multi-object tracking with persistent IDs using FastTrack.
* Bidirectional people counting:

  * IN: people crossing in one direction.
  * OUT: people crossing in the opposite direction.
* Background video processing using a job-based architecture.
* Unit tests for core application logic.
* REST API built with FastAPI.
* Interactive web interface built with Streamlit.
* Dockerized application with separate API and UI services.
* Prometheus metrics for application and video-processing monitoring.
* Grafana dashboard for real-time monitoring and visualization.
* Automated CI workflow using GitHub Actions.

## Architecture

The application is organized around a FastAPI backend and a Streamlit frontend.

```text
                    User
                     |
                     v
              Streamlit UI
                     |
                     | HTTP
                     v
               FastAPI API
                     |
                     v
             Job Manager
                     |
                     v
          Video Processing Pipeline
                     |
          +----------+----------+
          |                     |
          v                     v
    YOLO Detection       FastTrack Tracking
          |                     |
          +----------+----------+
                     |
                     v
              Event Detection
                     |
                     v
              IN / OUT Counts
                     |
                     v
             Processed Video


FastAPI
   |
   +---- /metrics ----> Prometheus ----> Grafana
   |
   +---- GitHub Actions ----> CI
```

## Project Structure

```text
People-Counter/
│
├── src/
│   ├── api/
│   │   └── app.py
│   │
│   ├── counting/
│   │   └── counter.py
│   │
│   ├── detection/
│   │   ├── detector.py
│   │   └── results.py
│   │
│   ├── monitoring/
│   │   └── metrics.py
│   │
│   ├── pipeline/
│   │   └── processor.py
│   │
│   ├── services/
│   │   ├── job_manager.py
│   │   └── video_processor.py
│   │
│   ├── ui/
│   │   └── app.py
│   │
│   └── config.py
│
├── tests/
│   └── test_counter.py
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│
├── prometheus/
│   └── prometheus.yml
│
│
├── dockerfile
├── dockerfile.ui
├── docker-compose.yml
├── .dockerignore
├── .env
├── requirements-api.txt
├── requirements-ui.txt
├── requirements-dev.txt
├── .gitignore
└── README.md
```


## Computer Vision Pipeline

The video processing pipeline follows these main steps:

1. Read the input video frame by frame.
2. Detect people using YOLO.
3. Track detected people across frames using FastTrack.
4. Assign persistent IDs to tracked people.
5. Determine when a tracked person crosses the counting line.
6. Determine the crossing direction.
7. Register an `IN` or `OUT` event.
8. Update the corresponding counters.
9. Draw detections, tracking IDs, and counting information on the output video.
10. Save the processed video.

The tracking system allows the application to distinguish between different people across consecutive frames instead of treating every detection as a new person.

## API

The backend is implemented with FastAPI.

Main endpoints include:

```text
GET  /health
POST /process-video
GET  /jobs/{job_id}
GET  /videos/{job_id}
GET  /metrics
```

### Job-Based Processing

Video processing is handled through a job-based architecture.

When a video is submitted:

```text
POST /process-video
        |
        v
     Job ID
        |
        v
Background processing
        |
        v
GET /jobs/{job_id}
        |
        v
completed / failed
```

This prevents the API request from having to wait synchronously for the entire video-processing operation.

## Web Interface

The frontend is built with Streamlit.

The interface allows users to:

1. Upload a video.
2. Preview the original video.
3. Start video processing.
4. Monitor the processing status.
5. View the number of people entering and exiting.
6. Watch the processed video.
7. Download the processed video.

## Docker

The application is containerized using Docker.

The project uses separate services for:

* FastAPI backend.
* Streamlit frontend.
* Prometheus.
* Grafana.

The services are managed using Docker Compose.

Start the application with:

```bash
docker compose up --build
```

After the containers start, the main services can be accessed locally through their configured ports.

Stop the application with:

```bash
docker compose down
```

## Monitoring

The FastAPI application exposes Prometheus metrics through:

```text
/metrics
```

The application records metrics related to:

* Total processed videos.
* Failed video-processing jobs.
* People entering.
* People exiting.
* Active processing jobs.
* Processing duration.
* API request count.
* API request duration.
* HTTP method.
* Endpoint.
* HTTP status code.

Prometheus collects these metrics and Grafana is used to visualize them, and provides visibility into application activity, video-processing performance, and API performance.

## Testing

The project includes automated tests for core functionality.

Run the tests with:

```bash
pytest
```

## CI/CD

GitHub Actions is used to automatically validate changes pushed to the repository.

The CI workflow performs automated checks such as:

* Installing project dependencies.
* Running tests.
* Building the Docker images.
