from prometheus_client import Counter, Histogram, Gauge


VIDEOS_PROCESSED = Counter(
    "people_counter_videos_processed_total",
    "Total number of videos successfully processed.",
)


VIDEOS_FAILED = Counter(
    "people_counter_videos_failed_total",
    "Total number of video processing jobs that failed.",
)


PEOPLE_ENTRIES = Counter(
    "people_counter_entries_total",
    "Total number of people counted entering.",
)


PEOPLE_EXITS = Counter(
    "people_counter_exits_total",
    "Total number of people counted exiting.",
)


PROCESSING_TIME = Histogram(
    "people_counter_processing_duration_seconds",
    "Time spent processing videos in seconds.",
)


JOBS_CREATED = Counter(
    "people_counter_jobs_created_total",
    "Total number of video processing jobs created.",
)


ACTIVE_JOBS = Gauge(
    "people_counter_active_jobs",
    "Number of video processing jobs currently active.",
)


# Count HTTP requests received by the API, grouped by method, endpoint, and HTTP status code
API_REQUESTS = Counter(
    "people_counter_api_requests_total",
    "Total number of HTTP requests received by the API.",
    ["method", "endpoint", "status"],
)


# Measure HTTP request duration, grouped by method and endpoint
API_REQUEST_DURATION = Histogram(
    "people_counter_api_request_duration_seconds",
    "Time spent handling API requests in seconds.",
    ["method", "endpoint"],
)