
import streamlit as st
import ollama
import uuid

# =====================================================
# PAGE CONFIGURATION
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

if "characters" not in st.session_state:
    st.session_state.characters = []

if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

if "selected_character" not in st.session_state:
    st.session_state.selected_character = None

if "generated_character" not in st.session_state:
    st.session_state.generated_character = None


# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #0b1020,
        #15132e,
        #211747
    );
    color: white;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

h1, h2, h3 {
    color: #ffffff !important;
}

p, label, span {
    color: #e5e7eb;
}

.hero {
    padding: 35px;
    text-align: center;
    border-radius: 25px;
    background: linear-gradient(
        120deg,
        rgba(124,58,237,0.28),
        rgba(37,99,235,0.20)
    );
    border: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 43px;
    font-weight: 800;
}

.hero p {
    color: #c4b5fd;
    font-size: 17px;
}

.section-card {
    background: rgba(255,255,255,0.06);
    padding: 24px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 20px;
}

.character-card {
    background: linear-gradient(
        135deg,
        rgba(124,58,237,0.20),
        rgba(37,99,235,0.13)
    );
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 20px;
    padding: 22px;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #17172e !important;
    color: white !important;
    border-radius: 12px !important;
}

.stButton button {
    border-radius: 12px;
    min-height: 45px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.15);
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    color: white;
}

.stButton button:hover {
    border-color: #c4b5fd;
    background: linear-gradient(90deg,#6d28d9,#4338ca);
}

[data-testid="stSidebar"] {
    background: #111127;
}

[data-testid="stChatMessage"] {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 15px;
}

hr {
    border-color: rgba(255,255,255,0.15);
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# OLLAMA FUNCTIONS
# =====================================================

def get_ai_response(model, messages):

    response = ollama.chat(
        model=model,
        messages=messages
    )

    return response["message"]["content"]


def check_ollama_error(error, model):

    error_text = str(error).lower()

    if "connection" in error_text or "connect" in error_text:
        st.error(
            "❌ Cannot connect to Ollama. "
            "Please start Ollama and try again."
        )

    elif "not found" in error_text or "pull" in error_text:
        st.error(
            f"❌ Model '{model}' is not available. "
            f"Run: ollama pull {model}"
        )

    else:
        st.error(f"Something went wrong: {error}")


# =====================================================
# CHARACTER GENERATION
# =====================================================

def generate_character(details, model):

    prompt = f"""
You are a professional fictional character designer.

Create a detailed, original and interesting fictional character.

CHARACTER DETAILS:

Name: {details['name']}
Age: {details['age']}
Occupation: {details['occupation']}
Personality: {details['personality']}
Superpower: {details['power']}
Genre: {details['genre']}

Write the character profile using these sections:

# 🎭 Character Introduction
Introduce the character in an engaging way.

# 🧠 Personality
Describe their personality, behaviour and habits.

# 📖 Backstory
Create an interesting fictional history.

# 💪 Strengths
Explain their strongest qualities.

# ⚡ Weaknesses
Give them believable limitations.

# 🎯 Goals and Motivation
Explain what they want to achieve.

# ✨ Special Abilities
Describe their powers and limitations.

# ⚔️ Enemy or Rival
Create an interesting fictional rival.

# 💬 Famous Dialogue
Write one original memorable dialogue.

Keep the profile creative, consistent and well-formatted.
Do not ignore the user's character details.
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
You are roleplaying as this fictional character.

CHARACTER PROFILE:

Name: {character['name']}
Age: {character['age']}
Occupation: {character['occupation']}
Personality: {character['personality']}
Superpower: {character['power']}
Genre: {character['genre']}

FULL CHARACTER BACKGROUND:

{character['profile']}

RULES:

1. Reply in the character's voice.
2. Stay consistent with the character's personality.
3. Remember the fictional world and background.
4. Do not randomly change your character's abilities.
5. Make conversations interesting and natural.
6. Never invent facts that contradict the profile.
7. You can use short actions or expressions where appropriate.
8. Keep replies reasonably concise.
9. If the user asks a question, answer naturally as the character.
10. Keep the conversation friendly and age-appropriate.

You are playing a fictional role. Do not claim to be a real person.
"""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": user_message
    })

    return get_ai_response(model, messages)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("## 🎭 Character Studio")

