
import streamlit as st
from supabase import create_client
from datetime import datetime
import time

st.set_page_config(
    page_title="Real-time Chat",
    page_icon="💬",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: #F7F5F0;
}
.main-title {
    font-family: Georgia, serif;
    font-size: 42px;
    font-weight: bold;
    color: #292720;
}
.subtitle {
    color: #827B70;
    font-size: 14px;
}
.chat-card {
    background: white;
    border: 1px solid #E8E2D8;
    border-radius: 14px;
    padding: 14px 18px;
    margin: 10px 0;
}
.chat-name {
    font-weight: bold;
    color: #62594B;
    font-size: 13px;
}
.chat-message {
    color: #292720;
    font-size: 16px;
    margin-top: 7px;
    overflow-wrap: anywhere;
}
.chat-time {
    color: #A39B8F;
    font-size: 11px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">CHAT ROOM.</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A little space to connect.</div>',
    unsafe_allow_html=True
)

st.write("")

# Connect to Supabase
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(supabase_url, supabase_key)
except Exception:
    st.error(
        "Database connection is not configured yet. "
        "Please add your Supabase credentials in Streamlit Secrets."
    )
    st.stop()

# Username
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.markdown("### Welcome!")
    username = st.text_input("Choose your nickname", max_chars=30)

    if st.button("Enter Chat Room", use_container_width=True):
        if username.strip():
            st.session_state.username = username.strip()
            st.rerun()
        else:
            st.warning("Please enter a nickname.")
    st.stop()

# Header
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"### Hello, {st.session_state.username} 👋")

with col2:
    if st.button("Log out"):
        st.session_state.username = ""
        st.rerun()

st.divider()

# Send message
with st.form("message_form", clear_on_submit=True):
    message = st.text_input(
        "Your message",
        max_chars=2000,
        placeholder="Write something..."
    )
    send = st.form_submit_button("Send message", use_container_width=True)

    if send:
        if message.strip():
            try:
                supabase.table("messages").insert({
                    "username": st.session_state.username,
                    "content": message.strip()
                }).execute()
                st.success("Message sent!")
            except Exception as e:
                st.error(f"Could not send message: {e}")
        else:
            st.warning("Message cannot be empty.")

st.divider()

# Load messages
st.markdown("### Conversation")

try:
    response = (
        supabase.table("messages")
        .select("*")
        .order("created_at", desc=False)
        .limit(100)
        .execute()
    )

    messages = response.data or []

    if not messages:
        st.info("No messages yet. Start the conversation!")

    for item in messages:
        created_at = item.get("created_at", "")
        try:
            time_text = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            ).astimezone().strftime("%H:%M")
        except Exception:
            time_text = ""

        st.markdown(
            f"""
            <div class="chat-card">
                <div class="chat-name">{item.get('username', 'User')}</div>
                <div class="chat-message">{item.get('content', '')}</div>
                <div class="chat-time">{time_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

except Exception as e:
    st.error(f"Could not load messages: {e}")

# Refresh
st.caption("The chat refreshes automatically every 3 seconds.")

time.sleep(3)
st.rerun()
