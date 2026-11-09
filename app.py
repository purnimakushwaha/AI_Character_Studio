
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
    "navigation": "Create",
    "confirm_delete_id": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value


# =====================================================
# DESIGN
# =====================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 12% 8%, #30205c 0%, transparent 35%),
        radial-gradient(circle at 90% 85%, #172c60 0%, transparent 35%),
        linear-gradient(135deg, #090d1c, #15132e, #211747);
    color: #ffffff;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1150px;
    padding-top: 1.8rem;
    padding-bottom: 2.5rem;
}

h1, h2, h3 {
    color: #ffffff !important;
}

p, label {
    color: #e2e4f0;
}

[data-testid="stSidebar"] {
    background: #101127;
    border-right: 1px solid rgba(255,255,255,.08);
}

.hero {
    padding: 27px 25px;
    border-radius: 22px;
    text-align: center;
    margin-bottom: 28px;
    background: linear-gradient(
        120deg,
        rgba(124,58,237,.28),
        rgba(37,99,235,.20)
    );
    border: 1px solid rgba(255,255,255,.13);
}

.hero h1 {
    font-size: 38px;
    font-weight: 850;
    margin: 0;
    letter-spacing: -1px;
}

.hero p {
    color: #c4b5fd;
    font-size: 14px;
    margin: 7px 0 0;
}

.section-title {
    font-size: 23px;
    font-weight: 750;
    margin-bottom: 5px;
}

.character-card {
    padding: 20px;
    border-radius: 17px;
    background: linear-gradient(
        135deg,
        rgba(124,58,237,.19),
        rgba(37,99,235,.12)
    );
    border: 1px solid rgba(167,139,250,.25);
    margin: 12px 0 20px;
}

.character-meta {
    color: #c4b5fd;
    font-size: 13px;
    line-height: 1.9;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background: #17172e !important;
    color: white !important;
    border-radius: 11px !important;
}

div[data-baseweb="select"] {
    background: #17172e;
    border-radius: 11px;
}

.stButton button,
.stFormSubmitButton button {
    border-radius: 11px;
    min-height: 43px;
    font-weight: 650;
    border: 1px solid rgba(255,255,255,.12);
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    color: white;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    border-color: #c4b5fd;
    background: linear-gradient(90deg,#6d28d9,#4338ca);
}

[data-testid="stChatMessage"] {
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px;
    background: rgba(255,255,255,.035);
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,.025);
    padding: 20px;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 18px;
}

hr {
    border-color: rgba(255,255,255,.12);
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# OLLAMA CLOUD
# =====================================================

def get_ollama_client():

    api_key = st.secrets.get("OLLAMA_API_KEY", "")

    if not api_key:
        raise ValueError("OLLAMA_API_KEY is missing.")

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


def show_error(error):

    message = str(error).lower()

    if "401" in message or "unauthorized" in message:
        st.error("Ollama authentication failed. Check your API key.")

    elif "403" in message or "forbidden" in message:
        st.error("Access denied. Check your Ollama account and model access.")

    elif "404" in message or "not found" in message:
        st.error("The selected Ollama model could not be found.")

    elif "429" in message or "rate limit" in message:
        st.error("Usage limit reached. Please try again later.")

    elif "timeout" in message or "connection" in message:
        st.error("Unable to connect to Ollama Cloud. Please try again.")

    elif "api_key" in message or "missing" in message:
        st.error("Ollama API key is missing. Check Streamlit Secrets.")

    else:
        st.error("Something went wrong while contacting the AI service.")

        with st.expander("Technical details"):
            st.code(str(error))


# =====================================================
# CHARACTER GENERATION
# =====================================================

def generate_character(details, model):

    prompt = f"""
You are a creative fictional character designer.

Create an original and engaging fictional character.

CHARACTER DETAILS:
Name: {details['name']}
Age: {details['age']}
Occupation: {details['occupation']}
Personality: {details['personality']}
Superpower: {details['power']}
Genre: {details['genre']}

Write the character profile using these sections:

## Character Introduction
A short and interesting introduction.

## Personality
Describe their personality and behaviour.

## Backstory
Create an engaging fictional background.

## Strengths and Weaknesses
Describe both their strengths and limitations.

## Goals and Motivation
Explain what they want to achieve.

## Special Abilities
Describe their abilities and limitations.

## Rival
Create an interesting fictional rival.

## Famous Dialogue
Write one original memorable line.

IMPORTANT:
- Keep the character original.
- Respect the supplied details.
- Do not change the character's name or power.
- Keep content age-appropriate.
- Avoid graphic violence.
- Make the profile interesting but not unnecessarily long.
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
You are roleplaying as the fictional character below.

NAME: {character['name']}
AGE: {character['age']}
OCCUPATION: {character['occupation']}
PERSONALITY: {character['personality']}
SUPERPOWER: {character['power']}
WORLD: {character['genre']}

CHARACTER PROFILE:
{character['profile']}

RULES:
- Speak naturally in this character's voice.
- Stay consistent with the character's personality.
- Remember the fictional background.
- Do not randomly change abilities or history.
- Keep replies reasonably concise.
- Keep the conversation friendly and age-appropriate.
- You are playing a fictional role, not a real person.
"""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    messages.extend(history[-16:])

    messages.append({
        "role": "user",
        "content": user_message
    })

    return get_ai_response(model, messages)


# =====================================================
# NAVIGATION
# =====================================================

def open_character_chat(character_id):

    st.session_state.selected_character = character_id
    st.session_state.navigation = "Chat"


def delete_character(character_id):

    st.session_state.characters = [
        c for c in st.session_state.characters
        if c["id"] != character_id
    ]

    st.session_state.chat_histories.pop(character_id, None)

    if st.session_state.selected_character == character_id:
        st.session_state.selected_character = None

    if st.session_state.generated_character == character_id:
        st.session_state.generated_character = None

    st.session_state.confirm_delete_id = None


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("## 🎭 Character Studio")

st.sidebar.radio(
    "Navigation",
    ["Create", "Gallery", "Chat"],
    key="navigation",
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Keep model setting simple and out of the main interface.
model = st.secrets.get("OLLAMA_MODEL", "gemma4:31b").strip()

if not model:
    model = "gemma4:31b"


# =====================================================
# MAIN HEADER
# =====================================================

st.markdown("""
<div class="hero">
    <h1>🎭 AI Character Studio</h1>
    <p>Imagine a character. Create their story. Bring them to life.</p>
</div>
""", unsafe_allow_html=True)


# =====================================================
# PAGE 1: CREATE
# =====================================================

if st.session_state.navigation == "Create":

    st.markdown("## ✨ Create a Character")

    with st.form("character_creation_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Character Name",
                placeholder="e.g. Aria Storm"
            )

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=150,
                value=21
            )

            occupation = st.text_input(
                "Occupation",
                placeholder="Detective, Wizard, Explorer..."
            )

        with col2:

            personality = st.text_input(
                "Personality",
                placeholder="Brave, funny, intelligent..."
            )

            power = st.text_input(
                "Special Ability",
                placeholder="Teleportation, Ice, Healing..."
            )

            genre = st.selectbox(
                "World / Genre",
                [
                    "Fantasy",
                    "Sci-Fi",
                    "Superhero",
                    "Mystery",
                    "Adventure",
                    "Anime",
                    "Magical World",
                    "Horror",
                    "Post-Apocalyptic"
                ]
            )

        generate = st.form_submit_button(
            "✨ Create Character",
            use_container_width=True
        )

    if generate:

        if not all([
            name.strip(),
            occupation.strip(),
            personality.strip(),
            power.strip()
        ]):
            st.warning("Please fill in all character details.")

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

                with st.spinner("Creating your character..."):

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

                st.rerun()

            except Exception as error:
                show_error(error)

    # Show the most recently created character

    character_id = st.session_state.generated_character

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
                <div class="character-meta">
                    <b>Age:</b> {character['age']}
                    &nbsp; · &nbsp;
                    <b>Occupation:</b> {html.escape(character['occupation'])}
                    <br>
                    <b>Personality:</b> {html.escape(character['personality'])}
                    <br>
                    <b>Ability:</b> {html.escape(character['power'])}
                    &nbsp; · &nbsp;
                    <b>World:</b> {html.escape(character['genre'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(character["profile"])

        st.button(
            "💬 Chat with Character",
            use_container_width=True,
            on_click=open_character_chat,
            args=(character["id"],)
        )


# =====================================================
# PAGE 2: GALLERY
# =====================================================

elif st.session_state.navigation == "Gallery":

    st.markdown("## 📚 My Characters")

    characters = st.session_state.characters

    if not characters:

        st.info("Your character gallery is empty.")

        if st.button("✨ Create Your First Character"):
            st.session_state.navigation = "Create"
            st.rerun()

    else:

        selected_id = st.selectbox(
            "Select Character",
            options=[c["id"] for c in characters],
            index=0,
            format_func=lambda cid: next(
                c["name"] for c in characters if c["id"] == cid
            )
        )

        character = next(
            c for c in characters
            if c["id"] == selected_id
        )

        st.markdown("---")

        st.markdown(f"## 🎭 {character['name']}")

        st.markdown(
            f"""
            <div class="character-card">
                <div class="character-meta">
                    <b>Age:</b> {character['age']}
                    &nbsp; · &nbsp;
                    <b>Occupation:</b> {html.escape(character['occupation'])}
                    <br>
                    <b>Personality:</b> {html.escape(character['personality'])}
                    <br>
                    <b>Ability:</b> {html.escape(character['power'])}
                    &nbsp; · &nbsp;
                    <b>World:</b> {html.escape(character['genre'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(character["profile"])

        col1, col2, col3 = st.columns(3)

        with col1:

            st.button(
                "💬 Chat",
                use_container_width=True,
                on_click=open_character_chat,
                args=(selected_id,)
            )

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

                    with st.spinner("Creating a new story..."):

                        new_profile = generate_character(details, model)

                    character["profile"] = new_profile

                    st.rerun()

                except Exception as error:
                    show_error(error)

        with col3:

            if st.button("🗑️ Delete", use_container_width=True):
                st.session_state.confirm_delete_id = selected_id
                st.rerun()

        if st.session_state.confirm_delete_id == selected_id:

            st.warning(f"Delete {character['name']} permanently from this session?")

            yes, no = st.columns(2)

            with yes:

                if st.button("Confirm Delete", type="primary", use_container_width=True):
                    delete_character(selected_id)
                    st.rerun()

            with no:

                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_delete_id = None
                    st.rerun()


# =====================================================
# PAGE 3: CHAT
# =====================================================

elif st.session_state.navigation == "Chat":

    st.markdown("## 💬 Character Chat")

    characters = st.session_state.characters

    if not characters:

        st.info("Create a character before starting a conversation.")

        if st.button("✨ Create Character"):
            st.session_state.navigation = "Create"
            st.rerun()

    else:

        character_ids = [c["id"] for c in characters]

        current_id = st.session_state.selected_character

        if current_id not in character_ids:
            current_id = character_ids[0]

        selected_id = st.selectbox(
            "Chat with",
            options=character_ids,
            index=character_ids.index(current_id),
            format_func=lambda cid: next(
                c["name"] for c in characters if c["id"] == cid
            )
        )

        st.session_state.selected_character = selected_id

        character = next(
            c for c in characters
            if c["id"] == selected_id
        )

        history = st.session_state.chat_histories.setdefault(
            selected_id, []
        )

        st.markdown(
            f"""
            <div class="character-card">
                <h3>🎭 {html.escape(character['name'])}</h3>
                <div class="character-meta">
                    {html.escape(character['occupation'])}
                    &nbsp; · &nbsp;
                    {html.escape(character['genre'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown("### Conversation")

        with col2:

            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_histories[selected_id] = []
                st.rerun()

        if not history:

            st.caption(f"Start a conversation with {character['name']}.")

        else:

            for message in history:

                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_message = st.chat_input(
            f"Message {character['name']}..."
        )

        if user_message:

            try:

                with st.spinner(f"{character['name']} is thinking..."):

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