st.sidebar.markdown("---")

model = st.sidebar.text_input(
    "Ollama Model",
    value="llama3.2",
    help="Enter an installed Ollama model name."
).strip()

if not model:
    model = "llama3.2"

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "✨ Create Character",
        "📚 My Characters",
        "💬 Character Chat"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    f"### 🎭 {len(st.session_state.characters)} Characters"
)

st.sidebar.caption("Powered by Ollama + Streamlit")


# =====================================================
# MAIN HERO
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
        "Give your imagination a personality, identity and special powers."
    )

    with st.form("character_form"):

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
                    "Post-Apocalyptic",
                    "Magical World"
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
                    "🤖 AI is creating your fictional character..."
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

            except Exception as e:

                check_ollama_error(e, model)


    # Show newly generated character

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

            st.markdown(
                f"## 🎭 {character['name']}"
            )

            st.markdown(
                f"""
                <div class="character-card">
                <b>Age:</b> {character['age']}<br>
                <b>Occupation:</b> {character['occupation']}<br>
                <b>Personality:</b> {character['personality']}<br>
                <b>Power:</b> {character['power']}<br>
                <b>Genre:</b> {character['genre']}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### 📖 Character Profile")

            st.markdown(character["profile"])

            if st.button("💬 Chat With This Character"):

                st.session_state.selected_character = character["id"]

                st.session_state.open_chat = True

                st.rerun()


# =====================================================
# PAGE 2: MY CHARACTERS
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
            "Select a character",
            options=[c["id"] for c in characters],
            format_func=lambda cid: next(
                c["name"] for c in characters if c["id"] == cid
            ),
            key="gallery_selection"
        )

        character = next(
            c for c in characters if c["id"] == selected_id
        )

        st.markdown("---")

        st.markdown(
            f"## 🎭 {character['name']}"
        )

        st.markdown(
            f"""
            <div class="character-card">

            <h3>Character Information</h3>

            **Age:** {character['age']}

            **Occupation:** {character['occupation']}

            **Personality:** {character['personality']}

            **Superpower:** {character['power']}

            **World:** {character['genre']}

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

                st.session_state.open_chat = True

                st.rerun()

        with col2:

            if st.button("🔄 Regenerate", use_container_width=True):

                try:

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

                    with st.spinner("Creating a new version..."):

                        new_profile = generate_character(details, model)

                    character["profile"] = new_profile

                    st.session_state.chat_histories[selected_id] = []

                    st.success("Character profile regenerated!")

                    st.rerun()

                except Exception as e:

                    check_ollama_error(e, model)

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
# PAGE 3: CHARACTER CHAT
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

        current_id = st.session_state.selected_character

        if current_id not in character_ids:
            current_id = character_ids[0]

        selected_id = st.selectbox(
            "Choose your character",
            options=character_ids,
            index=character_ids.index(current_id),
            format_func=lambda cid: next(
                c["name"] for c in characters if c["id"] == cid
            ),
            key="chat_character_selection"
        )

        st.session_state.selected_character = selected_id

        character = next(
            c for c in characters if c["id"] == selected_id
        )

        history = st.session_state.chat_histories.setdefault(
            selected_id, []
        )

        st.markdown(
            f"""
            <div class="character-card">

            <h3>🎭 {character['name']}</h3>

            **{character['occupation']}**

            {character['personality']}

            <br>

            <b>Special Power:</b> {character['power']}

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

        # Display previous messages

        if not history:

            st.info(
                f"Start a conversation with {character['name']}!"
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

            history.append({
                "role": "user",
                "content": user_message
            })

            try:

                with st.spinner(
                    f"🎭 {character['name']} is thinking..."
                ):

                    reply = chat_with_character(
                        character,
                        history[:-1],
                        user_message,
                        model
                    )

                history.append({
                    "role": "assistant",
                    "content": reply
                })

                st.rerun()

            except Exception as e:

                # Remove the unanswered user message so it can be retried.
                history.pop()

                check_ollama_error(e, model)


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:15px; color:#a5b4fc;">

    🎭 <b>AI Character Studio</b>

    <br>

    Create • Imagine • Interact

    <br>

    <small>Powered by Ollama & Streamlit</small>

    </div>
    """,
    unsafe_allow_html=True
)
