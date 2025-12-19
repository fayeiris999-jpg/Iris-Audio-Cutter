import os
import logging
import re
from typing import List, Dict, Optional, Tuple, Callable
from faster_whisper import WhisperModel
from pydub import AudioSegment
from rapidfuzz import fuzz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AudioTextCutter:
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize the AudioTextCutter with a Whisper model.
        
        Args:
            model_size: The size of the Whisper model (e.g., "tiny", "base", "small", "medium", "large-v3").
            device: Device to run the model on ("cpu" or "cuda").
            compute_type: Quantization type (e.g., "int8", "float16").
        """
        logger.info(f"Loading Whisper model: {model_size} on {device}...")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by converting to lowercase and removing punctuation.
        """
        # Remove punctuation and extra whitespace, convert to lowercase
        text = re.sub(r'[^\w\s]', '', text).lower()
        return re.sub(r'\s+', ' ', text).strip()

    def transcribe_audio(self, audio_path: str, progress_callback: Optional[Callable[[float, float], None]] = None) -> List[Dict]:
        """
        Transcribe audio file and return a list of words with timestamps.
        
        Args:
            audio_path: Path to the input audio file.
            progress_callback: Optional callback function(current_time, total_duration) to report progress.
            
        Returns:
            List of dictionaries containing 'word', 'start', 'end', and 'probability'.
        """
        logger.info(f"Transcribing audio: {audio_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        segments, info = self.model.transcribe(audio_path, word_timestamps=True)
        total_duration = info.duration
        logger.info(f"Processing audio with duration {total_duration:.2f}s")
        
        all_words = []
        # faster-whisper returns a generator, so we iterate through it
        for segment in segments:
            if progress_callback and total_duration > 0:
                progress_callback(segment.end, total_duration)
                
            if segment.words:
                for word in segment.words:
                    all_words.append({
                        'word': word.word.strip(),
                        'start': word.start,
                        'end': word.end,
                        'probability': word.probability
                    })
        
        # Ensure 100% progress at end
        if progress_callback and total_duration > 0:
            progress_callback(total_duration, total_duration)
            
        logger.info(f"Transcription complete. Found {len(all_words)} words.")
        return all_words

    def find_timestamps(self, transcribed_words: List[Dict], target_text: str, threshold: int = 80) -> Optional[Tuple[float, float]]:
        """
        Find the start and end timestamps for the target text in the transcribed words using fuzzy matching.
        
        Args:
            transcribed_words: List of word dictionaries from transcribe_audio.
            target_text: The text string to search for.
            threshold: Minimum fuzzy match score (0-100) to consider a match.
            
        Returns:
            Tuple of (start_time, end_time) if found, else None.
        """
        if not transcribed_words or not target_text:
            return None

        # Normalize target text and split into words
        normalized_target = self._normalize_text(target_text)
        target_word_tokens = normalized_target.split()
        target_len = len(target_word_tokens)
        
        if target_len == 0:
            return None

        best_score = 0
        best_segment = None

        # Sliding window search
        # We try window sizes close to the target word count to account for segmentation differences
        window_sizes = {target_len, target_len + 1, target_len - 1} if target_len > 1 else {1}
        
        # Iterate through the transcribed words
        for i in range(len(transcribed_words)):
            for w_size in window_sizes:
                if w_size <= 0:
                    continue
                if i + w_size > len(transcribed_words):
                    continue
                
                # Extract window
                window_words = transcribed_words[i : i + w_size]
                
                # Construct string from window
                window_text = " ".join([w['word'] for w in window_words])
                normalized_window = self._normalize_text(window_text)
                
                # Calculate fuzzy match score
                # ratio compares the similarity of the two strings
                score = fuzz.ratio(normalized_target, normalized_window)
                
                if score > best_score:
                    best_score = score
                    # Store start of first word and end of last word
                    best_segment = (window_words[0]['start'], window_words[-1]['end'])

        logger.info(f"Best match score: {best_score}")
        
        if best_score >= threshold:
            logger.info(f"Match found: {best_segment}")
            return best_segment
        else:
            logger.warning("No match found above threshold.")
            return None

    def clip_audio(self, audio_path: str, start_time: float, end_time: float, output_path: str, padding: float = 0.1):
        """
        Clip the audio file based on start and end timestamps.
        
        Args:
            audio_path: Path to the original audio file.
            start_time: Start time in seconds.
            end_time: End time in seconds.
            output_path: Path to save the clipped audio.
            padding: Padding in seconds to add to start and end.
        """
        logger.info(f"Clipping audio from {start_time}s to {end_time}s with {padding}s padding...")
        
        try:
            audio = AudioSegment.from_file(audio_path)
            
            # Apply padding (Pydub uses milliseconds)
            start_ms = max(0, (start_time - padding) * 1000)
            end_ms = min(len(audio), (end_time + padding) * 1000)
            
            # Slice audio
            clipped_audio = audio[start_ms:end_ms]
            
            # Export
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            clipped_audio.export(output_path, format="wav")
            logger.info(f"Audio clipped and saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error clipping audio: {e}")
            raise

def process_audio_clipping(audio_file: str, text_query: str, output_file: str = "output_clip.wav"):
    """
    Main workflow function to process audio clipping based on text query.
    """
    try:
        # 1. Initialize tool
        cutter = AudioTextCutter(model_size="base") # Using 'base' for balance of speed/accuracy
        
        # 2. Transcribe
        words = cutter.transcribe_audio(audio_file)
        
        # 3. Find Timestamps
        timestamps = cutter.find_timestamps(words, text_query)
        
        if timestamps:
            start, end = timestamps
            print(f"Text found at: {start:.2f}s - {end:.2f}s")
            
            # 4. Clip and Export
            cutter.clip_audio(audio_file, start, end, output_file)
            print(f"Success! Clip saved to {output_file}")
        else:
            print(f"Could not find the text '{text_query}' in the audio.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example Usage
    # Replace these paths with actual files for testing
    
    # Check if we have a sample file, otherwise just print usage
    sample_audio = "sample_audio.mp3" 
    target_text = "Hello world this is a test"
    
    if os.path.exists(sample_audio):
        process_audio_clipping(sample_audio, target_text)
    else:
        print("Please provide a valid audio file path to run the script.")
        print("Usage Example:")
        print(f"  process_audio_clipping('path/to/audio.mp3', 'text to find')")
