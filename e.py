import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, AIMessage
from langchain import PromptTemplate

import streamlit as st
from gtts import gTTS
import tempfile
import speech_recognition as sr

load_dotenv()

def main():
    language_codes = {
        "English": "en",
        "German": "de",
        "Spanish": "es",
        "French": "fr",
        "Italian": "it"
    }

    openai_api_key = os.getenv('OPENAI_API_KEY')
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.9, openai_api_key=openai_api_key)

    st.title("Polyglot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    lang_requirements = {
        'Beginner': """maximum of 50 to 100 words. use as basic and simple vocabulary and sentence structures as possible. 
            Must avoid idioms, slang, and complex grammatical constructs.""",
        'Intermediate': """maximum of 100 to 150 words. use a wider range of vocabulary and a variety of sentence structures. 
            You can include some idioms and colloquial expressions, but avoid highly technical language or complex literary expressions.""",
        'Advanced': """maximum of 150 to 200 words. use sophisticated vocabulary, complex sentence structures, idioms, colloquial expressions, 
            and technical language where appropriate."""
    }

    template = """You are an AI language learning assistant dedicated to helping learners practice their {language}.
        In this interaction, you will initiate and lead a conversation about a {topic} that the language learner selects.
        The conversation's length and complexity will vary based on the proficiency level chosen by the language learner.
        You will interact with the human in the role of a {proficiency_level} speaker.
        Language Proficiency Requirement: {lang_requirement}"""

    with st.sidebar:
        selected_language = st.selectbox("Language:", options=["English", "German", "Spanish", "French", "Italian"], key="language")
        selected_topic = st.selectbox("Topic:", options=["General", "Science", "History", "Art"], key="topic")
        selected_proficiency_level = st.selectbox("Proficiency Level:", options=["Beginner", "Intermediate", "Advanced"], key="level")

        st.session_state.selected_language = selected_language
        st.session_state.selected_topic = selected_topic
        st.session_state.selected_proficiency_level = selected_proficiency_level

        col1, col2 = st.columns(2)
        with col1:
            start_button = st.button("Start Conversation")

        with col2:
            clear_button = st.button("Clear Conversation")

    if start_button:
        prompt = PromptTemplate(
            template=template,
            input_variables=['language', 'topic', 'proficiency_level', 'lang_requirement']
        )

        formatted_prompt = prompt.format(
            language=selected_language,
            topic=selected_topic,
            proficiency_level=selected_proficiency_level,
            lang_requirement=lang_requirements[selected_proficiency_level]
        )

        messages = [
            SystemMessage(content=str(formatted_prompt), verbose=True)
        ]

        response = chat(messages)

        st.session_state.messages.append({"sender": "AI", "content": response.content})

        language_codes = {
            "English": "en",
            "German": "de",
            "Spanish": "es",
            "French": "fr",
            "Italian": "it"
        }

        selected_language_code = language_codes[selected_language]

        tts = gTTS(response.content, lang=selected_language_code)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            audio_file_path = temp_file.name
            tts.save(audio_file_path)

        st.audio(audio_file_path, format="audio/mp3")

    if clear_button:
        st.session_state.messages.clear()

    user_input = st.chat_input("Your Message:")
    if user_input:
        st.session_state.messages.append({"sender": "User", "content": user_input})

        user_message = AIMessage(content=user_input)
        response = chat([user_message])

        st.session_state.messages.append({"sender": "AI", "content": response.content})

        language_codes = {
            "English": "en",
            "German": "de",
            "Spanish": "es",
            "French": "fr",
            "Italian": "it"
        }

        selected_language_code = language_codes[selected_language]

        user_tts = gTTS(user_input, lang=selected_language_code)
        ai_tts = gTTS(response.content, lang=selected_language_code)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as user_audio_file:
            user_audio_file_path = user_audio_file.name
            user_tts.save(user_audio_file_path)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as ai_audio_file:
            ai_audio_file_path = ai_audio_file.name
            ai_tts.save(ai_audio_file_path)

        st.audio(user_audio_file_path, format="audio/mp3")
        st.audio(ai_audio_file_path, format="audio/mp3")

    if "speech_recognition_on" not in st.session_state:
        st.session_state.speech_recognition_on = False

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with st.sidebar:
        col3, _ = st.columns(2)
        with col3:
            speech_recognition_button = st.button("Start Speech Recognition") if not st.session_state.speech_recognition_on else st.button("Stop Speech Recognition")

    if speech_recognition_button:
        st.session_state.speech_recognition_on = not st.session_state.speech_recognition_on

        if st.session_state.speech_recognition_on:
            with mic as source:
                audio = recognizer.listen(source)

            user_input = recognizer.recognize_google(audio, language=language_codes[selected_language])

            st.session_state.messages.append({"sender": "User", "content": user_input})

            user_message = AIMessage(content=user_input)
            response = chat([user_message])

            selected_language_code = language_codes[selected_language]

            tts = gTTS(response.content, lang=selected_language_code)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                audio_file_path = temp_file.name
                tts.save(audio_file_path)

            st.audio(audio_file_path, format="audio/mp3")

            st.session_state.messages.append({"sender": "AI", "content": response.content})

    for message in st.session_state.messages:
        if message["sender"] == "AI":
            with st.chat_message("AI"):
                st.write(message["content"])
        elif message["sender"] == "User":
            with st.chat_message("User"):
                st.write(message["content"])

if __name__ == '__main__':
    main()
