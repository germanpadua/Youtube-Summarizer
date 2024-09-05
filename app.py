# File: app.py

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from gtts import gTTS
import os

# Summarization pipeline using Hugging Face transformers
summarizer = pipeline("summarization", model="t5-small")

def get_youtube_video_id(url):
    """Extract YouTube video ID from URL"""
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1]
    elif "youtu.be/" in url:
        return url.split("/")[-1]
    else:
        return None

def fetch_transcription(video_id):
    """Fetch the transcription using YouTube Transcript API"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([item['text'] for item in transcript])
        return text
    except Exception as e:
        return str(e)

def summarize_text(text):
    """Summarize the transcription using Hugging Face transformers"""
    try:
        # Hugging Face's summarizer model, adjusting chunk size for large texts
        max_chunk_size = 1024  # Max input length for the model is around 1024 tokens
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        summarized_chunks = [summarizer(chunk)[0]['summary_text'] for chunk in chunks]
        summary = " ".join(summarized_chunks)
        return summary
    except Exception as e:
        return str(e)

def convert_text_to_speech(text, filename="output.mp3"):
    """Convert summarized text to speech using gTTS"""
    try:
        tts = gTTS(text)
        tts.save(filename)
        return filename
    except Exception as e:
        return str(e)

# Streamlit app
st.title("YouTube Video Summarizer and Podcast Generator (Free Version)")

# Input YouTube URL
youtube_url = st.text_input("Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=video_id")

if youtube_url:
    video_id = get_youtube_video_id(youtube_url)

    if video_id:
        st.write(f"Fetching transcription for Video ID: {video_id}")
        transcription = fetch_transcription(video_id)
        
        if transcription:
            st.subheader("Transcription")
            st.text_area("Full Transcription", transcription, height=200)

            # Summarize transcription
            st.write("Summarizing transcription...")
            summary = summarize_text(transcription)

            if summary:
                st.subheader("Summary")
                st.write(summary)

                # Convert summary to speech
                st.write("Converting summary to podcast...")
                audio_file = convert_text_to_speech(summary)

                if audio_file:
                    # Play the generated audio
                    audio_bytes = open(audio_file, "rb").read()
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("Podcast generated successfully!")
            else:
                st.error("Failed to summarize the transcription.")
        else:
            st.error("Failed to fetch the transcription.")
    else:
        st.error("Invalid YouTube URL.")
