from datetime import datetime
import os
from pathlib import Path

from dotenv import load_dotenv
import requests
import streamlit as st


load_dotenv()


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
RAG_ENDPOINT = f"{API_BASE_URL}/rag/query"


class ChatInterface:
    def __init__(self):
        st.set_page_config(
            page_title="AI Assistant",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="collapsed",
        )

        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "is_typing" not in st.session_state:
            st.session_state.is_typing = False

        self.load_css()

    def load_css(self):
        css_file = Path(__file__).parent / "static" / "css" / "style.css"
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    @staticmethod
    def get_bot_response(question: str) -> str:
        try:
            response = requests.post(
                RAG_ENDPOINT,
                params={"question": question},
                headers={"accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()["response"]["content"]
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with the API: {str(e)}")
            return None

    def display_message(self, message):
        is_user = message["role"] == "user"
        message_class = "user-message" if is_user else "bot-message"
        avatar_class = "user-avatar" if is_user else "bot-avatar"
        avatar_content = "👤" if is_user else "🤖"

        st.markdown(
            f"""
            <div class="chat-message {message_class}">
                <div class="avatar {avatar_class}">{avatar_content}</div>
                <div>
                    <div class="message-content">{message["content"]}</div>
                    <div class="timestamp">{message["timestamp"]}</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    def display_typing_indicator(self):
        if st.session_state.is_typing:
            st.markdown(
                """
                <div class="chat-message bot-message">
                    <div class="avatar bot-avatar">🤖</div>
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    def display_chat_history(self):
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            self.display_message(message)
        self.display_typing_indicator()
        st.markdown("</div>", unsafe_allow_html=True)

    def create_input_area(self):
        with st.container():
            st.markdown('<div class="input-area">', unsafe_allow_html=True)

            col1, col2 = st.columns([6, 1])

            with col1:
                user_input = st.text_input(
                    label="Chat message",
                    placeholder="Type your message here...",
                    key="user_input",
                    label_visibility="collapsed",
                )

            with col2:
                submit = st.button("Send", key="send_button")

            st.markdown("</div>", unsafe_allow_html=True)

            return user_input, submit

    def handle_user_input(self):
        user_input, submit_button = self.create_input_area()

        if submit_button and user_input:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().strftime("%H:%M"),
                }
            )

            st.session_state.is_typing = True
            bot_response = self.get_bot_response(user_input)

            st.session_state.is_typing = False
            if bot_response:
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": bot_response,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )

            st.rerun()

    def render(self):
        st.markdown(
            """
            <div style="text-align: center;">
                <h1>AI Assistant Chatbot 🤖</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            label="Clear Chat",
            key="clear",
            help="Click to clear all chat messages",
        ):
            st.session_state.messages = []
            st.rerun()

        self.display_chat_history()
        self.handle_user_input()


def main():
    chat_interface = ChatInterface()
    chat_interface.render()


if __name__ == "__main__":
    main()
