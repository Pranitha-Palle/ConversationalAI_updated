document.addEventListener('DOMContentLoaded', function() {
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const transcriptElement = document.getElementById('transcript');
    const playbackAudio = document.getElementById('playbackAudio'); // Audio element for playback
    const audioElement = document.getElementById('audioElement');
    const textInput = document.getElementById('textInput');
    const synthesizeButton = document.getElementById('synthesizeButton');

    let mediaRecorder;
    let audioChunks = [];

    // Start recording
    recordButton.addEventListener('click', async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            playbackAudio.src = audioUrl; // Set the source of the playback audio element

            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.wav');

            // Send the audio to the server for speech-to-text conversion
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                if (result.transcript) {
                    transcriptElement.value = result.transcript; // Display transcript in text area
                } else if (result.error) {
                    transcriptElement.value = `Error during transcription: ${result.error}`;
                } else {
                    transcriptElement.value = "No transcription available.";
                }
            } catch (error) {
                transcriptElement.value = "Error during transcription.";
                console.error("Error:", error);
            }
        };

        recordButton.disabled = true;
        stopButton.disabled = false;
    });

    // Stop recording
    stopButton.addEventListener('click', () => {
        mediaRecorder.stop();
        recordButton.disabled = false;
        stopButton.disabled = true;
        audioChunks = [];
    });

    // Synthesize text to speech
    synthesizeButton.addEventListener('click', async () => {
        const text = textInput.value;
        try {
            const response = await fetch('/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            const result = await response.json();
            if (result.audioUrl) {
                audioElement.src = result.audioUrl;
                audioElement.play();
            }
        } catch (error) {
            console.error("Error during synthesis:", error);
        }
    });
});