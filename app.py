import os
import streamlit as st
import google.generativeai as genai
from elevenlabs import ElevenLabs, VoiceSettings
import tempfile
from dotenv import load_dotenv
import pygame

# 🎯 Load environment variables
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

# ✅ Configure Gemini
genai.configure(api_key=GOOGLE_KEY)

# ✅ Configure ElevenLabs client
client = ElevenLabs(api_key=ELEVEN_KEY)

# 🎧 Initialize pygame for audio playback
pygame.mixer.init()

# 🧩 Define Characters and Voices
CHARACTERS = {
    "Crush 🐢": {
        "style": "Talk like Crush from Finding Nemo — laid-back surfer dude, chill, uses 'dude' a lot.",
        "voice_id": "iP95p4xoKVk53GoZ742B",  # Chris (example)
        "image": "assets/crush.png",
        "voice_settings": VoiceSettings(stability=0.4, similarity_boost=0.9),
    },
    "Baymax 🤖": {
        "style": "Talk like Baymax from Big Hero 6 — calm, compassionate, precise, and caring.",
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",  # CalmBot (example)
        "image": "assets/baymax.png",
        "voice_settings": VoiceSettings(stability=0.9, similarity_boost=0.6),
    },
    "Gina 💅": {
        "style": "Talk like Gina Linetti from Brooklyn 99 — witty, confident, sarcastic but helpful.",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Sassy Gina
        "image": "assets/gina.png",
        "voice_settings": VoiceSettings(stability=0.5, similarity_boost=0.95),
    },
    "Rachel 👗": {
        "style": "Talk like Rachel Green from Friends — stylish, kind, emotional, gives fashion/life advice.",
        "voice_id": "Xb7hH8MSUJpSbSDYk0k2",  # Warm Rachel
        "image": "assets/rachel.png",
        "voice_settings": VoiceSettings(stability=0.7, similarity_boost=0.85),
    },
}

# 🗣️ Function to play audio
def play_audio(audio_bytes):
    """Play audio bytes using pygame"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(audio_bytes)
    temp_file.close()
    pygame.mixer.music.load(temp_file.name)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove(temp_file.name)


# 💬 Function to get character response
def get_character_reply(character_name, user_message):
    char = CHARACTERS[character_name]
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"You are {character_name}. {char['style']}\nUser: {user_message}\n{character_name}:"

    response = model.generate_content(prompt)
    text = response.text.strip()

    st.markdown(f"**{character_name}:** {text}")

    # Convert to voice using ElevenLabs
    try:
        audio_gen = client.text_to_speech.convert(
            voice_id=char["voice_id"],
            model_id="eleven_multilingual_v2",
            text=text,
            voice_settings=char["voice_settings"],
        )
        audio_bytes = b"".join(audio_gen)
        play_audio(audio_bytes)
    except Exception as e:
        st.error(f"Voice error: {e}")


# 🖥️ Streamlit UI
st.set_page_config(page_title="AI Character Lounge", page_icon="🎭", layout="centered")
st.title("🎭 AI Character Lounge")
st.write("Choose a character to talk to — chill, laugh, or get advice!")

# Character selection
character = st.selectbox("Choose your character:", list(CHARACTERS.keys()))

# Show character image
try:
    st.image(CHARACTERS[character]["image"], width=200)
except Exception:
    st.warning("Couldn't load character image — make sure it's in the 'assets' folder.")

st.markdown("---")

# Chat input
mode = st.radio("Choose your mode:", ["💬 Text Chat", "🎙️ Voice Chat (coming soon)"])

if mode == "💬 Text Chat":
    user_input = st.text_input("You:", placeholder="Type your message here...")
    if st.button("Send"):
        if user_input.strip():
            get_character_reply(character, user_input)
        else:
            st.warning("Please type a message first!")

elif mode == "🎙️ Voice Chat (coming soon)":
    st.info("Voice chat feature will be added in Phase 2 🎤")

