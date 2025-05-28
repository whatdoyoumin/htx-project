# asr/cv-decode.py
import pandas as pd
import requests
import os
import time


CSV_DIR   = "../common_voice"
AUDIO_DIR = os.path.join(CSV_DIR,"cv-valid-dev")
CSV_FILE  = os.path.join(CSV_DIR, "cv-valid-dev.csv")
#ASR_API_URL = "http://localhost:8001/asr" local development
#ASR_API_URL = os.getenv('ASR_API_URL', "http://172.31.22.243:5000/asr") #deploy on server

# Use environment variable if set, otherwise default to localhost
ASR_API_URL = os.getenv("ASR_API_URL", "http://localhost:8001/asr")


def transcribe_and_update_csv():
    """
    Calls the ASR API to transcribe MP3 files from the Common Voice dataset
    and updates the cv-valid-dev.csv with generated transcriptions.
    """
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found at {CSV_FILE}. Please ensure common-voice.zip is extracted correctly.")
        return

    try:
        df = pd.read_csv(CSV_FILE)
            # ==== ADD THIS FOR A QUICK SMOKE TEST ====
        #df = df.head(5)   # only process the first row
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Add a new column for generated text if it doesn't exist [cite: 21]
    if 'generated_text' not in df.columns:
        df['generated_text'] = None # Initialize with None or empty string

    print(f"Starting transcription of {len(df)} audio files...")
    transcription_count = 0
    error_count = 0

    for index, row in df.iterrows():
        filepath = os.path.join(AUDIO_DIR, row['filename'])
        if not os.path.exists(filepath):
            print(f"Warning: File not found: {filepath}. Skipping.")
            error_count += 1
            continue

        try:
            with open(filepath, 'rb') as f:
                files = {'file': (row['filename'], f, 'audio/mpeg')}
                response = requests.post(ASR_API_URL, files=files)
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                result = response.json()
                transcription = result.get('transcription', '')
                # duration = result.get('duration', '') # We could also store duration if needed

                df.at[index, 'generated_text'] = transcription
                transcription_count += 1
                if transcription_count % 100 == 0:
                    print(f"Transcribed {transcription_count} files so far.")

        except requests.exceptions.RequestException as e:
            print(f"Error calling ASR API for {filepath}: {e}")
            df.at[index, 'generated_text'] = f"API Error: {e}"
            error_count += 1
        except Exception as e:
            print(f"An unexpected error occurred for {filepath}: {e}")
            df.at[index, 'generated_text'] = f"Processing Error: {e}"
            error_count += 1

        # Optional: Add a small delay to avoid overwhelming the API
        # time.sleep(0.1)

    # Save the updated CSV file with transcription output
    output_csv_path = os.path.join(CSV_DIR, "cv-valid-dev_transcribed.csv")
    df.to_csv(output_csv_path, index=False)
    print(f"\nTranscription complete!")
    print(f"Successfully transcribed {transcription_count} files.")
    print(f"Encountered {error_count} errors/skipped files.")
    print(f"Updated CSV saved to: {output_csv_path}")


if __name__ == "__main__":
    print("Ensure your ASR microservice is running at:", ASR_API_URL)
    print("e.g., run `python asr_api.py` in the 'asr' directory.")
    input("Press Enter to start transcription...")
    transcribe_and_update_csv()