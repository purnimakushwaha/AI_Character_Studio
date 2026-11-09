
import streamlit as st
from ollama import Client
import uuid
import html

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Character Studio",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION STATE
# =====================================================

DEFAULTS = {
    "characters": [],
    "chat_histories": {},
    "selected_character": None,
    "generated_character": None,
    "pending_chat": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value


# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 15% 10%, #30205c 0%, transparent 35%),
        radial-gradient(circle at 85% 80%, #172c60 0%, transparent 35%),
        linear-gradient(135deg, #090d1c, #15132e, #211747);
    color: white;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: white !important;
}

p, label {
    color: #e5e7eb;
}

.hero {
    padding: 40px 25px;
    text-align: center;
    border-radius: 25px;
    background: linear-gradient(
        120deg,
        rgba(124,58,237,.28),
        rgba(37,99,235,.20)
    );
    border: 1px solid rgba(255,255,255,.15);
    margin-bottom: 30px;
    box-shadow: 0 15px 45px rgba(0,0,0,.2);
}

.hero h1 {
    font-size: 43px;
    font-weight: 850;
    margin-bottom: 8px;
}

.hero p {
    color: #c4b5fd;
    font-size: 17px;
}

.character-card {
    background: linear-gradient(
        135deg,
        rgba(124,58,237,.20),
        rgba(37,99,235,.13)
    );
    border: 1px solid rgba(167,139,250,.25);
    border-radius: 20px;
    padding: 22px;
    margin: 12px 0;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #17172e !important;
    color: white !important;
    border-radius: 12px !important;
}

.stButton button,
.stFormSubmitButton button {
    border-radius: 12px;
    min-height: 45px;
    font-weight: 650;
    border: 1px solid rgba(255,255,255,.15);
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    color: white;
    transition: .2s;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    border-color: #c4b5fd;
    background: linear-gradient(90deg,#6d28d9,#4338ca);
}

[data-testid="stSidebar"] {
    background: #111127;
}

[data-testid="stChatMessage"] {
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 15px;
}

div[data-baseweb="select"] {
    background: #17172e;
    border-radius: 12px;
}

hr {
    border-color: rgba(255,255,255,.15);
}

.small-note {
    color: #a5b4fc;
    font-size: 13px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# OLLAMA CLOUD CONNECTION
# =====================================================

def get_ollama_client():

    try:
        api_key = st.secrets.get("OLLAMA_API_KEY", "")

    except Exception:
        api_key = ""

    if not api_key:
        raise ValueError(
            "OLLAMA_API_KEY is missing. "
            "Add your API key in Streamlit Cloud Settings > Secrets."
        )

    return Client(
        host="https://ollama.com",
        headers={
            "Authorization": f"Bearer {api_key}"
        }
    )


def get_ai_response(model, messages):

    client = get_ollama_client()

    response = client.chat(
        model=model,
        messages=messages,
        stream=False
    )

    return response.message.content


# =====================================================
# ERROR HANDLING
# =====================================================

def show_error(error):

    message = str(error)
    lower = message.lower()

    if "api_key" in lower or "missing" in lower:

        st.error(
            "🔑 Ollama API key is missing. "
            "Check your Streamlit Secrets configuration."
        )

    elif "401" in lower or "unauthorized" in lower:

        st.error(
            "🔒 API authentication failed. "
            "Check your Ollama API key."
        )

    elif "403" in lower or "forbidden" in lower:

        st.error(
            "⛔ Access denied. Check your Ollama account access "
            "and model availability."
        )

    elif "404" in lower or "not found" in lower:

        st.error(
            "❌ Model not found. Check the model name "
            "in the sidebar."
        )

    elif "429" in lower or "rate limit" in lower:

        st.error(
            "⏳ API usage limit reached. Please try again later."
        )

    elif any(word in lower for word in [
        "connection",
        "connect",
        "timeout"
    ]):

        st.error(
            "🌐 Unable to connect to Ollama Cloud. "
            "Please check your internet connection."
        )

    else:

        st.error("Something went wrong.")

        with st.expander("Technical error details"):
            st.code(message)


# =====================================================
# CHARACTER GENERATION
# =====================================================

def generate_character(details, model):

    prompt = f"""
You are a professional fictional character designer.

Create an original, detailed and interesting fictional character.

CHARACTER DETAILS:

Name: {details['name']}
Age: {details['age']}
Occupation: {details['occupation']}
Personality: {details['personality']}
Superpower: {details['power']}
Genre: {details['genre']}

Create a beautiful character profile using these sections:

# 🎭 Character Introduction
Introduce the character.

# 🧠 Personality
Describe their behaviour, habits and personality.

# 📖 Backstory
Create an interesting fictional history.

# 💪 Strengths
Describe their strongest qualities.

# 🌙 Weaknesses
Give the character believable limitations.

# 🎯 Goals and Motivation
Explain what they want to achieve.

# ✨ Special Abilities
Describe their abilities and limitations.

# ⚔️ Enemy or Rival
Create an interesting fictional rival.

# 💬 Famous Dialogue
Write one original memorable dialogue.

IMPORTANT:
- Respect all the details provided by the user.
- Make the character original.
- Keep the story engaging.
- Avoid graphic violence.
- Do not change the character's name or superpower.
"""

    return get_ai_response(
        model,
        [{"role": "user", "content": prompt}]
    )


# =====================================================
# CHARACTER CHAT
# =====================================================

def chat_with_character(character, history, user_message, model):

    system_prompt = f"""
You are roleplaying as a fictional character.

CHARACTER NAME: {character['name']}
AGE: {character['age']}
OCCUPATION: {character['occupation']}
PERSONALITY: {character['personality']}
SUPERPOWER: {character['power']}
WORLD: {character['genre']}

CHARACTER BACKGROUND:

{character['profile']}

YOUR ROLE:

1. Speak in this character's voice.
2. Maintain personality consistency.
3. Remember the character's fictional background.
4. Keep the conversation natural and engaging.
5. Do not randomly change abilities or history.
6. Respond directly to the user's messages.
7. Use expressions or short actions when appropriate.
8. Keep responses reasonably concise.
9. Keep the conversation friendly and age-appropriate.
10. Do not claim to be a real person.

You are playing a fictional role.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Include recent conversation for context
    messages.extend(history[-20:])

    messages.append({
        "role": "user",
        "content": user_message
    })

    return get_ai_response(model, messages)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("## 🎭 AI Character Studio")

st.sidebar.caption("Create • Imagine • Interact")

st.sidebar.markdown("---")

model = st.sidebar.text_input(
    "AI Cloud Model",
    value="gemma4:31b",
    help="Ollama Cloud API model name."
).strip()

if not model:
    model = "gemma4:31b"

st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Choose a section",
    [
        "✨ Create Character",
        "📚 My Characters",
        "💬 Character Chat"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    f"### 🎭 {len(st.session_state.characters)} Characters"
)

st.sidebar.caption("AI powered by Ollama Cloud")


# =====================================================
# HERO
# =====================================================

st.markdown("""
<div class="hero">

<h1>🎭 AI CHARACTER STUDIO</h1>

<p>
Create fictional worlds, design unforgettable characters
and bring them to life through AI conversations.
</p>

</div>
""", unsafe_allow_html=True)


# =====================================================
# PAGE 1: CREATE CHARACTER
# =====================================================

if page == "✨ Create Character":

    st.markdown("## ✨ Create Your Character")

    st.write(
        "Give your imagination a name, personality and special abilities."
    )

    with st.form("character_creation_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Character Name",
                placeholder="Example: Aria Storm"
            )

            age = st.number_input(
                "Character Age",
                min_value=1,
                max_value=150,
                value=21
            )

            occupation = st.text_input(
                "Occupation",
                placeholder="Warrior, Detective, Wizard..."
            )

        with col2:

            personality = st.text_input(
                "Personality",
                placeholder="Brave, intelligent, mysterious..."
            )

            power = st.text_input(
                "Superpower",
                placeholder="Fire, Ice, Teleportation..."
            )

            genre = st.selectbox(
                "World / Genre",
                [
                    "Fantasy",
                    "Sci-Fi",
                    "Superhero",
                    "Mystery",
                    "Horror",
                    "Adventure",
                    "Anime",
                    "Magical World",
                    "Post-Apocalyptic"
                ]
            )

        st.markdown("---")

        generate = st.form_submit_button(
            "✨ Generate My Character",
            use_container_width=True
        )

    if generate:

        if not all([
            name.strip(),
            occupation.strip(),
            personality.strip(),
            power.strip()
        ]):

            st.warning("⚠️ Please complete all character details.")

        else:

            details = {
                "name": name.strip(),
                "age": age,
                "occupation": occupation.strip(),
                "personality": personality.strip(),
                "power": power.strip(),
                "genre": genre
            }

            try:

                with st.spinner(
                    "🤖 AI is creating your character..."
                ):

                    profile = generate_character(details, model)

                character = {
                    "id": str(uuid.uuid4()),
                    **details,
                    "profile": profile
                }

                st.session_state.characters.append(character)

                st.session_state.chat_histories[character["id"]] = []

                st.session_state.selected_character = character["id"]

                st.session_state.generated_character = character["id"]

                st.success("🎉 Your character has been created!")

                st.rerun()

            except Exception as error:

                show_error(error)

    # Display latest character

    character_id = st.session_state.generated_character

    if character_id:

        character = next(
            (
                c for c in st.session_state.characters
                if c["id"] == character_id
            ),
            None
        )

        if character:

            st.markdown("---")

            st.markdown(f"## 🎭 {character['name']}")

            st.markdown(
                f"""
                <div class="character-card">

                <b>Age:</b> {character['age']}<br>
                <b>Occupation:</b> {html.escape(character['occupation'])}<br>
                <b>Personality:</b> {html.escape(character['personality'])}<br>
                <b>Power:</b> {html.escape(character['power'])}<br>
                <b>Genre:</b> {html.escape(character['genre'])}

                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### 📖 Character Profile")

            st.markdown(character["profile"])

            if st.button(
                "💬 Chat With This Character",
                use_container_width=True
            ):

                st.session_state.selected_character = character["id"]

                st.session_state.pending_chat = character["id"]

                st.rerun()


# =====================================================
# PAGE 2: CHARACTER GALLERY
# =====================================================

elif page == "📚 My Characters":

    st.markdown("## 📚 My Character Gallery")

    characters = st.session_state.characters

    if not characters:

        st.info(
            "You haven't created any characters yet. "
            "Visit Create Character to get started!"
        )

    else:

        selected_id = st.selectbox(
            "Select your character",
            options=[c["id"] for c in characters],
            format_func=lambda cid: next(
                c["name"] for c in characters if c["id"] == cid
            )
        )

        character = next(
            c for c in characters if c["id"] == selected_id
        )

        st.markdown("---")

        st.markdown(f"## 🎭 {character['name']}")

        st.markdown(
            f"""
            <div class="character-card">

            <h3>Character Information</h3>

            <b>Age:</b> {character['age']}<br>
            <b>Occupation:</b> {html.escape(character['occupation'])}<br>
            <b>Personality:</b> {html.escape(character['personality'])}<br>
            <b>Superpower:</b> {html.escape(character['power'])}<br>
            <b>World:</b> {html.escape(character['genre'])}

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 📖 Character Story")

        st.markdown(character["profile"])

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button("💬 Chat", use_container_width=True):

                st.session_state.selected_character = selected_id

                st.session_state.pending_chat = selected_id

                st.rerun()

        with col2:

            if st.button("🔄 Regenerate", use_container_width=True):

                details = {
                    key: character[key]
                    for key in [
                        "name",
                        "age",
                        "occupation",
                        "personality",
                        "power",
                        "genre"
                    ]
                }

                try:

                    with st.spinner(
                        "🤖 Creating a new character story..."
                    ):

                        new_profile = generate_character(details, model)

                    character["profile"] = new_profile

                    st.session_state.chat_histories[selected_id] = []

                    st.success("New character profile generated!")

                    st.rerun()

                except Exception as error:

                    show_error(error)

        with col3:

            if st.button("🗑️ Delete", use_container_width=True):

                st.session_state.characters = [
                    c for c in characters
                    if c["id"] != selected_id
                ]

                st.session_state.chat_histories.pop(
                    selected_id, None
                )

                if st.session_state.selected_character == selected_id:
                    st.session_state.selected_character = None

                if st.session_state.generated_character == selected_id:
                    st.session_state.generated_character = None

                st.success("Character deleted!")

                st.rerun()


# =====================================================
# PAGE 3: CHAT WITH CHARACTER
# =====================================================

elif page == "💬 Character Chat":

    st.markdown("## 💬 Talk With Your Character")

    characters = st.session_state.characters

    if not characters:

        st.warning(
            "Create a character first before starting a conversation."
        )

    else:

        character_ids = [c["id"] for c in characters]

        current_id = st.session_state.pending_chat

        if current_id not in character_ids:
            current_id = st.session_state.selected_character

        if current_id not in character_ids:
            current_id = character_ids[0]

        selected_id = st.selectbox(
            "Choose your character",
            options=character_ids,
            index=character_ids.index(current_id),
            format_func=lambda cid: next(
                c["name"] for c in characters if c["id"] == cid
            )
        )

        st.session_state.selected_character = selected_id
        st.session_state.pending_chat = None

        character = next(
            c for c in characters if c["id"] == selected_id
        )

        history = st.session_state.chat_histories.setdefault(
            selected_id, []
        )

        st.markdown(
            f"""
            <div class="character-card">

            <h3>🎭 {html.escape(character['name'])}</h3>

            <b>{html.escape(character['occupation'])}</b><br>

            {html.escape(character['personality'])}<br><br>

            <b>Special Power:</b>
            {html.escape(character['power'])}

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("### 💭 Conversation")

        with col2:

            if st.button("🧹 Clear Chat", use_container_width=True):

                st.session_state.chat_histories[selected_id] = []

                st.rerun()

        # Display previous conversation

        if not history:

            st.info(
                f"Start a conversation with {character['name']}!"
            )

            st.markdown(
                "**Try saying:** Hello! Tell me about your world."
            )

        else:

            for message in history:

                with st.chat_message(message["role"]):

                    st.markdown(message["content"])

        # Chat input

        user_message = st.chat_input(
            f"Message {character['name']}..."
        )

        if user_message:

            try:

                with st.spinner(
                    f"🎭 {character['name']} is thinking..."
                ):

                    reply = chat_with_character(
                        character,
                        history,
                        user_message,
                        model
                    )

                history.append({
                    "role": "user",
                    "content": user_message
                })

                history.append({
                    "role": "assistant",
                    "content": reply
                })

                st.rerun()

            except Exception as error:

                show_error(error)


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown("""
<div class="small-note">

🎭 <b>AI Character Studio</b>

<br><br>

Create • Imagine • Interact

<br>

Powered by Ollama Cloud & Streamlit

</div>
""", unsafe_allow_html=True)
