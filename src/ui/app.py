import time
import requests
import streamlit as st

from src.config import API_URL, PUBLIC_API_URL


st.set_page_config(
    page_title="People Counter",
    page_icon="🚶",
    layout="wide",
)

# CSS injection for styling
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
        }

        .app-header {
            text-align: center;
            padding: 0 0 0.5rem 0;
        }

        .app-header h1 {
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .app-subtitle {
            text-align: center;
            color: #8a8f98;
            font-size: 1.05rem;
            margin-bottom: 2rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(150, 150, 150, 0.06);
            border: 1px solid rgba(150, 150, 150, 0.2);
            border-radius: 14px;
            padding: 1rem 1rem 0.6rem 1rem;
            text-align: center;
        }

        div[data-testid="stMetricLabel"] {
            justify-content: center;
        }

        div[data-testid="stMetricValue"] {
            font-size: 2.4rem;
        }

        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.4rem;
        }

        .results-divider {
            margin: 2rem 0 1rem 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <h1>🚶 People Counter</h1>
    </div>
    <div class="app-subtitle">
        Upload a video to detect, track, and count people moving across the counting line
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Upload section
# ------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a video",
    type=["mp4", "avi", "mov", "mkv"],
)

if uploaded_file is not None:
    # Display the uploaded video
    col_video, col_info = st.columns([2, 1])
    with col_video:
        st.video(uploaded_file)
    with col_info:
        st.markdown("#### 📄 File details")
        st.write(f"**Name:** {uploaded_file.name}")
        st.write(f"**Type:** {uploaded_file.type}")
        st.write(f"**Size:** {uploaded_file.size / (1024 * 1024):.2f} MB")
        st.write("")
        process_clicked = st.button(
            "▶ Process Video", type="primary", use_container_width=True
        )

    if process_clicked:
        try:
            # Upload the video and create a background processing job
            with st.spinner("Uploading video..."):
                response = requests.post(
                    f"{API_URL}/process-video",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    },
                    timeout=120,
                )

            # Raise an exception if FastAPI returned an error
            response.raise_for_status()
            job = response.json()
            job_id = job["job_id"]

        except requests.RequestException as exc:
            st.error(f"Could not start video processing: {exc}")

        else:
            # Poll the API until processing finishes
            progress_placeholder = st.empty()

            while True:
                status_response = requests.get(
                    f"{API_URL}/jobs/{job_id}",
                    timeout=30,
                )
                status_response.raise_for_status()
                status = status_response.json()["status"]

                if status == "queued":
                    progress_placeholder.info("⏳ Video is waiting to be processed...")
                elif status == "processing":
                    progress_placeholder.info("⚙️ Processing video...")
                elif status == "completed":
                    progress_placeholder.success("✅ Video processing completed.")
                    break
                elif status == "failed":
                    error = status_response.json().get(
                        "error",
                        "Unknown processing error.",
                    )
                    st.error(f"Video processing failed: {error}")
                    st.stop()

                # Wait before checking the job status again
                time.sleep(2)

            results = status_response.json()
            entries = results["entries"]
            exits = results["exits"]

            st.markdown('<hr class="results-divider">', unsafe_allow_html=True)
            st.markdown("### 📊 Results")

            col1, col2 = st.columns(2)
            with col1:
                st.metric(" IN", entries)
            with col2:
                st.metric(" OUT", exits)


            # Build the URL of the processed video
            video_url = f"{PUBLIC_API_URL}/videos/{job_id}"

            st.subheader("🎬 Processed Video")
            # Let the browser request the video directly from FastAPI
            st.video(video_url)
            # Provide a direct download link
            st.markdown(f"[⬇️ Download Processed Video]({video_url})")