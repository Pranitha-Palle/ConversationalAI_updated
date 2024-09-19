import os
from flask import Flask, render_template, request, jsonify
from google.cloud import speech, texttospeech
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

# Path to the Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\palle\OneDrive\Desktop\conversationalAI\credentials.json"

# Initializing Google Speech-to-Text and Text-to-Speech clients
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

@app.route('/')
def index():
    return render_template('index.html')

# Handling audio upload and speech-to-text conversion
@app.route('/upload', methods=['POST'])
def upload_audio():
    file = request.files['file']
    filename = 'recording.mp4'

    # Ensure the uploads folder exists
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # Read the audio file content
    audio_files='audio recording.wav'
    with io.open(filepath, 'rb') as audio_file:
        content = audio_file.read()
 
        audio = speech.RecognitionAudio(content=content)
        
    # Speech-to-text configuration
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,  # Adjust sample rate to match the recording
        language_code='en-US',
        model = 'video'
    )

    #try:
        # Send audio data to Google Speech-to-Text API for transcription
    response = speech_client.recognize(config=config, audio=audio)
    for results in response.results:
        print(results.alternatives[0].transcript)
        

        # If transcription is successful, extract the transcript
        #if response.results:
            #transcript = response.results.alternatives[0].transcript
            #print(transcript)
        #else:
            #transcript = "No transcription available."

    #except Exception as e:
        #print(f"Error during transcription: {e}")
        #return jsonify({'error': str(e)})

    #return jsonify({'transcript': transcript})

# Route for handling text-to-speech conversion
@app.route('/synthesize', methods=['POST'])
def synthesize_text():
    data = request.json
    input_text = data.get('text', '')

    # Set up the text-to-speech request
    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Send text-to-speech request to Google API
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Save the generated audio to a file
    audio_filename = "output.mp3"
    audio_path = os.path.join('static', audio_filename)
    with open(audio_path, 'wb') as out:
        out.write(response.audio_content)

    return jsonify({'audioUrl': f'/static/{audio_filename}'})

if __name__ == '__main__':
    app.run(debug=True)