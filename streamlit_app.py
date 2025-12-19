import streamlit as st
import os
import tempfile
import logging
from audio_cutter import AudioTextCutter

# Set page configuration
st.set_page_config(
    page_title="Iris Audio Cutter",
    page_icon="✂️",
    layout="centered"
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache the model loading to prevent reloading on every interaction
@st.cache_resource
def load_model(model_size):
    return AudioTextCutter(model_size=model_size)

def main():
    st.title("✂️ Iris Audio Cutter")
    st.markdown("""
    Upload an audio file, enter a text phrase, and this tool will find and clip that segment for you.
    """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("Settings")
        model_size = st.selectbox(
            "Whisper Model Size",
            ["tiny", "base", "small", "medium", "large-v3"],
            index=1,
            help="Larger models are more accurate but slower."
        )
        padding = st.slider(
            "Padding (seconds)",
            min_value=0.0,
            max_value=2.0,
            value=0.1,
            step=0.1,
            help="Time added before and after the matched audio."
        )
        threshold = st.slider(
            "Match Threshold",
            min_value=50,
            max_value=100,
            value=80,
            step=5,
            help="Minimum fuzzy match score required (0-100)."
        )

    # Main interface
    uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a", "ogg"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")
        
        text_query = st.text_input("Enter the text to find in the audio:", placeholder="e.g. 'Hello world this is a test'")
        
        if st.button("Find and Clip", type="primary"):
            if not text_query:
                st.warning("Please enter some text to search for.")
            else:
                # Use st.status container for better progress indication
                with st.status("Initializing...", expanded=True) as status:
                    try:
                        # Save uploaded file to a temporary file
                        status.write("Saving uploaded file...")
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        try:
                            # Load model
                            status.write(f"Loading Whisper model ({model_size})...")
                            cutter = load_model(model_size)
                            
                            # Transcribe
                            status.write("Transcribing audio (this may take a while)...")
                            progress_bar = st.progress(0, text="Starting transcription...")
                            
                            def update_progress(current, total):
                                if total > 0:
                                    percent = min(current / total, 1.0)
                                    progress_bar.progress(percent, text=f"Transcribing: {int(percent*100)}% ({current:.1f}s / {total:.1f}s)")
                                
                            words = cutter.transcribe_audio(tmp_path, progress_callback=update_progress)
                            progress_bar.progress(1.0, text="Transcription complete!")
                            
                            # Find timestamps
                            status.write(f"Searching for text: '{text_query}'...")
                            timestamps = cutter.find_timestamps(words, text_query, threshold=threshold)
                            
                            if timestamps:
                                start, end = timestamps
                                status.write(f"Match found at {start:.2f}s - {end:.2f}s. Clipping...")
                                
                                # Clip audio
                                output_filename = f"clip_{start:.2f}_{end:.2f}.wav"
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
                                    output_path = tmp_out.name
                                
                                cutter.clip_audio(tmp_path, start, end, output_path, padding=padding)
                                
                                status.update(label="Processing complete!", state="complete", expanded=False)
                                
                                # Show result
                                st.success(f"Match found! ({start:.2f}s - {end:.2f}s)")
                                st.subheader("Result")
                                st.audio(output_path, format="audio/wav")
                                
                                # Download button
                                with open(output_path, "rb") as f:
                                    st.download_button(
                                        label="Download Clip",
                                        data=f,
                                        file_name=output_filename,
                                        mime="audio/wav"
                                    )
                                    
                                # Clean up output file
                                os.unlink(output_path)
                            else:
                                status.update(label="Text not found", state="error", expanded=False)
                                st.error(f"Could not find the text '{text_query}' in the audio with sufficient confidence.")
                                
                        finally:
                            # Clean up input file
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
                                
                    except Exception as e:
                        status.update(label="Error occurred", state="error")
                        st.error(f"An error occurred: {str(e)}")
                        logger.error(f"Error processing request: {e}")

if __name__ == "__main__":
    main()
