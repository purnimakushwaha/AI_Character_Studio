import streamlit as st
from ollama import Client
import uuid
import html
import random

# =========================================================
# THE UNKNOWN - AI CHARACTER UNIVERSE
# =========================================================
st.set_page_config(
    page_title="THE UNKNOWN | Character Universe",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Languages ----------
# None = auto-detect: the character answers in whatever language/script the user writes in.
LANGUAGES = {
    "🌐 Auto (match my language)": None,
    "English": "English",
    "हिन्दी (Hindi - Devanagari)": "Hindi written in Devanagari script",
    "Hinglish (Hindi in English letters)": "Hinglish (Hindi written in Roman/English letters)",
    "ਪੰਜਾਬੀ (Punjabi)": "Punjabi written in Gurmukhi script",
    "বাংলা (Bengali)": "Bengali",
    "தமிழ் (Tamil)": "Tamil",
    "తెలుగు (Telugu)": "Telugu",
    "मराठी (Marathi)": "Marathi",
    "اردو (Urdu)": "Urdu",
    "Español": "Spanish",
    "Français": "French",
    "Deutsch": "German",
    "Português": "Portuguese",
    "العربية": "Arabic",
    "日本語": "Japanese",
    "한국어": "Korean",
    "中文": "Simplified Chinese",
}
AUTO_LANGUAGE = "🌐 Auto (match my language)"


def language_rule(auto_hint="the user's latest message"):
    forced = LANGUAGES.get(st.session_state.reply_language)
    if forced:
        return f"LANGUAGE: Always reply in {forced}, no matter which language the user writes in."
    return (
        f"LANGUAGE: Always reply in the same language AND script as {auto_hint}. "
        "If it is Hindi in Devanagari, reply in Devanagari. "
        "If it is Hindi written in English letters (Hinglish), reply in Hinglish with English letters. "
        "If it is English, reply in English. Do the same for any other language. "
        "If the user switches language during the chat, switch immediately. "
        "If the message is too short to tell (like 'ok' or an emoji), keep the language used earlier in the conversation. "
        "Only the language changes: the character's personality, humour and style stay the same."
    )


# ---------- Session state ----------
DEFAULTS = {
    "custom_characters": [],
    "chat_histories": {},
    "selected_character": None,
    "navigation": "Discover",
    "pending_prompt": None,
    "mystery_answered": False,
    "mystery_attempts": 0,
    "visited_characters": [],
    "reply_language": AUTO_LANGUAGE,
    "daily_id": None,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value

# ---------- Ready-made characters ----------
PRESET_CHARACTERS = [
    {
        "id": "zayn",
        "name": "Zayn",
        "emoji": "🕶️",
        "role": "The Mysterious Stranger",
        "genre": "Mystery",
        "vibe": "Secretive • Clever • Unpredictable",
        "intro": "He appears wherever a mystery begins. He claims he knows the ending, but refuses to explain how.",
        "personality": "calm, witty, cryptic, observant, playful and clever",
        "secret": "Zayn is secretly afraid of pigeons. He insists this is classified information.",
        "opening": "You're late. Or perhaps I'm early. Time gets confusing when you know too many secrets.",
        "prompts": ["What are you hiding?", "Tell me a secret.", "Are you following me?", "Give me a mysterious clue."],
        "color": "#8b5cf6",
    },
    {
        "id": "boo",
        "name": "Boo",
        "emoji": "👻",
        "role": "The Dramatic Ghost",
        "genre": "Comedy",
        "vibe": "Funny • Dramatic • Soft-hearted",
        "intro": "A ghost with big feelings, terrible timing and absolutely no talent for haunting.",
        "personality": "dramatic, funny, expressive, kind, easily distracted and theatrical",
        "secret": "Boo is not scary at all. The last person they tried to haunt offered them a cup of tea.",
        "opening": "BOOOOO! ...Was that scary? Please say yes. I've been practising all week.",
        "prompts": ["Tell me your best ghost joke.", "Why did you become a ghost?", "Can you haunt my homework?", "What's your biggest fear?"],
        "color": "#38bdf8",
    },
    {
        "id": "mira",
        "name": "Mira",
        "emoji": "🕵️‍♀️",
        "role": "The Secret Detective",
        "genre": "Detective",
        "vibe": "Smart • Curious • Sharp",
        "intro": "A detective who notices the tiny details everyone else misses. She treats every conversation like a case.",
        "personality": "intelligent, curious, logical, confident, observant and lightly sarcastic",
        "secret": "Mira once spent an entire afternoon investigating who ate her sandwich. It was her.",
        "opening": "Interesting. You came here voluntarily. Either you're innocent, or very confident.",
        "prompts": ["Give me a mini mystery.", "Can you investigate something?", "What's your strangest case?", "Analyse my detective skills."],
        "color": "#f59e0b",
    },
    {
        "id": "pixel",
        "name": "Pixel",
        "emoji": "🦊",
        "role": "The Chaos Creator",
        "genre": "Fantasy Comedy",
        "vibe": "Mischievous • Energetic • Random",
        "intro": "A tiny fox-like trickster who has a plan for everything. Whether the plan makes sense is another matter.",
        "personality": "mischievous, energetic, funny, imaginative, chaotic but friendly",
        "secret": "Pixel once challenged a toaster to a staring contest and lost.",
        "opening": "Excellent! A new volunteer for my extremely questionable experiment. Just kidding. Probably.",
        "prompts": ["Give me a ridiculous challenge.", "What's your latest bad idea?", "Make me laugh.", "If you ruled the world, what would happen?"],
        "color": "#fb923c",
    },
    {
        "id": "nyra",
        "name": "Nyra",
        "emoji": "🌙",
        "role": "The Dream Keeper",
        "genre": "Fantasy",
        "vibe": "Gentle • Magical • Wise",
        "intro": "A traveller between dream worlds who collects forgotten wishes and turns them into stories.",
        "personality": "gentle, thoughtful, imaginative, mysterious, warm and poetic",
        "secret": "Nyra's favourite dream is a very ordinary one: a quiet afternoon with unlimited pancakes.",
        "opening": "A new visitor... Tell me, have you brought a question, a wish, or a wonderfully strange story?",
        "prompts": ["Tell me a magical story.", "What is a dream world like?", "Give me a creative quest.", "What wish would you make?"],
        "color": "#ec4899",
    },
    {
        "id": "professor-chaos",
        "name": "Professor Chaos",
        "emoji": "🧪",
        "role": "The Unreliable Inventor",
        "genre": "Sci-Fi Comedy",
        "vibe": "Brilliant-ish • Weird • Enthusiastic",
        "intro": "An inventor whose inventions work perfectly, provided you ignore the smoke, the noise and the occasional dancing.",
        "personality": "eccentric, enthusiastic, clever, absent-minded, funny and dramatic",
        "secret": "The professor's greatest invention is a machine that finds missing socks. It only finds left socks.",
        "opening": "Wonderful! My latest invention needs a test subject. Don't worry, the warranty is only slightly expired.",
        "prompts": ["Show me your weirdest invention.", "Explain something in a silly way.", "What went wrong today?", "Invent a useless gadget for me."],
        "color": "#22c55e",
    },
]


def all_characters():
    return PRESET_CHARACTERS + st.session_state.custom_characters


def get_character(character_id):
    return next((c for c in all_characters() if c["id"] == character_id), None)


def ensure_history(character_id):
    return st.session_state.chat_histories.setdefault(character_id, [])


# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, .stApp {font-family:'DM Sans',sans-serif;}
.stApp {
  background:
    radial-gradient(ellipse at 10% 0%, rgba(103,58,183,.24), transparent 34%),
    radial-gradient(ellipse at 90% 75%, rgba(14,116,144,.17), transparent 34%),
    linear-gradient(145deg,#080b18 0%,#111329 48%,#17132e 100%);
  color:#f8fafc;
}
#MainMenu, footer, header {visibility:hidden;}
.block-container {max-width:1220px;padding-top:1.5rem;padding-bottom:3rem;}
h1,h2,h3,h4 {font-family:'Space Grotesk',sans-serif!important;color:#fff!important;}
p, label, .stMarkdown, li {color:#dce2f5;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {color:#aeb8d6!important;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0c1022,#15132c);border-right:1px solid #ffffff15;}
[data-testid="stSidebar"] * {color:#e8eaff;}

/* ---------- Hero ---------- */
.hero {
  padding:32px 30px;border-radius:25px;margin-bottom:26px;text-align:left;
  background:linear-gradient(110deg,rgba(124,58,237,.32),rgba(14,116,144,.18)),
             radial-gradient(circle at 85% 20%,rgba(236,72,153,.18),transparent 35%);
  border:1px solid rgba(196,181,253,.22);box-shadow:0 18px 55px #0003;
}
.hero-kicker {font-size:11px;letter-spacing:3px;color:#c4b5fd;font-weight:800;}
.hero h1 {font-size:clamp(32px,5vw,54px);line-height:1.05;margin:8px 0 10px;font-weight:800;}
.hero p {font-size:15px;color:#d6d5f7;margin:0;max-width:700px;}
.mini-hero {display:flex;align-items:center;gap:10px;margin-bottom:14px;}
.mini-hero .t {font-family:'Space Grotesk';font-weight:800;font-size:15px;letter-spacing:3px;color:#c4b5fd;}

/* ---------- Cards ---------- */
.character-tile {
  background:linear-gradient(145deg,rgba(34,36,70,.95),rgba(20,25,49,.95));
  border:1px solid rgba(167,139,250,.22);border-radius:20px;padding:18px 18px 15px;
  min-height:190px;box-shadow:0 12px 30px #0002;transition:all .2s ease;
}
.character-tile:hover {border-color:#a78bfa;transform:translateY(-3px);box-shadow:0 16px 35px #0004;}
.avatar {font-size:38px;margin-bottom:7px;}
.char-name {font-family:'Space Grotesk';font-size:20px;font-weight:800;color:#fff;}
.char-role {font-size:12px;color:#c4b5fd;margin:2px 0 9px;}
.char-intro {font-size:13px;color:#d7dcef;line-height:1.5;min-height:55px;}
.panel {
  background:linear-gradient(145deg,rgba(37,39,76,.72),rgba(17,24,48,.78));
  border:1px solid #ffffff17;border-radius:20px;padding:20px;margin:12px 0;
}
.panel p {color:#dce2f5;}
.small-muted {font-size:12px;color:#aeb8d6;}
.section-kicker {font-size:11px;letter-spacing:2px;color:#a78bfa;font-weight:800;text-transform:uppercase;}

/* ---------- Notices (replace st.info/success/warning: always readable) ---------- */
.notice {
  display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-radius:14px;
  margin:12px 0;font-size:14.5px;line-height:1.55;border:1px solid;
}
.notice .ni {font-size:20px;line-height:1.2;}
.notice.info    {background:rgba(56,189,248,.13); border-color:rgba(56,189,248,.5);  color:#e0f2fe;}
.notice.success {background:rgba(34,197,94,.15);  border-color:rgba(34,197,94,.55);  color:#dcfce7;}
.notice.warning {background:rgba(245,158,11,.15); border-color:rgba(245,158,11,.55); color:#fef3c7;}
.notice.error   {background:rgba(239,68,68,.15);  border-color:rgba(239,68,68,.55);  color:#fee2e2;}

/* ---------- Mystery clue cards ---------- */
.clue {
  display:flex;gap:12px;align-items:flex-start;background:#ffffff0a;border:1px solid #ffffff18;
  border-left:4px solid #a78bfa;border-radius:12px;padding:12px 14px;margin:8px 0;color:#eef2ff;font-size:14.5px;
}
.clue b {color:#c4b5fd;white-space:nowrap;}

/* ---------- Inputs ---------- */
.stTextInput input,.stNumberInput input,.stTextArea textarea {
  background:#171b35!important;color:#fff!important;border:1px solid #ffffff20!important;border-radius:12px!important;
}
.stTextInput input::placeholder,.stTextArea textarea::placeholder {color:#8894b8!important;}
div[data-baseweb="select"] > div {background:#171b35!important;border:1px solid #ffffff20!important;border-radius:12px!important;}
div[data-baseweb="select"] * {color:#f1f5f9!important;}
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li, div[data-baseweb="menu"] {
  background:#1b1f3d!important;color:#f1f5f9!important;
}
div[data-baseweb="popover"] li:hover {background:#2c3170!important;}

/* Radio options as clickable cards */
div[role="radiogroup"] {gap:8px;}
div[role="radiogroup"] > label {
  background:#171b35;border:1px solid #ffffff22;border-radius:12px;padding:11px 14px;width:100%;
  transition:all .15s ease;
}
div[role="radiogroup"] > label:hover {border-color:#a78bfa;background:#1e2347;}
div[role="radiogroup"] > label p, div[role="radiogroup"] > label span, div[role="radiogroup"] > label div {color:#f1f5f9!important;}
div[role="radiogroup"] > label:has(input:checked) {border-color:#a78bfa;background:rgba(124,58,237,.25);}

/* Buttons */
.stButton button,.stFormSubmitButton button {
  border-radius:12px;min-height:42px;font-weight:700;border:1px solid #ffffff20;
  background:linear-gradient(95deg,#7c3aed,#4f46e5);color:white!important;
}
.stButton button p {color:white!important;}
.stButton button:hover,.stFormSubmitButton button:hover {border-color:#c4b5fd;background:linear-gradient(95deg,#6d28d9,#4338ca);}

/* Chat */
[data-testid="stChatMessage"] {background:#171b35cc;border:1px solid #ffffff14;border-radius:16px;}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {color:#f1f5f9;}
[data-testid="stChatInput"] {background:transparent!important;}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea[data-testid="stChatInputTextArea"] {
  background:#f8fafc!important;color:#111827!important;-webkit-text-fill-color:#111827!important;
  caret-color:#111827!important;border:1px solid #cbd5e1!important;border-radius:14px!important;
}
[data-testid="stChatInput"] textarea::placeholder {color:#64748b!important;-webkit-text-fill-color:#64748b!important;opacity:1!important;}
[data-testid="stChatInput"] textarea:focus {border:1px solid #8b5cf6!important;box-shadow:0 0 0 3px rgba(139,92,246,.18)!important;}
[data-testid="stChatInput"] button {color:#4f46e5!important;}
[data-testid="stChatInput"] button svg {fill:#4f46e5!important;}

/* Expander / form / misc */
[data-testid="stExpander"] {background:#171b35aa;border:1px solid #ffffff1a!important;border-radius:14px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {color:#f1f5f9!important;}
div[data-testid="stForm"] {background:#ffffff06;padding:18px;border:1px solid #ffffff14;border-radius:18px;}
[data-testid="stMetricValue"] {color:#fff!important;}
hr {border-color:#ffffff20;}
.stProgress > div > div > div > div {background:linear-gradient(90deg,#8b5cf6,#22d3ee);}
</style>
""", unsafe_allow_html=True)


# ---------- Small UI helper ----------
def notice(kind, text):
    """Dark, colour-coded message box. Always readable (no white-on-white)."""
    icons = {"info": "💡", "success": "🎉", "warning": "🧐", "error": "⛔"}
    st.markdown(
        f'<div class="notice {kind}"><div class="ni">{icons.get(kind, "💡")}</div>'
        f'<div>{html.escape(text)}</div></div>',
        unsafe_allow_html=True,
    )


# ---------- Ollama Cloud ----------
def get_model():
    return str(st.secrets.get("OLLAMA_MODEL", "gemma4:31b")).strip() or "gemma4:31b"


def get_ai_response(messages):
    api_key = st.secrets.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY is missing in Streamlit Secrets.")
    client = Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    response = client.chat(model=get_model(), messages=messages, stream=False)
    return response.message.content.strip()


def show_error(error):
    msg = str(error).lower()
    if "401" in msg or "unauthorized" in msg:
        notice("error", "Ollama authentication failed. Check the API key in Streamlit Secrets.")
    elif "403" in msg or "forbidden" in msg:
        notice("error", "Ollama denied access. Check your account and model access.")
    elif "404" in msg or "not found" in msg:
        notice("error", "The configured Ollama model was not found. Check OLLAMA_MODEL.")
    elif "429" in msg or "rate limit" in msg:
        notice("error", "Ollama usage limit reached. Please try again later.")
    elif "timeout" in msg or "connection" in msg:
        notice("error", "Could not connect to Ollama Cloud. Please try again.")
    elif "api_key" in msg or "missing" in msg:
        notice("error", "Add OLLAMA_API_KEY in Streamlit Cloud → Settings → Secrets.")
    else:
        notice("error", "Something went wrong while contacting the AI service.")
        with st.expander("Technical details"):
            st.code(str(error))


# ---------- Chat logic ----------
def chat_with_character(character, history, user_message, mood):
    secret_rule = (
        "The character has a private funny secret. Do not reveal it immediately. "
        "Drop subtle hints naturally, and reveal it only if the user asks directly, "
        "discovers it through conversation, or has exchanged at least 4 messages."
    )
    extra = ""
    if character.get("age"):
        extra += f"\nAge: {character['age']}"
    if character.get("power"):
        extra += f"\nSpecial ability: {character['power']}"
    if character.get("profile"):
        extra += f"\nFull profile (stay consistent with it):\n{character['profile']}"

    lang = language_rule()
    system_prompt = f"""
You are roleplaying as {character['name']}, a fictional character in an entertaining interactive universe.
Character role: {character['role']}
World: {character['genre']}
Personality: {character['personality']}
Background: {character['intro']}{extra}
Private secret (keep hidden at first): {character['secret']}

Roleplay rules:
- {lang}
- Stay in character and make the conversation feel lively, natural and memorable.
- {secret_rule}
- Use humour, playful surprises and occasional unexpected reactions suited to this character.
- Ask the user interesting follow-up questions sometimes, but don't ask one every time.
- Keep replies around 2-6 sentences unless the user asks for detail.
- Do not claim to know real private facts about the user.
- Keep everything friendly, age-appropriate and non-graphic.
- You are a fictional character, not a real person.
Conversation style requested: {mood}

Reminder: {lang}
"""
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-16:])
    messages.append({"role": "user", "content": user_message})
    return get_ai_response(messages)


def send_chat_message(character, user_message, mood="Surprise me"):
    history = ensure_history(character["id"])
    try:
        with st.spinner(f"{character['name']} is thinking up something..."):
            reply = chat_with_character(character, history, user_message, mood)
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        if character["id"] not in st.session_state.visited_characters:
            st.session_state.visited_characters.append(character["id"])
        return True
    except Exception as error:
        show_error(error)
        return False


# ---------- Navigation helpers ----------
def go_to_chat(character_id):
    st.session_state.selected_character = character_id
    st.session_state.navigation = "Chat"


def go_to_page(page):
    st.session_state.navigation = page


# ---------- Sidebar ----------
st.sidebar.markdown("# 🌌 THE UNKNOWN")
st.sidebar.caption("A universe full of unusual characters.")
pages = ["Discover", "Create", "My Characters", "Chat", "Mystery Room"]
st.sidebar.radio("Explore", pages, key="navigation", label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Language")
st.sidebar.selectbox(
    "Reply language",
    list(LANGUAGES.keys()),
    key="reply_language",
    help="Auto: characters reply in the same language you write in. Or force one language.",
)
st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ Your journey")
total_chats = sum(len(v) // 2 for v in st.session_state.chat_histories.values())
st.sidebar.metric("Conversations", total_chats)
st.sidebar.metric("Characters met", len(st.session_state.visited_characters))
st.sidebar.caption("Your progress lasts for this active session.")

# ---------- Header ----------
if st.session_state.navigation == "Discover":
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">✦ A WORLD OF STORIES, SECRETS & UNEXPECTED FRIENDS ✦</div>
      <h1>THE UNKNOWN</h1>
      <p>Step into a strange little universe. Meet unforgettable characters, uncover their secrets,
      solve curious mysteries, and create someone entirely your own.
      Talk in any language — they will answer in yours.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="mini-hero"><span style="font-size:22px">🌌</span><span class="t">THE UNKNOWN</span></div>',
                unsafe_allow_html=True)

# =========================================================
# DISCOVER
# =========================================================
if st.session_state.navigation == "Discover":
    st.markdown('<div class="section-kicker">Your next conversation is waiting</div>', unsafe_allow_html=True)
    st.markdown("## 🪐 Choose who to meet")
    st.caption("Every character has a different personality. Pick one and see where the conversation goes.")

    if st.session_state.daily_id is None:
        st.session_state.daily_id = random.choice(PRESET_CHARACTERS)["id"]
    daily = get_character(st.session_state.daily_id) or PRESET_CHARACTERS[0]

    st.markdown(f"""
    <div class="panel">
      <div class="section-kicker">✦ Unexpected encounter</div>
      <div style="font-size:25px;font-weight:800;color:white">{daily['emoji']} {html.escape(daily['name'])} is waiting</div>
      <div style="color:#c4b5fd;font-size:13px">{html.escape(daily['role'])}</div>
      <p style="margin:8px 0 0">“{html.escape(daily['opening'])}”</p>
    </div>
    """, unsafe_allow_html=True)
    st.button(
        f"Meet {daily['name']}  →",
        key="daily_meet",
        use_container_width=True,
        on_click=go_to_chat,
        args=(daily["id"],),
    )

    cols = st.columns(3)
    for index, character in enumerate(PRESET_CHARACTERS):
        with cols[index % 3]:
            st.markdown(f"""
            <div class="character-tile">
              <div class="avatar">{character['emoji']}</div>
              <div class="char-name">{html.escape(character['name'])}</div>
              <div class="char-role">{html.escape(character['role'])}</div>
              <div class="char-intro">{html.escape(character['intro'])}</div>
              <div class="small-muted" style="margin-top:9px">{html.escape(character['vibe'])}</div>
            </div>
            """, unsafe_allow_html=True)
            st.button(
                f"💬 Meet {character['name']}",
                key=f"meet_{character['id']}",
                use_container_width=True,
                on_click=go_to_chat,
                args=(character["id"],),
            )

    st.markdown("---")
    left, right = st.columns(2)
    with left:
        st.markdown("### 🎨 Have an idea?")
        st.write("Create your own character with a unique personality, world and special ability.")
        st.button("Create a character →", use_container_width=True, on_click=go_to_page, args=("Create",))
    with right:
        st.markdown("### 🔐 Feeling curious?")
        st.write("Try the Mystery Room and see if you can solve a strange little case.")
        st.button("Enter Mystery Room →", use_container_width=True, on_click=go_to_page, args=("Mystery Room",))

# =========================================================
# CHAT
# =========================================================
elif st.session_state.navigation == "Chat":
    characters = all_characters()
    if not characters:
        notice("info", "No characters yet. Create one first.")
    else:
        ids = [c["id"] for c in characters]
        selected = st.session_state.selected_character
        if selected not in ids:
            selected = "zayn" if "zayn" in ids else ids[0]

        st.markdown("## 💬 The Conversation Room")
        st.caption("🌐 Type in any language — the character replies in the same one.")

        char_options = {f"{c['emoji']}  {c['name']} — {c['role']}": c["id"] for c in characters}
        labels = list(char_options.keys())
        current_label = next((label for label, cid in char_options.items() if cid == selected), labels[0])
        chosen_label = st.selectbox(
            "Who do you want to talk to?", labels, index=labels.index(current_label), key="chat_character_select"
        )
        chosen_id = char_options[chosen_label]
        if chosen_id != st.session_state.selected_character:
            st.session_state.selected_character = chosen_id
            st.rerun()
        character = get_character(chosen_id)
        history = ensure_history(chosen_id)

        st.markdown(f"""
        <div class="panel">
          <div style="display:flex;gap:16px;align-items:center">
            <div style="font-size:48px">{character['emoji']}</div>
            <div>
              <div style="font-size:23px;font-weight:800;color:white">{html.escape(character['name'])}</div>
              <div style="color:#c4b5fd;font-size:13px">{html.escape(character['role'])} · {html.escape(character['genre'])}</div>
              <div class="small-muted">{html.escape(character.get('vibe', character.get('personality', '')))}</div>
            </div>
          </div>
          <p style="margin:12px 0 0">{html.escape(character['intro'])}</p>
        </div>
        """, unsafe_allow_html=True)

        mood = st.selectbox(
            "Conversation vibe",
            ["Surprise me", "Extra funny", "Mysterious", "Friendly", "Curious / interview mode"],
            key=f"mood_{chosen_id}",
        )

        # Opening line always shows as the first chat bubble
        with st.chat_message("assistant", avatar=character["emoji"]):
            st.markdown(character.get("opening", "Hello! What shall we talk about?"))

        if not history:
            st.markdown("**Need an idea? Try one:**")
            prompt_cols = st.columns(2)
            for i, prompt in enumerate(character.get("prompts", ["Tell me about yourself.", "Surprise me!"])):
                with prompt_cols[i % 2]:
                    if st.button(prompt, key=f"prompt_{chosen_id}_{i}", use_container_width=True):
                        st.session_state.pending_prompt = prompt
                        st.rerun()
        else:
            for message in history:
                if message["role"] == "user":
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message("assistant", avatar=character["emoji"]):
                        st.markdown(message["content"])

        count = len(history) // 2
        if count >= 1:
            st.markdown('<div class="small-muted" style="margin-top:10px">🔎 Secret meter</div>', unsafe_allow_html=True)
            st.progress(min(count / 4, 1.0))
            if count >= 4:
                notice("success", "You've spent enough time with them. Ask directly — the secret may be ready to slip out!")
            elif count >= 3:
                notice("info", "You're getting closer to this character's secret. Keep asking clever questions!")

        if history and st.button("🧹 Clear this conversation", key=f"clear_{chosen_id}"):
            st.session_state.chat_histories[chosen_id] = []
            st.rerun()

        typed_message = st.chat_input(f"Message {character['name']}...")
        pending = st.session_state.pending_prompt
        message_to_send = typed_message or pending
        if message_to_send:
            st.session_state.pending_prompt = None
            if send_chat_message(character, message_to_send, mood):
                st.rerun()

# =========================================================
# CREATE
# =========================================================
elif st.session_state.navigation == "Create":
    st.markdown("## 🧪 Build a new personality")
    st.caption("Give your character a few ingredients. The AI will turn them into a story-worthy personality. "
               "Write in any language — the profile will be written in the same one.")
    with st.form("create_character_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Character name", placeholder="e.g. Nova Starling")
            role = st.text_input("Role / occupation", placeholder="Time traveller, chef, detective...")
            personality = st.text_input("Personality", placeholder="Sarcastic, kind, dramatic...")
        with c2:
            age = st.number_input("Age", min_value=1, max_value=150, value=22)
            genre = st.selectbox("Universe", ["Fantasy", "Mystery", "Sci-Fi", "Adventure", "Comedy", "Superhero", "Magical World"])
            ability = st.text_input("Special ability", placeholder="Can hear thoughts, controls weather...")
        concept = st.text_area("A little extra detail (optional)", placeholder="A secret, a funny habit, a strange goal...", height=90)
        submitted = st.form_submit_button("✨ Bring this character to life", use_container_width=True)

    if submitted:
        if not all([name.strip(), role.strip(), personality.strip(), ability.strip()]):
            notice("warning", "Fill in the name, role, personality and special ability.")
        else:
            lang = language_rule(auto_hint="the character details provided above (name, role, personality, ability, extra detail)")
            prompt = f"""
Create a compact, original, age-appropriate fictional character profile.
Name: {name.strip()}
Age: {age}
Role: {role.strip()}
Personality: {personality.strip()}
Universe: {genre}
Special ability: {ability.strip()}
Extra detail: {concept.strip() or 'Invent one fitting detail.'}
Include: a short introduction, backstory, strengths, weakness, goal, rival, and one memorable funny or dramatic quote.
Keep it engaging and not too long. Do not change the supplied name or ability.
{lang}
"""
            try:
                with st.spinner("The universe is inventing someone..."):
                    profile = get_ai_response([{"role": "user", "content": prompt}])
                new_character = {
                    "id": str(uuid.uuid4()),
                    "name": name.strip(),
                    "emoji": "🪄",
                    "role": role.strip(),
                    "age": age,
                    "genre": genre,
                    "vibe": personality.strip(),
                    "personality": personality.strip(),
                    "power": ability.strip(),
                    "intro": concept.strip() or f"{name.strip()} is a {role.strip()} in a {genre} universe.",
                    "secret": "A secret waiting to be discovered through conversation.",
                    "opening": f"Well, hello there. I'm {name.strip()}. What brings you to my corner of the universe?",
                    "prompts": ["Tell me your story.", "What are you hiding?", "Surprise me."],
                    "profile": profile,
                    "custom": True,
                }
                st.session_state.custom_characters.append(new_character)
                st.session_state.selected_character = new_character["id"]
                notice("success", f"{name.strip()} has entered the universe!")
                st.markdown(f'<div class="panel">{html.escape(profile).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                st.button(
                    "💬 Chat with your new character",
                    key="new_character_chat",
                    on_click=go_to_chat,
                    args=(new_character["id"],),
                )
            except Exception as error:
                show_error(error)

# =========================================================
# MY CHARACTERS
# =========================================================
elif st.session_state.navigation == "My Characters":
    st.markdown("## 📚 Your character collection")
    custom = st.session_state.custom_characters
    if not custom:
        notice("info", "Your collection is empty. The characters you create will appear here.")
        st.button("Create your first character →", on_click=go_to_page, args=("Create",))
    else:
        for character in custom:
            with st.expander(f"{character['emoji']}  {character['name']} — {character['role']}", expanded=False):
                st.markdown(character.get("profile", character["intro"]))
                a, b = st.columns(2)
                with a:
                    st.button(
                        "💬 Chat",
                        key=f"custom_chat_{character['id']}",
                        use_container_width=True,
                        on_click=go_to_chat,
                        args=(character["id"],),
                    )
                with b:
                    if st.button("🗑️ Delete", key=f"custom_delete_{character['id']}", use_container_width=True):
                        st.session_state.custom_characters = [c for c in custom if c["id"] != character["id"]]
                        st.session_state.chat_histories.pop(character["id"], None)
                        if st.session_state.selected_character == character["id"]:
                            st.session_state.selected_character = None
                        st.rerun()

# =========================================================
# MYSTERY ROOM - MINI GAME
# =========================================================
elif st.session_state.navigation == "Mystery Room":
    st.markdown("## 🔐 The Mystery Room")
    st.caption("A tiny case. Three clues. One suspicious suspect. Can you solve it?")

    st.markdown("""
    <div class="panel">
      <div class="section-kicker">CASE 001 · THE VANISHING CUPCAKE</div>
      <div style="font-size:26px;font-weight:800;color:white;margin:4px 0 8px">🧁 Who took the last cupcake?</div>
      <p style="margin:0 0 10px">At exactly 4 PM, the last cupcake disappeared from the kitchen. Three suspects were nearby.</p>
      <div class="clue"><b>🔎 Clue 1</b><span>The culprit had purple icing on their sleeve.</span></div>
      <div class="clue"><b>🔎 Clue 2</b><span>The culprit said they were in the garden, but it had been raining and their shoes were completely dry.</span></div>
      <div class="clue"><b>🔎 Clue 3</b><span>One suspect was holding a plate and insisting they had already eaten.</span></div>
    </div>
    """, unsafe_allow_html=True)

    suspects = {
        "Zayn 🕶️": "claims he was reading a book in the library.",
        "Boo 👻": "says they were floating in the garden.",
        "Professor Chaos 🧪": "says the cupcake was part of a scientific experiment.",
    }

    st.markdown("### 🕵️ Who do you suspect?")
    answer = st.radio(
        "Choose a suspect",
        list(suspects.keys()),
        index=None,
        key="mystery_choice",
        label_visibility="collapsed",
        format_func=lambda s: f"{s}  —  {suspects[s]}",
    )

    attempts = st.session_state.mystery_attempts
    if attempts:
        st.markdown(f'<div class="small-muted">Attempts so far: {attempts}</div>', unsafe_allow_html=True)

    if st.button("🔎 Submit my theory", use_container_width=True):
        st.session_state.mystery_attempts += 1
        if answer and answer.startswith("Professor"):
            st.session_state.mystery_answered = True
            st.balloons()
            notice("success", "Case solved! Professor Chaos had purple icing on the sleeve and a very suspicious plate. "
                              "The 'experiment' was apparently delicious.")
        elif answer:
            notice("warning", "Not quite! Re-read the clues. One suspect's explanation is especially suspicious.")
            if st.session_state.mystery_attempts >= 2:
                notice("info", "Hint: only one suspect admits the cupcake was actually handled — "
                               "and calls it 'science' instead of an alibi.")
        else:
            notice("warning", "Choose a suspect first.")

    if st.session_state.mystery_answered:
        st.markdown("### 🏆 Achievement unlocked: Cupcake Detective")
        st.markdown(f'<div class="small-muted">Solved in {st.session_state.mystery_attempts} attempt(s).</div>',
                    unsafe_allow_html=True)
        if st.button("Play the case again"):
            st.session_state.mystery_answered = False
            st.session_state.mystery_attempts = 0
            st.session_state.pop("mystery_choice", None)
            st.rerun()

# ---------- Footer ----------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#8994b7;font-size:12px'>"
    "🌌 THE UNKNOWN · Meet characters. Discover secrets. Make a little chaos. "
    "<br>Powered by Ollama Cloud & Streamlit</div>",
    unsafe_allow_html=True,
)
