# asr/asr_api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from transformers import pipeline
import torchaudio
import soundfile as sf
from pydub import AudioSegment
import os
import io
import tempfile

app = FastAPI()


# Load the ASR model globally to avoid re-loading for each request
try:
    asr_pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-960h")
    print("ASR model loaded successfully.")
except Exception as e:
    print(f"Error loading ASR model: {e}")
    asr_pipeline = None # Handle case where model loading fails

@app.get("/ping")
async def ping():
    """
    Health check endpoint.
    Returns "pong" if the service is running.
    """
    return "pong"

@app.post("/asr")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribes an audio MP3 file using the wav2vec2-large-960h model.

    Input:
        file: Binary of an audio mp3 file (multipart/form-data)

    Response:
        transcription: The transcribed text.
        duration: The duration of the audio file in seconds.
    """
    if asr_pipeline is None:
        raise HTTPException(status_code=500, detail="ASR model not loaded.")

    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only MP3 files are supported.")

    tmp_audio_path = None # Initialize to None for cleanup in finally block
    temp_wav_path = None

    try:
        # Read the uploaded file content into memory first
        content = await file.read()

        # Create a temporary MP3 file to handle pydub loading
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio_file:
            tmp_audio_file.write(content)
            tmp_audio_path = tmp_audio_file.name # Get the path

        # Load audio using pydub for format conversion and duration
        # pydub sometimes needs ffmpeg, which we'll address below
        audio = AudioSegment.from_file(tmp_audio_path, format="mp3")
        duration_seconds = len(audio) / 1000.0

        # Convert to 16kHz WAV in memory for the ASR model
        # Create another temporary WAV file for torchaudio to load, then delete
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav_file:
            temp_wav_path = tmp_wav_file.name
            audio.set_frame_rate(16000).set_channels(1).export(tmp_wav_file, format="wav")
            # Close the file explicitly to ensure it's released before torchaudio loads it
            tmp_wav_file.close()

        # Load the 16kHz wav file with torchaudio
        audio_input, sample_rate = torchaudio.load(temp_wav_path)

        if sample_rate != 16000:
            # Resample if needed, though pydub export should handle this
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            audio_input = resampler(audio_input)
            sample_rate = 16000

        # Transcribe the audio. Passing the path to the temporary WAV file is best for transformers.
        transcription_result = asr_pipeline(temp_wav_path, chunk_length_s=10, stride_length_s=(4, 2))

        transcribed_text = transcription_result['text'] if transcription_result and 'text' in transcription_result else ""

        return JSONResponse(content={
            "transcription": transcribed_text,
            "duration": f"{duration_seconds:.1f}"
        })

    except Exception as e:
        print(f"Error processing audio file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio file: {e}")
    finally:
        # Ensure temporary files are deleted even if an error occurs
        if tmp_audio_path and os.path.exists(tmp_audio_path):
            os.remove(tmp_audio_path)
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)