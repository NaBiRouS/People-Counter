import time
from src.config import API_URL
import requests
import streamlit as st


st.set_page_config(
    page_title="People Counter",
    layout="wide",
)


st.title("People Counter")
st.write(
    "Upload a video to detect, track, and count people "
    "moving across the counting line."
)

uploaded_file = st.file_uploader(
    "Upload a video",
    type=["mp4", "avi", "mov", "mkv"],
)


if uploaded_file is not None:
    # Display the uploaded video
    st.video(uploaded_file)

    if st.button("Process Video", type="primary"):

        try:
            # Upload the video and create a background processing job
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
                    progress_placeholder.info(
                        "Video is waiting to be processed..."
                    )

                elif status == "processing":
                    progress_placeholder.info(
                        "Processing video..."
                    )

                elif status == "completed":
                    progress_placeholder.success(
                        "Video processing completed."
                    )
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

            col1, col2 = st.columns(2)

            with col1:
                st.metric("IN", entries)

            with col2:
                st.metric("OUT", exits)


            # =================== OPTION 01 ===================
            # # Retrieve the completed H.264 video from FastAPI
            # video_response = requests.get(
            #     f"{API_URL}/videos/{job_id}",
            #     timeout=120,
            # )

            # video_response.raise_for_status()

            # processed_video = video_response.content

            # st.subheader("Processed Video")

            # # Display the browser-compatible H.264 video
            # st.video(processed_video)

            # st.download_button(
            #     label="Download Processed Video",
            #     data=processed_video,
            #     file_name=f"{job_id}_processed.mp4",
            #     mime="video/mp4",
            # )


            # =================== OPTION 02 ===================
            # Build the URL of the processed video
            video_url = f"{API_URL}/videos/{job_id}"

            st.subheader("Processed Video")

            # Let the browser request the video directly from FastAPI
            st.video(video_url)

            # Provide a direct download link
            st.markdown(f"[Download Processed Video]({video_url})")