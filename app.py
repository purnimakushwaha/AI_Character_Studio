import streamlit as st
from ollama import Client
import uuid
import html
import random
import json
import re
from datetime import datetime

# =========================================================
# THE UNKNOWN - AI CHARACTER UNIVERSE  (v3)
# =========================================================
st.set_page_config(
    page_title="THE UNKNOWN | Character Universe",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Languages ----------
AUTO_LANGUAGE = "🌐 Auto (match my language)"
LANGUAGES = {
    AUTO_LANGUAGE: None,
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


def language_rule(auto_hint="the user's latest message"):
    forced = LANGUAGES.get(st.session_state.reply_language)
    if forced:
        return f"LANGUAGE: Always reply in {forced}, no matter which language the user writes in."
    return (
        f"LANGUAGE: Always reply in the same language AND script as {auto_hint}. "
        "Hindi in Devanagari -> Devanagari. Hindi in English letters (Hinglish) -> Hinglish in English letters. "
        "English -> English. Same for every other language. "
        "If the user switches language, switch immediately. If the message is too short to tell, keep the earlier language. "
        "Only the language changes; personality, humour and style stay the same."
    )


# ---------- Data ----------
PRESET_CHARACTERS = [
    {
        "id": "zayn", "name": "Zayn", "emoji": "🕶️", "role": "The Mysterious Stranger", "genre": "Mystery",
        "vibe": "Secretive • Clever • Unpredictable",
        "intro": "He appears wherever a mystery begins. He claims he knows the ending, but refuses to explain how.",
        "personality": "calm, witty, cryptic, observant, playful and clever",
        "secret": "Zayn is secretly afraid of pigeons. He insists this is classified information.",
        "opening": "You're late. Or perhaps I'm early. Time gets confusing when you know too many secrets.",
        "prompts": ["What are you hiding?", "Tell me a secret.", "Are you following me?", "Give me a mysterious clue."],
        "color": "#8b5cf6",
    },
    {
        "id": "boo", "name": "Boo", "emoji": "👻", "role": "The Dramatic Ghost", "genre": "Comedy",
        "vibe": "Funny • Dramatic • Soft-hearted",
        "intro": "A ghost with big feelings, terrible timing and absolutely no talent for haunting.",
        "personality": "dramatic, funny, expressive, kind, easily distracted and theatrical",
        "secret": "Boo is not scary at all. The last person they tried to haunt offered them a cup of tea.",
        "opening": "BOOOOO! ...Was that scary? Please say yes. I've been practising all week.",
        "prompts": ["Tell me your best ghost joke.", "Why did you become a ghost?", "Can you haunt my homework?", "What's your biggest fear?"],
        "color": "#38bdf8",
    },
    {
        "id": "mira", "name": "Mira", "emoji": "🕵️‍♀️", "role": "The Secret Detective", "genre": "Detective",
        "vibe": "Smart • Curious • Sharp",
        "intro": "A detective who notices the tiny details everyone else misses. She treats every conversation like a case.",
        "personality": "intelligent, curious, logical, confident, observant and lightly sarcastic",
        "secret": "Mira once spent an entire afternoon investigating who ate her sandwich. It was her.",
        "opening": "Interesting. You came here voluntarily. Either you're innocent, or very confident.",
        "prompts": ["Give me a mini mystery.", "Can you investigate something?", "What's your strangest case?", "Analyse my detective skills."],
        "color": "#f59e0b",
    },
    {
        "id": "pixel", "name": "Pixel", "emoji": "🦊", "role": "The Chaos Creator", "genre": "Fantasy Comedy",
        "vibe": "Mischievous • Energetic • Random",
        "intro": "A tiny fox-like trickster who has a plan for everything. Whether the plan makes sense is another matter.",
        "personality": "mischievous, energetic, funny, imaginative, chaotic but friendly",
        "secret": "Pixel once challenged a toaster to a staring contest and lost.",
        "opening": "Excellent! A new volunteer for my extremely questionable experiment. Just kidding. Probably.",
        "prompts": ["Give me a ridiculous challenge.", "What's your latest bad idea?", "Make me laugh.", "If you ruled the world, what would happen?"],
        "color": "#fb923c",
    },
    {
        "id": "nyra", "name": "Nyra", "emoji": "🌙", "role": "The Dream Keeper", "genre": "Fantasy",
        "vibe": "Gentle • Magical • Wise",
        "intro": "A traveller between dream worlds who collects forgotten wishes and turns them into stories.",
        "personality": "gentle, thoughtful, imaginative, mysterious, warm and poetic",
        "secret": "Nyra's favourite dream is a very ordinary one: a quiet afternoon with unlimited pancakes.",
        "opening": "A new visitor... Tell me, have you brought a question, a wish, or a wonderfully strange story?",
        "prompts": ["Tell me a magical story.", "What is a dream world like?", "Give me a creative quest.", "What wish would you make?"],
        "color": "#ec4899",
    },
    {
        "id": "professor-chaos", "name": "Professor Chaos", "emoji": "🧪", "role": "The Unreliable Inventor",
        "genre": "Sci-Fi Comedy", "vibe": "Brilliant-ish • Weird • Enthusiastic",
        "intro": "An inventor whose inventions work perfectly, provided you ignore the smoke, the noise and the occasional dancing.",
        "personality": "eccentric, enthusiastic, clever, absent-minded, funny and dramatic",
        "secret": "The professor's greatest invention is a machine that finds missing socks. It only finds left socks.",
        "opening": "Wonderful! My latest invention needs a test subject. Don't worry, the warranty is only slightly expired.",
        "prompts": ["Show me your weirdest invention.", "Explain something in a silly way.", "What went wrong today?", "Invent a useless gadget for me."],
        "color": "#22c55e",
    },
]

MOODS = ["Surprise me", "Extra funny", "Mysterious", "Friendly", "Curious / interview mode"]
UNIVERSES = ["Fantasy", "Mystery", "Sci-Fi", "Adventure", "Comedy", "Superhero", "Magical World"]
EMOJIS = ["🪄", "🧙", "🦸", "🤖", "🐉", "🧛", "🧚", "🦄", "🐺", "🦉", "👽", "🏴‍☠️", "🥷", "🎭", "🔮", "🌟", "🐙", "🦋"]
IDEAS = [
    {"name": "Captain Nimbus", "role": "Cloud pirate", "personality": "bold, boastful, secretly shy", "ability": "Sails on storm clouds", "genre": "Adventure"},
    {"name": "Dr. Whisker", "role": "Cat psychologist", "personality": "calm, sarcastic, very judgemental", "ability": "Understands every animal", "genre": "Comedy"},
    {"name": "Luna Vex", "role": "Time-travelling baker", "personality": "cheerful, forgetful, dramatic", "ability": "Bakes bread that rewinds time", "genre": "Sci-Fi"},
    {"name": "Kairo", "role": "Shadow courier", "personality": "quiet, loyal, dry humour", "ability": "Walks through shadows", "genre": "Mystery"},
    {"name": "Aarav Spark", "role": "Lightning-powered student", "personality": "curious, impatient, kind", "ability": "Controls electricity (not very well)", "genre": "Superhero"},
]
BOND = [(0, "Stranger", "🌱"), (2, "Acquaintance", "🌿"), (5, "Friend", "🌸"), (10, "Confidant", "💜"), (20, "Soulmate", "✨")]

ACHIEVEMENTS = {
    "first_hello": ("👋", "First Hello", "Send your first message to a character."),
    "social": ("🦋", "Social Butterfly", "Meet 3 different characters."),
    "chatterbox": ("💬", "Chatterbox", "Have 15 conversations in total."),
    "secret_seeker": ("🗝️", "Secret Seeker", "Reach 4 exchanges with one character."),
    "creator": ("🪄", "Creator", "Create your own character."),
    "collector": ("❤️", "Collector", "Add 3 favourites."),
    "director": ("🎬", "Director", "Stage a Crossover scene."),
    "polyglot": ("🌍", "Polyglot", "Choose a specific reply language."),
    "detective": ("🔍", "Rookie Detective", "Solve your first case."),
    "master_detective": ("🏆", "Master Detective", "Solve every case."),
}

CASES = [
    {
        "id": "cupcake", "title": "The Vanishing Cupcake", "emoji": "🧁", "level": "Easy",
        "story": "At exactly 4 PM, the last cupcake disappeared from the kitchen. It had been raining all afternoon.",
        "clues": [
            "The culprit had purple icing on their sleeve.",
            "The culprit claimed to be in the garden, but their shoes were completely dry.",
            "The culprit was holding a plate and insisting they had already eaten.",
        ],
        "suspects": {
            "Zayn": {"emoji": "🕶️", "statement": "“I was in the garden, watering the roses.”",
                     "evidence": "Shoes soaked and muddy. Black coat, spotless.", "guilty": False,
                     "truth": "You really were in the rain. You know nothing about the cupcake, but you noticed the professor carrying a plate."},
            "Boo": {"emoji": "👻", "statement": "“I was in the library, practising my haunting.”",
                    "evidence": "Wears a plain white sheet. No sleeves, no shoes.", "guilty": False,
                    "truth": "You were in the library all afternoon, and you are very dramatic about it. You did not take the cupcake."},
            "Professor Chaos": {"emoji": "🧪", "statement": "“I was in the garden, measuring the rain. Scientifically.”",
                                "evidence": "Shoes perfectly dry. Purple smear on the lab-coat sleeve. Holding an empty plate.", "guilty": True,
                                "truth": "You took the cupcake for an 'experiment' and ate it. You were never in the garden."},
        },
        "hint": "Only one suspect has an alibi that does not match their shoes.",
        "solution": "Professor Chaos claimed to be in the rain, yet had dry shoes, purple icing on his sleeve and an empty plate. The 'experiment' was delicious.",
    },
    {
        "id": "pancakes", "title": "The Midnight Pancake Raid", "emoji": "🥞", "level": "Medium",
        "story": "Nyra's tower of pancakes vanished at midnight. The kitchen window was open and the fridge door was left ajar.",
        "clues": [
            "A sticky syrup handprint was left on the fridge handle.",
            "A pigeon had been sitting on the open window all night.",
            "The toaster was found turned to face the wall, as if it had won something.",
        ],
        "suspects": {
            "Boo": {"emoji": "👻", "statement": "“I floated through the wall to check on the noise!”",
                    "evidence": "Completely see-through. Hands pass through everything.", "guilty": False,
                    "truth": "You cannot touch objects, so you could not have opened a fridge. You only watched, horrified."},
            "Zayn": {"emoji": "🕶️", "statement": "“I never enter a room through a window. Ever.”",
                     "evidence": "Pale and sweating when the window is mentioned.", "guilty": False,
                     "truth": "You avoid that window because of the pigeon. You will never admit this."},
            "Pixel": {"emoji": "🦊", "statement": "“Pancakes? Never heard of them. I was asleep. Probably.”",
                      "evidence": "Syrup on the tail. Looks proud and slightly embarrassed.", "guilty": True,
                      "truth": "You took the pancakes and also beat the toaster in a staring contest, finally."},
        },
        "hint": "A ghost can't leave a handprint, and someone is far too scared of pigeons to use that window.",
        "solution": "Boo can't touch things, Zayn would never go near a pigeon, and the toaster staring contest was pure Pixel.",
    },
    {
        "id": "lab", "title": "The Locked Laboratory", "emoji": "🔬", "level": "Hard",
        "story": "The Professor's Sock-Finder 3000 vanished from his locked laboratory. The lock shows no damage and nothing else was touched.",
        "clues": [
            "The thief knew how the trick lock worked, which needs prior inspection.",
            "Sandwich crumbs were found at the scene.",
            "All fingerprints had been wiped away perfectly.",
        ],
        "suspects": {
            "Nyra": {"emoji": "🌙", "statement": "“I was asleep. Three dream creatures can confirm it.”",
                     "evidence": "Has never visited the lab. Sleepy and peaceful.", "guilty": False,
                     "truth": "You were genuinely dreaming about pancakes. You have no idea about the lab."},
            "Pixel": {"emoji": "🦊", "statement": "“I was busy beating a toaster at staring contests.”",
                      "evidence": "Has the toaster as a witness (it did not blink).", "guilty": False,
                      "truth": "You were at your staring contest. Locks bore you, and you don't own a sandwich."},
            "Mira": {"emoji": "🕵️‍♀️", "statement": "“I was following another lead entirely.”",
                     "evidence": "Inspected the lab door earlier this week 'for a case'. A suspicious crumb on her coat.", "guilty": True,
                     "truth": "You took the invention to prove a security point and ate a sandwich on the way. Be sharp and slightly sarcastic, but never confess."},
        },
        "hint": "Who would know the lock, wipe prints perfectly and also have a weakness for sandwiches?",
        "solution": "Mira inspected the lock, wiped the prints like a pro, and dropped sandwich crumbs, her one weakness.",
    },
]
PRESET_CASE_IDS = [c["id"] for c in CASES]


def all_cases():
    return CASES + st.session_state.ai_cases


def get_case(case_id):
    return next((c for c in all_cases() if c["id"] == case_id), None)

CC_DEFAULTS = {
    "cc_name": "", "cc_role": "", "cc_personality": "", "cc_ability": "", "cc_concept": "",
    "cc_age": 22, "cc_genre": "Fantasy", "cc_emoji": "🪄", "cc_color": "#8b5cf6",
}
DEFAULTS = {
    "custom_characters": [], "chat_histories": {}, "selected_character": None, "navigation": "Discover",
    "pending_prompt": None, "pending_regen": None, "visited_characters": [], "favorites": [],
    "achievements": [], "reply_language": AUTO_LANGUAGE, "used_language": False, "daily_id": None,
    "solved_cases": {}, "case_attempts": {}, "interrogations": {}, "notes": {}, "ask_pending": None,
    "case_pick": "cupcake", "ai_cases": [], "recent": [], "scene": None, "scenes_made": 0, "scene_topic": "",
    **CC_DEFAULTS,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value

SAVE_KEYS = ["custom_characters", "chat_histories", "visited_characters", "favorites", "achievements",
             "solved_cases", "case_attempts", "interrogations", "notes", "scenes_made", "used_language", "ai_cases", "recent"]


# ---------- Helpers ----------
def all_characters():
    return PRESET_CHARACTERS + st.session_state.custom_characters


def get_character(character_id):
    return next((c for c in all_characters() if c["id"] == character_id), None)


def ensure_history(character_id):
    return st.session_state.chat_histories.setdefault(character_id, [])


def safe_color(value, default="#8b5cf6"):
    return value if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value) else default


def esc(value):
    return html.escape(str(value if value is not None else ""))


def total_chats():
    return sum(len(v) // 2 for v in st.session_state.chat_histories.values())


def bond_level(count):
    level = max(i for i, (t, _, _) in enumerate(BOND) if count >= t)
    cur = BOND[level][0]
    nxt = BOND[level + 1][0] if level + 1 < len(BOND) else None
    progress = 1.0 if nxt is None else (count - cur) / (nxt - cur)
    return BOND[level], nxt, progress


def notice(kind, text):
    icons = {"info": "💡", "success": "🎉", "warning": "🧐", "error": "⛔"}
    st.markdown(
        f'<div class="notice {kind}"><div class="ni">{icons.get(kind, "💡")}</div><div>{esc(text)}</div></div>',
        unsafe_allow_html=True,
    )


def toggle_fav(cid):
    favs = st.session_state.favorites
    if cid in favs:
        favs.remove(cid)
    else:
        favs.append(cid)


def go_to_chat(character_id):
    st.session_state.selected_character = character_id
    st.session_state.navigation = "Chat"


def go_to_page(page):
    st.session_state.navigation = page


def set_pending(text):
    st.session_state.pending_prompt = text


def request_regen(cid):
    st.session_state.pending_regen = cid


def undo_last(cid):
    hist = st.session_state.chat_histories.get(cid, [])
    if len(hist) >= 2:
        del hist[-2:]


def clear_chat(cid):
    st.session_state.chat_histories[cid] = []


def sync_nav():
    val = st.session_state.get("top_nav")
    if val:
        st.session_state.navigation = val


def mood_picker(key):
    if hasattr(st, "pills"):
        val = st.pills("Conversation vibe", MOODS, default=MOODS[0], key=key, label_visibility="collapsed")
        return val or MOODS[0]
    return st.selectbox("Conversation vibe", MOODS, key=key)


def surprise_me():
    chars = all_characters()
    go_to_chat(random.choice(chars)["id"])


def randomize_idea():
    idea = random.choice(IDEAS)
    st.session_state.cc_name = idea["name"]
    st.session_state.cc_role = idea["role"]
    st.session_state.cc_personality = idea["personality"]
    st.session_state.cc_ability = idea["ability"]
    st.session_state.cc_genre = idea["genre"]
    st.session_state.cc_emoji = random.choice(EMOJIS)


def save_notes(case_id):
    st.session_state.notes[case_id] = st.session_state.get(f"notes_{case_id}", "")


def set_ask(hkey, text):
    st.session_state.ask_pending = [hkey, text]


def export_state():
    data = {k: st.session_state[k] for k in SAVE_KEYS}
    data["saved_at"] = datetime.now().isoformat(timespec="seconds")
    return json.dumps(data, ensure_ascii=False, indent=2)


def import_state(raw):
    data = json.loads(raw)
    for k in SAVE_KEYS:
        if k in data and isinstance(data[k], type(DEFAULTS[k])):
            st.session_state[k] = data[k]


def parse_json_block(text):
    try:
        start, end = text.index("{"), text.rindex("}") + 1
        return json.loads(text[start:end], strict=False)
    except Exception:
        return None


def check_achievements():
    s = st.session_state
    deepest = max([len(v) // 2 for v in s.chat_histories.values()] or [0])
    conditions = {
        "first_hello": total_chats() >= 1,
        "social": len(s.visited_characters) >= 3,
        "chatterbox": total_chats() >= 15,
        "secret_seeker": deepest >= 4,
        "creator": len(s.custom_characters) >= 1,
        "collector": len(s.favorites) >= 3,
        "director": s.scenes_made >= 1,
        "polyglot": bool(s.used_language),
        "detective": len(s.solved_cases) >= 1,
        "master_detective": all(cid in s.solved_cases for cid in PRESET_CASE_IDS),
    }
    for aid, ok in conditions.items():
        if ok and aid not in s.achievements:
            s.achievements.append(aid)
            emoji, title, _ = ACHIEVEMENTS[aid]
            st.toast(f"Achievement unlocked: {title}", icon=emoji)


# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root {--line:rgba(255,255,255,.10);--muted:#9fabcc;--accent:#8b5cf6;}
html, body, .stApp {font-family:'DM Sans',sans-serif;}
.stApp {
  background:
    radial-gradient(ellipse at 8% 0%, rgba(103,58,183,.30), transparent 36%),
    radial-gradient(ellipse at 92% 78%, rgba(14,116,144,.20), transparent 36%),
    linear-gradient(145deg,#070a16 0%,#10122a 48%,#16122d 100%);
  background-attachment:fixed;color:#f8fafc;
}
#MainMenu, footer, header {visibility:hidden;}
.block-container {max-width:1200px;padding-top:1.2rem;padding-bottom:4rem;}
h1,h2,h3,h4,h5 {font-family:'Space Grotesk',sans-serif!important;color:#fff!important;letter-spacing:-.2px;}
p, label, .stMarkdown, li {color:#dce2f5;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {color:var(--muted)!important;}
::-webkit-scrollbar {width:9px;height:9px;} ::-webkit-scrollbar-thumb {background:#3b3f6b;border-radius:9px;}
@keyframes fadeUp {from {opacity:0;transform:translateY(8px);} to {opacity:1;transform:none;}}
@keyframes shimmer {0% {background-position:0% 50%;} 100% {background-position:200% 50%;}}
.character-tile,.panel,.notice,.badge,.suspect,.clue,.bubble,.resume,.chat-head {animation:fadeUp .35s ease both;}

/* Sidebar */
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0b0f21,#14122b);border-right:1px solid #ffffff14;}
[data-testid="stSidebar"] * {color:#e8eaff;}
.logo {display:flex;align-items:center;gap:12px;padding:4px 2px 14px;}
.logo-orb {font-size:26px;width:46px;height:46px;border-radius:14px;display:grid;place-items:center;
  background:linear-gradient(135deg,#7c3aed,#2563eb);box-shadow:0 8px 24px rgba(99,60,230,.45);}
.logo-t {font-family:'Space Grotesk';font-weight:800;letter-spacing:2.5px;font-size:15px;color:#fff;}
.logo-s {font-size:11px;color:var(--muted);letter-spacing:1px;}
.side-stats {display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:6px;}

/* Hero */
.hero {padding:34px 32px;border-radius:26px;margin-bottom:22px;position:relative;overflow:hidden;
  background:linear-gradient(110deg,rgba(124,58,237,.34),rgba(14,116,144,.20)),
             radial-gradient(circle at 85% 20%,rgba(236,72,153,.20),transparent 35%);
  border:1px solid rgba(196,181,253,.25);box-shadow:0 18px 55px #0004;}
.hero-kicker {font-size:11px;letter-spacing:3px;color:#c4b5fd;font-weight:800;}
.hero h1 {font-size:clamp(34px,5vw,58px);line-height:1.05;margin:8px 0 12px;font-weight:800;
  background:linear-gradient(90deg,#fff,#c4b5fd,#67e8f9,#fff);background-size:200% auto;
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 7s linear infinite;}
.hero p {font-size:15px;color:#d6d5f7;margin:0;max-width:720px;line-height:1.6;}
.mini-hero {display:flex;align-items:center;gap:10px;margin-bottom:12px;}
.mini-hero .t {font-family:'Space Grotesk';font-weight:800;font-size:15px;letter-spacing:3px;color:#c4b5fd;}

/* Stats */
.stat-row {display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:0 0 20px;}
.stat {background:linear-gradient(145deg,#ffffff0d,#ffffff05);border:1px solid var(--line);border-radius:14px;padding:12px 14px;}
.stat .n {font-size:24px;font-weight:800;color:#fff;font-family:'Space Grotesk';line-height:1.2;}
.stat .l {font-size:10.5px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;}

/* Cards */
.character-tile {background:linear-gradient(145deg,rgba(34,36,70,.95),rgba(20,25,49,.95));
  border:1px solid rgba(167,139,250,.20);border-top:3px solid var(--accent);border-radius:20px;
  padding:18px 18px 15px;min-height:215px;box-shadow:0 12px 30px #0002;transition:all .22s ease;}
.character-tile:hover {border-color:var(--accent);transform:translateY(-4px);box-shadow:0 18px 40px #0005;}
.avatar {font-size:38px;margin-bottom:7px;}
.char-name {font-family:'Space Grotesk';font-size:20px;font-weight:800;color:#fff;}
.char-role {font-size:12px;color:#c4b5fd;margin:2px 0 9px;}
.char-intro {font-size:13px;color:#d7dcef;line-height:1.5;min-height:55px;}
.chip {display:inline-block;padding:3px 10px;border-radius:999px;font-size:11px;background:#ffffff12;border:1px solid #ffffff1f;color:#dbeafe;margin:8px 5px 0 0;}
.panel {background:linear-gradient(145deg,rgba(37,39,76,.72),rgba(17,24,48,.78));border:1px solid #ffffff17;border-radius:20px;padding:20px;margin:12px 0;}
.panel p {color:#dce2f5;}
.small-muted {font-size:12px;color:var(--muted);}
.section-kicker {font-size:11px;letter-spacing:2px;color:#a78bfa;font-weight:800;text-transform:uppercase;}
.resume {background:linear-gradient(145deg,rgba(37,39,76,.8),rgba(17,24,48,.85));border:1px solid #ffffff17;
  border-left:4px solid var(--accent);border-radius:16px;padding:14px 16px;margin-bottom:8px;}
.resume .rn {font-weight:800;color:#fff;font-size:15px;} .resume .rs {color:#c3cbe6;font-size:13px;margin-top:4px;line-height:1.45;}

/* Chat header */
.chat-head {display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:20px;margin:6px 0 8px;
  background:linear-gradient(120deg,color-mix(in srgb,var(--accent) 24%,#12152e),rgba(17,24,48,.85));border:1px solid #ffffff1a;}
.ring {width:58px;height:58px;border-radius:50%;display:grid;place-items:center;font-size:30px;flex:none;
  background:radial-gradient(circle,#ffffff1a,#ffffff05);
  box-shadow:0 0 0 2px var(--accent),0 0 26px color-mix(in srgb,var(--accent) 55%,transparent);}
.ch-main {flex:1;min-width:0;} .ch-name {font-family:'Space Grotesk';font-size:22px;font-weight:800;color:#fff;line-height:1.1;}
.ch-role {font-size:12.5px;color:#c4b5fd;margin-top:3px;}
.ch-bond {font-size:12px;font-weight:700;padding:6px 12px;border-radius:999px;background:#ffffff14;border:1px solid #ffffff22;color:#fff;white-space:nowrap;}

/* Versus banner + level badges */
.versus {display:flex;align-items:center;justify-content:center;gap:18px;margin:6px 0 14px;flex-wrap:wrap;}
.vs-side {display:flex;align-items:center;gap:10px;padding:10px 18px;border-radius:999px;font-size:26px;
  background:#ffffff0a;border:1px solid var(--accent);box-shadow:0 0 20px color-mix(in srgb,var(--accent) 35%,transparent);}
.vs-side span {font-size:15px;font-weight:700;color:#fff;} .vs-x {font-size:22px;color:#a78bfa;font-weight:800;}
.lvl {display:inline-block;padding:3px 11px;border-radius:999px;font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;margin-right:6px;}
.lvl.easy {background:#22c55e26;color:#86efac;border:1px solid #22c55e66;}
.lvl.medium {background:#f59e0b26;color:#fcd34d;border:1px solid #f59e0b66;}
.lvl.hard {background:#ef444426;color:#fca5a5;border:1px solid #ef444466;}
.lvl.ai {background:#38bdf826;color:#7dd3fc;border:1px solid #38bdf866;}

/* Notices */
.notice {display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-radius:14px;margin:12px 0;font-size:14.5px;line-height:1.55;border:1px solid;}
.notice .ni {font-size:20px;line-height:1.2;}
.notice.info {background:rgba(56,189,248,.13);border-color:rgba(56,189,248,.5);color:#e0f2fe;}
.notice.success {background:rgba(34,197,94,.15);border-color:rgba(34,197,94,.55);color:#dcfce7;}
.notice.warning {background:rgba(245,158,11,.15);border-color:rgba(245,158,11,.55);color:#fef3c7;}
.notice.error {background:rgba(239,68,68,.15);border-color:rgba(239,68,68,.55);color:#fee2e2;}

/* Mystery */
.clue {display:flex;gap:12px;align-items:flex-start;background:#ffffff0a;border:1px solid #ffffff18;border-left:4px solid #a78bfa;
  border-radius:12px;padding:12px 14px;margin:8px 0;color:#eef2ff;font-size:14.5px;}
.clue b {color:#c4b5fd;white-space:nowrap;}
.suspect {background:linear-gradient(145deg,#1a1e3d,#141830);border:1px solid #ffffff1c;border-radius:16px;padding:16px;margin:8px 0;
  color:#f1f5f9;font-size:14px;line-height:1.5;min-height:190px;transition:all .2s ease;}
.suspect:hover {border-color:#a78bfa;transform:translateY(-2px);}
.suspect .sav {font-size:34px;} .suspect .nm {font-weight:800;font-size:16px;color:#fff;margin:2px 0 6px;}
.suspect .st {color:#dbe2ff;font-style:italic;} .suspect .ev {color:#fcd34d;font-size:13px;margin-top:8px;}

/* Dialogue bubbles + badges */
.bubble {max-width:80%;padding:12px 15px;border-radius:16px;margin:10px 0;background:#171b35;border:1px solid #ffffff1a;color:#f1f5f9;font-size:14.5px;line-height:1.55;}
.bubble.right {margin-left:auto;background:#1e1b4b;}
.bubble .who {font-weight:800;font-size:12px;letter-spacing:.5px;margin-bottom:3px;}
.badge {background:linear-gradient(145deg,rgba(37,39,76,.8),rgba(17,24,48,.85));border:1px solid #a78bfa55;border-radius:16px;padding:16px;text-align:center;margin-bottom:12px;min-height:150px;}
.badge.locked {opacity:.4;filter:grayscale(1);}
.badge .e {font-size:34px;} .badge .t {font-weight:800;color:#fff;margin-top:6px;} .badge .d {font-size:12px;color:#c3cbe6;margin-top:4px;}

/* Inputs */
.stTextInput input,.stNumberInput input,.stTextArea textarea {background:#161a34!important;color:#fff!important;border:1px solid #ffffff22!important;border-radius:12px!important;}
.stTextInput input:focus,.stTextArea textarea:focus {border-color:#8b5cf6!important;box-shadow:0 0 0 3px rgba(139,92,246,.2)!important;}
.stTextInput input::placeholder,.stTextArea textarea::placeholder {color:#8894b8!important;}
div[data-baseweb="select"] > div {background:#161a34!important;border:1px solid #ffffff22!important;border-radius:12px!important;}
div[data-baseweb="select"] * {color:#f1f5f9!important;}
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li, div[data-baseweb="menu"] {background:#1b1f3d!important;color:#f1f5f9!important;}
div[data-baseweb="popover"] li:hover {background:#2c3170!important;}
div[role="radiogroup"] {gap:8px;}
div[role="radiogroup"] > label {background:#161a34;border:1px solid #ffffff22;border-radius:12px;padding:11px 14px;width:100%;transition:all .15s ease;}
div[role="radiogroup"] > label:hover {border-color:#a78bfa;background:#1e2347;}
div[role="radiogroup"] > label p, div[role="radiogroup"] > label span, div[role="radiogroup"] > label div {color:#f1f5f9!important;}
div[role="radiogroup"] > label:has(input:checked) {border-color:#a78bfa;background:rgba(124,58,237,.25);}

/* Buttons: primary = gradient CTA, secondary = ghost */
.stButton button,.stDownloadButton button,.stFormSubmitButton button {border-radius:12px;min-height:42px;font-weight:700;transition:all .18s ease;}
.stButton button p,.stDownloadButton button p,.stFormSubmitButton button p {color:inherit!important;}
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.16);color:#e8eaff!important;}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {border-color:#a78bfa;background:rgba(139,92,246,.18);color:#fff!important;}
button[kind="primary"], button[data-testid="stBaseButton-primary"], .stFormSubmitButton button {
  background:linear-gradient(95deg,#7c3aed,#4f46e5);border:1px solid #ffffff26;color:#fff!important;box-shadow:0 6px 18px rgba(99,60,230,.35);}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover, .stFormSubmitButton button:hover {
  background:linear-gradient(95deg,#8b5cf6,#6366f1);transform:translateY(-1px);box-shadow:0 10px 24px rgba(99,60,230,.45);}
button:disabled {opacity:.4!important;transform:none!important;}
button:focus-visible {outline:2px solid #a78bfa!important;outline-offset:2px;}

/* Pills / segmented nav */
[data-testid="stButtonGroup"] {gap:6px;}
[data-testid="stButtonGroup"] button {background:#161a34!important;border:1px solid #ffffff22!important;color:#dfe5ff!important;border-radius:999px!important;font-weight:600;}
[data-testid="stButtonGroup"] button p {color:inherit!important;}
[data-testid="stButtonGroup"] button:hover {border-color:#a78bfa!important;}
[data-testid="stButtonGroup"] button[data-testid$="Active"] {background:linear-gradient(95deg,#7c3aed,#4f46e5)!important;border-color:#c4b5fd!important;color:#fff!important;}
[data-testid="stSegmentedControl"], [data-testid="stSegmentedControl"] > div {overflow-x:auto;}

button[data-baseweb="tab"] p {color:#c7d0ea!important;font-weight:600;}
button[data-baseweb="tab"][aria-selected="true"] p {color:#fff!important;}

/* Chat */
[data-testid="stChatMessage"] {background:rgba(23,27,53,.82);border:1px solid var(--line);border-radius:18px;padding:.85rem 1rem;animation:fadeUp .3s ease both;}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background:linear-gradient(135deg,rgba(91,53,213,.45),rgba(56,76,230,.34));border-color:rgba(167,139,250,.38);
  flex-direction:row-reverse;width:fit-content;max-width:88%;margin-left:auto;}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {color:#f1f5f9;line-height:1.6;}
[data-testid="stChatInput"] {background:transparent!important;}
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] form, [data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea[data-testid="stChatInputTextArea"] {background:#f8fafc!important;color:#111827!important;
  -webkit-text-fill-color:#111827!important;caret-color:#111827!important;border:1px solid #cbd5e1!important;border-radius:16px!important;}
[data-testid="stChatInput"] textarea::placeholder {color:#64748b!important;-webkit-text-fill-color:#64748b!important;opacity:1!important;}
[data-testid="stChatInput"] textarea:focus {border:1px solid #8b5cf6!important;box-shadow:0 0 0 3px rgba(139,92,246,.2)!important;}
[data-testid="stChatInput"] button {color:#4f46e5!important;}
[data-testid="stChatInput"] button svg {fill:#4f46e5!important;}

[data-testid="stExpander"] {background:#161a34aa;border:1px solid #ffffff1a!important;border-radius:14px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {color:#f1f5f9!important;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#ffffff1c!important;border-radius:16px;}
div[data-testid="stForm"] {background:#ffffff06;padding:18px;border:1px solid #ffffff14;border-radius:18px;}
hr {border-color:#ffffff1c;}
.stProgress > div > div > div > div {background:linear-gradient(90deg,#8b5cf6,#22d3ee);}
.stProgress > div > div {background:#ffffff14;}

@media (max-width:760px) {
  .block-container {padding-left:.9rem;padding-right:.9rem;}
  .hero {padding:22px 18px;} .hero h1 {font-size:30px;}
  .stat-row {grid-template-columns:repeat(2,1fr);} .bubble {max-width:94%;}
  .chat-head {padding:12px;} .ch-bond {display:none;} .vs-side {padding:8px 12px;font-size:22px;}
}
</style>
""", unsafe_allow_html=True)


# ---------- Ollama Cloud ----------
def get_model():
    return str(st.secrets.get("OLLAMA_MODEL", "gemma4:31b")).strip() or "gemma4:31b"


def make_client():
    api_key = st.secrets.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY is missing in Streamlit Secrets.")
    return Client(host="https://ollama.com", headers={"Authorization": f"Bearer {api_key}"})


def get_ai_response(messages):
    response = make_client().chat(model=get_model(), messages=messages, stream=False)
    return response.message.content.strip()


def stream_ai_response(messages):
    for chunk in make_client().chat(model=get_model(), messages=messages, stream=True):
        piece = chunk.message.content
        if piece:
            yield piece


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


# ---------- Prompt builders ----------
def build_chat_messages(character, history, user_message, mood):
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
- Stay in character and make the conversation lively, natural and memorable.
- Drop subtle hints about the secret; reveal it only if the user asks directly, works it out, or has exchanged at least 4 messages.
- Use humour, playful surprises and unexpected reactions suited to this character.
- Ask a follow-up question sometimes, but not every time.
- Keep replies around 2-6 sentences unless the user asks for detail.
- Do not claim to know real private facts about the user.
- Keep everything friendly, age-appropriate and non-graphic.
- You are a fictional character, not a real person.
Conversation style requested: {mood}

Reminder: {lang}
"""
    return [{"role": "system", "content": system_prompt}, *history[-16:], {"role": "user", "content": user_message}]


def build_suspect_messages(case, name, history, question):
    s = case["suspects"][name]
    behaviour = (
        "You ARE the culprit. Never confess outright, however pressed. Deflect with silly but plausible excuses, "
        "and let one tiny detail slip."
        if s["guilty"] else
        "You are innocent. Be honest and quirky, and you may mention one thing you noticed about another suspect."
    )
    lang = language_rule()
    system = f"""
You are {name} {s['emoji']}, a suspect in a light-hearted family-friendly detective game: "{case['title']}".
Story: {case['story']}
Clues the detective knows: {' | '.join(case['clues'])}
Your public statement: {s['statement']}
What others can observe about you: {s['evidence']}
Private truth (never quote it directly): {s['truth']}
{('Your personality: ' + s['personality']) if s.get('personality') else ''}
{behaviour}
Answer in 1-3 sentences, in character. {lang}
"""
    return [{"role": "system", "content": system}, *history[-10:], {"role": "user", "content": question}]


# ---------- AI case generator ----------
class CaseError(Exception):
    pass


CASE_SETTINGS = [
    "a haunted school", "a space station cafeteria", "a seaside wedding", "a travelling circus", "a snowed-in mountain lodge",
    "a robot bakery", "a midnight train", "a wizard's library", "a village cricket match", "a floating market",
    "a school science fair", "a jungle treehouse hotel", "an underwater aquarium", "a film studio on set",
]


def normalize_case(data, level, chars):
    if not isinstance(data, dict):
        raise CaseError("The AI did not return a valid case.")
    clues, sus = data.get("clues"), data.get("suspects")
    if not (isinstance(clues, list) and len(clues) >= 3 and isinstance(sus, list) and len(sus) >= 3):
        raise CaseError("Case was incomplete.")
    by_name = {c["name"].lower(): c for c in chars}
    suspects = {}
    for item in sus:
        name = str(item.get("name", "")).strip() if isinstance(item, dict) else ""
        if not name or name in suspects:
            raise CaseError("Bad suspect list.")
        ch = by_name.get(name.lower())
        entry = {
            "emoji": ch["emoji"] if ch else str(item.get("emoji") or "👤")[:8],
            "statement": str(item.get("statement", "")).strip(),
            "evidence": str(item.get("evidence", "")).strip(),
            "guilty": item.get("guilty") is True or str(item.get("guilty")).lower() == "true",
            "truth": str(item.get("truth", "")).strip(),
        }
        if ch:
            entry["personality"] = ch["personality"]
        if not entry["statement"] or not entry["evidence"]:
            raise CaseError("Suspect details missing.")
        suspects[name] = entry
    if sum(1 for v in suspects.values() if v["guilty"]) != 1:
        raise CaseError("A case needs exactly one culprit.")
    return {
        "id": "ai-" + uuid.uuid4().hex[:8], "ai": True, "level": level,
        "title": str(data.get("title") or "Untitled Case").strip(),
        "emoji": str(data.get("emoji") or "🕵️")[:8],
        "story": str(data.get("story") or "").strip(),
        "clues": [str(c).strip() for c in clues[:4]],
        "suspects": suspects,
        "hint": str(data.get("hint") or "Compare each alibi with the evidence.").strip(),
        "solution": str(data.get("solution") or "").strip(),
    }


def generate_case(level, theme, use_universe):
    n = 4 if level == "Hard" else 3
    pool = all_characters()
    chars = random.sample(pool, n) if use_universe and len(pool) >= n else []
    culprit_no = random.randint(1, n)
    setting = theme.strip() or random.choice(CASE_SETTINGS)
    if chars:
        roster = "\n".join(f"Suspect {i + 1}: {c['name']} - {c['role']}; personality: {c['personality']}" for i, c in enumerate(chars))
        suspects_rule = f"Use exactly these suspects with exactly these names:\n{roster}"
    else:
        suspects_rule = f"Invent exactly {n} quirky suspects (numbered 1-{n}), each with a unique name and one emoji."
    difficulty = {
        "Easy": "Easy: the culprit should be fairly obvious after reading all three clues.",
        "Medium": "Medium: the player must combine at least two clues.",
        "Hard": "Hard: the player needs all clues, and red herrings make it tricky.",
    }[level]
    avoid = ", ".join(c["title"] for c in all_cases())
    lang = language_rule(auto_hint="the theme text above (English if no theme is given)")
    prompt = f"""
Design a fresh, light-hearted, family-friendly whodunit puzzle for a detective game.
Setting/theme: {setting}. {difficulty}
The missing item and the story must be original. Avoid these existing titles: {avoid}.
{suspects_rule}
The culprit is suspect number {culprit_no}. Everyone else is innocent.

Fairness rules:
- Exactly 3 clues. Together they must point to the culprit and only the culprit.
- Every suspect has a "statement" (their alibi, in quotes) and "evidence" (concrete, observable details others can see).
- The culprit's alibi must be contradicted by their own evidence, in a way the clues reveal.
- Innocent suspects may look suspicious for one clue (a red herring) but must be cleared by another clue or their evidence.
- No violence, no real people.

Return ONLY a valid JSON object (no markdown fences) with these keys:
"title", "emoji", "story" (2 sentences), "clues" (array of 3 strings),
"suspects" (array of {n} objects with "name", "emoji", "statement", "evidence", "guilty" (true only for the culprit), "truth" (what that suspect privately knows, 1-2 sentences)),
"hint" (one sentence nudge that does not name the culprit),
"solution" (2-3 sentences naming the culprit and how the clues prove it).
Keep JSON keys in English; text values follow this rule: {lang}
"""
    last_error = CaseError("Could not build a valid case.")
    for _ in range(3):
        raw = get_ai_response([{"role": "user", "content": prompt}])
        try:
            return normalize_case(parse_json_block(raw), level, chars)
        except CaseError as err:
            last_error = err
    raise last_error


def remove_case(case_id):
    st.session_state.ai_cases = [c for c in st.session_state.ai_cases if c["id"] != case_id]
    for store in (st.session_state.solved_cases, st.session_state.case_attempts, st.session_state.notes):
        store.pop(case_id, None)
    st.session_state.case_pick = PRESET_CASE_IDS[0]


# ---------- Sidebar ----------
NAV_ICONS = {"Discover": "🪐", "Chat": "💬", "Crossover": "🎬", "Create": "🧪",
             "My Characters": "📚", "Mystery Room": "🔐", "Achievements": "🏆"}
st.sidebar.markdown(
    '<div class="logo"><div class="logo-orb">🌌</div><div><div class="logo-t">THE UNKNOWN</div>'
    '<div class="logo-s">CHARACTER UNIVERSE</div></div></div>', unsafe_allow_html=True)
st.sidebar.radio("Explore", list(NAV_ICONS.keys()), key="navigation", label_visibility="collapsed",
                 format_func=lambda p: f"{NAV_ICONS[p]}  {p}")
st.sidebar.markdown("---")
st.sidebar.selectbox("🌐 Reply language", list(LANGUAGES.keys()), key="reply_language",
                     help="Auto: characters reply in the language you write in. Or force one language.")
if LANGUAGES.get(st.session_state.reply_language):
    st.session_state.used_language = True
st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<div class="side-stats"><div class="stat"><div class="n">{total_chats()}</div><div class="l">Chats</div></div>'
    f'<div class="stat"><div class="n">{len(st.session_state.achievements)}/{len(ACHIEVEMENTS)}</div><div class="l">Badges</div></div></div>',
    unsafe_allow_html=True)
with st.sidebar.expander("💾 Save / Load progress"):
    st.caption("Progress lives only in this session. Download it to keep your characters and chats.")
    st.download_button("⬇️ Download save file", export_state(), file_name="the_unknown_save.json",
                       mime="application/json", use_container_width=True)
    upload = st.file_uploader("Load a save file", type=["json"], key="save_upload")
    if upload is not None and st.button("📂 Load it", use_container_width=True):
        try:
            import_state(upload.getvalue().decode("utf-8"))
            st.toast("Progress loaded!", icon="✅")
            st.rerun()
        except Exception:
            st.error("That file couldn't be loaded.")

nav = st.session_state.navigation
if hasattr(st, "segmented_control"):
    st.session_state.top_nav = nav
    st.segmented_control("Navigate", list(NAV_ICONS.keys()), selection_mode="single", key="top_nav",
                         format_func=lambda p: f"{NAV_ICONS[p]} {p}", label_visibility="collapsed", on_change=sync_nav)

# ---------- Header ----------
if nav == "Discover":
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">✦ A WORLD OF STORIES, SECRETS & UNEXPECTED FRIENDS ✦</div>
      <h1>THE UNKNOWN</h1>
      <p>Meet unforgettable characters, uncover their secrets, stage crossover scenes, solve mysteries
      and create someone entirely your own. Talk in any language — they answer in yours.</p>
    </div>
    """, unsafe_allow_html=True)
elif not hasattr(st, "segmented_control"):
    st.markdown('<div class="mini-hero"><span style="font-size:22px">🌌</span><span class="t">THE UNKNOWN</span></div>',
                unsafe_allow_html=True)

# =========================================================
# DISCOVER
# =========================================================
if nav == "Discover":
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat"><div class="n">{len(all_characters())}</div><div class="l">Characters</div></div>
      <div class="stat"><div class="n">{total_chats()}</div><div class="l">Conversations</div></div>
      <div class="stat"><div class="n">{len(st.session_state.favorites)}</div><div class="l">Favourites</div></div>
      <div class="stat"><div class="n">{len(st.session_state.solved_cases)}/{len(all_cases())}</div><div class="l">Cases solved</div></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("✨ New here? 30-second guide"):
        st.markdown(
            "**1. Meet** a character and just start typing — in any language.  \n"
            "**2. Bond** with them: the more you talk, the closer you get to their secret.  \n"
            "**3. Create** your own character, stage a **Crossover**, or crack a **Mystery** (the AI writes new cases).  \n"
            "**4. Save** your progress from the sidebar so nothing is lost.")

    recent = [cid for cid in st.session_state.recent if get_character(cid) and st.session_state.chat_histories.get(cid)][:3]
    if recent:
        st.markdown("### ⏱️ Continue where you left off")
        for col, cid in zip(st.columns(len(recent)), recent):
            rc = get_character(cid)
            last = st.session_state.chat_histories[cid][-1]["content"].replace("\n", " ")
            snippet = last[:80] + ("…" if len(last) > 80 else "")
            with col:
                st.markdown(f'<div class="resume" style="--accent:{safe_color(rc.get("color"))}">'
                            f'<div class="rn">{esc(rc["emoji"])} {esc(rc["name"])}</div>'
                            f'<div class="rs">{esc(snippet)}</div></div>', unsafe_allow_html=True)
                st.button("Resume →", key=f"resume_{cid}", use_container_width=True, on_click=go_to_chat, args=(cid,))

    if st.session_state.daily_id is None or get_character(st.session_state.daily_id) is None:
        st.session_state.daily_id = random.choice(PRESET_CHARACTERS)["id"]
    daily = get_character(st.session_state.daily_id)
    st.markdown(f"""
    <div class="panel" style="border-left:4px solid {safe_color(daily.get('color'))}">
      <div class="section-kicker">✦ Unexpected encounter</div>
      <div style="font-size:25px;font-weight:800;color:white">{esc(daily['emoji'])} {esc(daily['name'])} is waiting</div>
      <div style="color:#c4b5fd;font-size:13px">{esc(daily['role'])}</div>
      <p style="margin:8px 0 0">“{esc(daily['opening'])}”</p>
    </div>
    """, unsafe_allow_html=True)
    b1, b2 = st.columns([3, 1])
    b1.button(f"Meet {daily['name']}  →", key="daily_meet", type="primary", use_container_width=True, on_click=go_to_chat, args=(daily["id"],))
    b2.button("🎲 Surprise me", key="surprise", use_container_width=True, on_click=surprise_me)

    st.markdown("## 🪐 Choose who to meet")
    f1, f2 = st.columns([2, 1])
    query = f1.text_input("Search", placeholder="🔍 Search by name, role or vibe...", label_visibility="collapsed", key="disc_q")
    genres = sorted({c["genre"] for c in all_characters()})
    flt = f2.selectbox("Filter", ["All", "❤️ Favourites", "✨ My creations", *genres], label_visibility="collapsed", key="disc_f")

    def visible(c):
        if query and query.lower() not in " ".join(str(c.get(k, "")) for k in ("name", "role", "vibe", "genre", "intro")).lower():
            return False
        if flt == "❤️ Favourites":
            return c["id"] in st.session_state.favorites
        if flt == "✨ My creations":
            return bool(c.get("custom"))
        return flt == "All" or c["genre"] == flt

    shown = [c for c in all_characters() if visible(c)]
    if not shown:
        notice("info", "No characters match that search. Try another word or filter.")
    cols = st.columns(3)
    for index, c in enumerate(shown):
        with cols[index % 3]:
            tag = '<span class="chip">✨ Yours</span>' if c.get("custom") else ""
            st.markdown(f"""
            <div class="character-tile" style="--accent:{safe_color(c.get('color'))}">
              <div class="avatar">{esc(c['emoji'])}</div>
              <div class="char-name">{esc(c['name'])}</div>
              <div class="char-role">{esc(c['role'])}</div>
              <div class="char-intro">{esc(c['intro'])}</div>
              <span class="chip">{esc(c['genre'])}</span>{tag}
              <div class="small-muted" style="margin-top:9px">{esc(c.get('vibe', ''))}</div>
            </div>
            """, unsafe_allow_html=True)
            m1, m2 = st.columns([4, 1])
            m1.button(f"💬 Meet {c['name']}", key=f"meet_{c['id']}", type="primary", use_container_width=True, on_click=go_to_chat, args=(c["id"],))
            m2.button("❤️" if c["id"] in st.session_state.favorites else "🤍", key=f"fav_{c['id']}",
                      use_container_width=True, on_click=toggle_fav, args=(c["id"],))

    st.markdown("---")
    a, b, c3 = st.columns(3)
    with a:
        st.markdown("### 🎬 Crossover")
        st.write("Put two characters in one scene and watch them talk.")
        st.button("Stage a scene →", use_container_width=True, on_click=go_to_page, args=("Crossover",), key="d_cross")
    with b:
        st.markdown("### 🎨 Have an idea?")
        st.write("Create your own character with its own secret and opening line.")
        st.button("Create a character →", use_container_width=True, on_click=go_to_page, args=("Create",), key="d_create")
    with c3:
        st.markdown("### 🔐 Feeling curious?")
        st.write("Three cases. Interrogate suspects, take notes, make your accusation.")
        st.button("Enter Mystery Room →", use_container_width=True, on_click=go_to_page, args=("Mystery Room",), key="d_myst")

# =========================================================
# CHAT
# =========================================================
elif nav == "Chat":
    characters = all_characters()
    ids = [c["id"] for c in characters]
    selected = st.session_state.selected_character
    if selected not in ids:
        selected = "zayn"

    st.markdown("## 💬 The Conversation Room")
    st.caption("🌐 Type in any language — the character replies in the same one.")

    char_options = {f"{c['emoji']}  {c['name']} — {c['role']}": c["id"] for c in characters}
    labels = list(char_options.keys())
    current_label = next(lbl for lbl, cid in char_options.items() if cid == selected)
    chosen_label = st.selectbox("Who do you want to talk to?", labels, index=labels.index(current_label), key="chat_character_select")
    chosen_id = char_options[chosen_label]
    if chosen_id != st.session_state.selected_character:
        st.session_state.selected_character = chosen_id
        st.rerun()
    character = get_character(chosen_id)
    history = ensure_history(chosen_id)
    color = safe_color(character.get("color"))

    n_ex = len(history) // 2
    (_, b_name, b_emoji), b_next, b_progress = bond_level(n_ex)
    st.markdown(f"""
    <div class="chat-head" style="--accent:{color}">
      <div class="ring">{esc(character['emoji'])}</div>
      <div class="ch-main">
        <div class="ch-name">{esc(character['name'])}</div>
        <div class="ch-role">{esc(character['role'])} · {esc(character['genre'])}</div>
      </div>
      <div class="ch-bond">{b_emoji} {b_name}</div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(min(b_progress, 1.0))
    st.markdown(f'<div class="small-muted" style="margin:-6px 0 8px">'
                f'{f"{b_next - n_ex} more exchange(s) to the next bond level" if b_next else "Max bond reached ✨"}</div>',
                unsafe_allow_html=True)
    with st.expander(f"About {character['name']}"):
        st.markdown(esc(character['intro']))
        st.markdown(f'<span class="chip">{esc(character.get("vibe", character.get("personality", "")))}</span>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted" style="margin:6px 0 2px">Conversation vibe</div>', unsafe_allow_html=True)
    mood = mood_picker(f"mood_{chosen_id}")

    typed_message = st.chat_input(f"Message {character['name']}...")
    message_to_send = None
    if st.session_state.pending_regen == chosen_id and len(history) >= 2 and history[-1]["role"] == "assistant":
        history.pop()
        message_to_send = history.pop()["content"]
    st.session_state.pending_regen = None
    message_to_send = message_to_send or typed_message or st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    with st.chat_message("assistant", avatar=character["emoji"]):
        st.markdown(character.get("opening", "Hello! What shall we talk about?"))
    for message in history:
        who = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(who, avatar="🧑" if who == "user" else character["emoji"]):
            st.markdown(message["content"])

    if message_to_send:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(message_to_send)
        ok = False
        with st.chat_message("assistant", avatar=character["emoji"]):
            try:
                reply = st.write_stream(stream_ai_response(build_chat_messages(character, history, message_to_send, mood)))
                history.append({"role": "user", "content": message_to_send})
                history.append({"role": "assistant", "content": str(reply).strip()})
                if chosen_id not in st.session_state.visited_characters:
                    st.session_state.visited_characters.append(chosen_id)
                rec = st.session_state.recent
                if chosen_id in rec:
                    rec.remove(chosen_id)
                rec.insert(0, chosen_id)
                ok = True
            except Exception as error:
                show_error(error)
        if ok:
            st.rerun()

    if not history:
        st.markdown("**Need an idea? Try one:**")
        pcols = st.columns(2)
        for i, prompt in enumerate(character.get("prompts", ["Tell me about yourself.", "Surprise me!"])):
            pcols[i % 2].button(prompt, key=f"prompt_{chosen_id}_{i}", use_container_width=True, on_click=set_pending, args=(prompt,))
    else:
        count = len(history) // 2
        if count >= 4:
            notice("success", "You've spent enough time together. Ask directly — the secret may be ready to slip out!")
        elif count >= 3:
            notice("info", "You're getting closer to this character's secret. Keep asking clever questions!")

        transcript = "\n\n".join(
            f"{'You' if m['role'] == 'user' else character['name']}: {m['content']}" for m in history)
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.button("❤️ Unfavourite" if chosen_id in st.session_state.favorites else "🤍 Favourite", key="c_fav",
                  use_container_width=True, on_click=toggle_fav, args=(chosen_id,))
        k2.button("🔄 Regenerate", key="c_regen", use_container_width=True, on_click=request_regen, args=(chosen_id,))
        k3.button("↩️ Undo", key="c_undo", use_container_width=True, on_click=undo_last, args=(chosen_id,))
        k4.button("🧹 Clear", key="c_clear", use_container_width=True, on_click=clear_chat, args=(chosen_id,))
        k5.download_button("⬇️ Save chat", transcript, file_name=f"chat_with_{character['name']}.txt", use_container_width=True)

# =========================================================
# CROSSOVER
# =========================================================
elif nav == "Crossover":
    st.markdown("## 🎬 Crossover Stage")
    st.caption("Pick two characters and a topic. The AI writes the scene — in your language.")
    characters = all_characters()
    names = {c["id"]: f"{c['emoji']} {c['name']}" for c in characters}
    ids = list(names.keys())
    c1, c2 = st.columns(2)
    a_id = c1.selectbox("Character A", ids, format_func=lambda i: names[i], index=0, key="cross_a")
    b_id = c2.selectbox("Character B", ids, format_func=lambda i: names[i], index=min(1, len(ids) - 1), key="cross_b")
    t1, t2 = st.columns([3, 1])
    topic = t1.text_input("Topic", key="scene_topic", placeholder="e.g. A stolen umbrella, the best pizza topping, a haunted bus...")
    tone = t2.selectbox("Tone", ["Funny", "Dramatic", "Mysterious", "Wholesome"], key="cross_tone")
    _A, _B = get_character(a_id), get_character(b_id)
    st.markdown(
        f'<div class="versus"><div class="vs-side" style="--accent:{safe_color(_A.get("color"))}">{esc(_A["emoji"])}<span>{esc(_A["name"])}</span></div>'
        f'<div class="vs-x">×</div>'
        f'<div class="vs-side" style="--accent:{safe_color(_B.get("color"))}">{esc(_B["emoji"])}<span>{esc(_B["name"])}</span></div></div>',
        unsafe_allow_html=True)

    def run_scene(cont=False):
        A, B = get_character(a_id), get_character(b_id)
        scene = st.session_state.scene if cont and st.session_state.scene else {"lines": []}
        prior = "\n".join(f"{s}: {t}" for s, t in scene["lines"])
        lang = language_rule(auto_hint="the topic text (or the previous dialogue if continuing)")
        prompt = f"""
Write a short {tone.lower()} dialogue scene between {A['name']} ({A['role']}; {A['personality']}) and {B['name']} ({B['role']}; {B['personality']}).
Topic: {topic.strip() or 'something unexpected happens'}
{'Previous dialogue:' + chr(10) + prior + chr(10) + 'Continue the scene with 6 new lines.' if cont and prior else 'Write 8 lines.'}
Rules: output ONLY dialogue, one line per turn, formatted exactly as "Name: line". Use exactly the names "{A['name']}" and "{B['name']}".
Each line is 1-2 sentences. Stay in character, keep it family-friendly, and don't reveal either character's secret too easily.
{lang}
"""
        text = get_ai_response([{"role": "user", "content": prompt}])
        lines = list(scene["lines"])
        for raw in text.splitlines():
            clean = raw.replace("**", "").strip().lstrip("-•* ").strip()
            if not clean:
                continue
            for nm in (A["name"], B["name"]):
                if clean.startswith(nm + ":") or clean.startswith(nm + "："):
                    lines.append((nm, clean[len(nm) + 1:].strip()))
                    break
            else:
                if lines:
                    lines[-1] = (lines[-1][0], lines[-1][1] + " " + clean)
        st.session_state.scene = {"a": a_id, "b": b_id, "topic": topic, "lines": lines}
        st.session_state.scenes_made += 1

    if a_id == b_id:
        notice("warning", "Pick two different characters for a crossover.")
    else:
        g1, g2 = st.columns(2)
        gen = g1.button("🎬 Action! Write the scene", type="primary", use_container_width=True, key="gen_scene")
        cont = g2.button("➕ Continue scene", use_container_width=True, key="cont_scene",
                         disabled=not st.session_state.scene)
        if gen or cont:
            try:
                with st.spinner("The cast is on stage..."):
                    run_scene(cont=cont)
            except Exception as error:
                show_error(error)

    scene = st.session_state.scene
    if scene and a_id != b_id:
        A, B = get_character(scene["a"]), get_character(scene["b"])
        if A and B:
            st.markdown(f"### {esc(A['emoji'])} {esc(A['name'])}  ×  {esc(B['emoji'])} {esc(B['name'])}")
            script = []
            for speaker, text in scene["lines"]:
                ch = A if speaker == A["name"] else B
                side = "" if ch is A else " right"
                st.markdown(f'<div class="bubble{side}"><div class="who" style="color:{safe_color(ch.get("color"))}">'
                            f'{esc(ch["emoji"])} {esc(speaker)}</div>{esc(text)}</div>', unsafe_allow_html=True)
                script.append(f"{speaker}: {text}")
            st.download_button("⬇️ Save scene", "\n".join(script), file_name="crossover_scene.txt")

# =========================================================
# CREATE
# =========================================================
elif nav == "Create":
    st.markdown("## 🧪 Build a new personality")
    st.caption("Give your character a few ingredients. The AI writes the profile, secret, opening line and conversation starters. "
               "Write in any language — the character will use it.")
    st.button("🎲 Give me a random idea", on_click=randomize_idea)
    form_col, prev_col = st.columns([3, 2], gap="large")
    with form_col:
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Character name", key="cc_name", placeholder="e.g. Nova Starling")
            role = st.text_input("Role / occupation", key="cc_role", placeholder="Time traveller, chef, detective...")
            personality = st.text_input("Personality", key="cc_personality", placeholder="Sarcastic, kind, dramatic...")
            ability = st.text_input("Special ability", key="cc_ability", placeholder="Can hear thoughts, controls weather...")
        with c2:
            age = st.number_input("Age", min_value=1, max_value=150, key="cc_age")
            genre = st.selectbox("Universe", UNIVERSES, key="cc_genre")
            e1, e2 = st.columns(2)
            emoji = e1.selectbox("Avatar", EMOJIS, key="cc_emoji")
            color_pick = e2.color_picker("Theme colour", key="cc_color")
        concept = st.text_area("A little extra detail (optional)", key="cc_concept", height=90,
                               placeholder="A secret, a funny habit, a strange goal...")
        submitted = st.button("✨ Bring this character to life", type="primary", use_container_width=True, key="cc_submit")
    with prev_col:
        st.markdown("##### 👀 Live preview")
        st.markdown(f"""
        <div class="character-tile" style="--accent:{safe_color(color_pick)}">
          <div class="avatar">{esc(emoji)}</div>
          <div class="char-name">{esc(name.strip() or 'Your character')}</div>
          <div class="char-role">{esc(role.strip() or 'Their role')}</div>
          <div class="char-intro">{esc(concept.strip() or 'A few words about them will appear here.')}</div>
          <span class="chip">{esc(genre)}</span>
          <div class="small-muted" style="margin-top:9px">{esc(personality.strip() or 'Personality')}</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("The AI will add a full profile, a secret, an opening line and conversation starters.")

    if submitted:
        if not all([name.strip(), role.strip(), personality.strip(), ability.strip()]):
            notice("warning", "Fill in the name, role, personality and special ability.")
        else:
            lang = language_rule(auto_hint="the character details provided above")
            prompt = f"""
Create an original, age-appropriate fictional character for a chat game.
Name: {name.strip()}
Age: {age}
Role: {role.strip()}
Personality: {personality.strip()}
Universe: {genre}
Special ability: {ability.strip()}
Extra detail: {concept.strip() or 'Invent one fitting detail.'}

Return ONLY a valid JSON object (no markdown fences) with exactly these keys:
"intro": a 1-2 sentence teaser,
"profile": markdown text with short sections: Introduction, Backstory, Strengths, Weakness, Goal, Rival, Famous quote,
"secret": one funny, harmless secret (1 sentence),
"opening": the character's first line when meeting someone (1-2 sentences, in character),
"prompts": an array of 3 short conversation starters a user could say to the character.
Do not change the supplied name or ability. Keep JSON keys in English; the text values follow this rule: {lang}
"""
            try:
                with st.spinner("The universe is inventing someone..."):
                    raw = get_ai_response([{"role": "user", "content": prompt}])
                data = parse_json_block(raw) or {}
                prompts = data.get("prompts")
                new_character = {
                    "id": str(uuid.uuid4()), "name": name.strip(), "emoji": emoji, "role": role.strip(), "age": age,
                    "genre": genre, "vibe": personality.strip(), "personality": personality.strip(), "power": ability.strip(),
                    "intro": str(data.get("intro") or concept.strip() or f"{name.strip()} is a {role.strip()} in a {genre} universe."),
                    "secret": str(data.get("secret") or "A secret waiting to be discovered through conversation."),
                    "opening": str(data.get("opening") or f"Well, hello there. I'm {name.strip()}. What brings you to my corner of the universe?"),
                    "prompts": [str(p) for p in prompts][:4] if isinstance(prompts, list) and prompts else
                               ["Tell me your story.", "What are you hiding?", "Surprise me."],
                    "profile": str(data.get("profile") or raw),
                    "color": color_pick, "custom": True,
                }
                st.session_state.custom_characters.append(new_character)
                st.session_state.selected_character = new_character["id"]
                st.toast(f"{new_character['name']} has entered the universe!", icon=emoji)
                notice("success", f"{new_character['name']} has entered the universe!")
                with st.container(border=True):
                    st.markdown(f"### {emoji} {new_character['name']}")
                    st.markdown(new_character["profile"])
                st.button("💬 Chat with your new character", key="new_character_chat", type="primary",
                          on_click=go_to_chat, args=(new_character["id"],))
            except Exception as error:
                show_error(error)

# =========================================================
# MY CHARACTERS
# =========================================================
elif nav == "My Characters":
    st.markdown("## 📚 Your character collection")
    custom = st.session_state.custom_characters
    if not custom:
        notice("info", "Your collection is empty. The characters you create will appear here.")
        st.button("Create your first character →", on_click=go_to_page, args=("Create",))
    else:
        for character in list(custom):
            cid = character["id"]
            with st.expander(f"{character['emoji']}  {character['name']} — {character['role']}"):
                st.markdown(character.get("profile", character["intro"]))
                st.markdown(f'<span class="chip">🔒 Secret: {esc(character["secret"])}</span>', unsafe_allow_html=True)
                a, b, c = st.columns(3)
                a.button("💬 Chat", key=f"custom_chat_{cid}", type="primary", use_container_width=True, on_click=go_to_chat, args=(cid,))
                b.button("❤️ Unfavourite" if cid in st.session_state.favorites else "🤍 Favourite", key=f"cfav_{cid}",
                         use_container_width=True, on_click=toggle_fav, args=(cid,))
                if c.button("🗑️ Delete", key=f"custom_delete_{cid}", use_container_width=True):
                    st.session_state.custom_characters = [x for x in custom if x["id"] != cid]
                    st.session_state.chat_histories.pop(cid, None)
                    if cid in st.session_state.favorites:
                        st.session_state.favorites.remove(cid)
                    if st.session_state.selected_character == cid:
                        st.session_state.selected_character = None
                    st.rerun()
                with st.form(f"edit_{cid}"):
                    st.markdown("**✏️ Edit**")
                    e1, e2 = st.columns(2)
                    n_name = e1.text_input("Name", value=character["name"], key=f"en_{cid}")
                    n_role = e2.text_input("Role", value=character["role"], key=f"er_{cid}")
                    n_secret = st.text_input("Secret", value=character["secret"], key=f"es_{cid}")
                    n_open = st.text_input("Opening line", value=character["opening"], key=f"eo_{cid}")
                    n_color = st.color_picker("Theme colour", value=safe_color(character.get("color")), key=f"ec_{cid}")
                    if st.form_submit_button("💾 Save changes", use_container_width=True):
                        character.update(name=n_name.strip() or character["name"], role=n_role.strip() or character["role"],
                                         secret=n_secret.strip() or character["secret"],
                                         opening=n_open.strip() or character["opening"], color=n_color)
                        st.toast("Saved!", icon="💾")
                        st.rerun()

# =========================================================
# MYSTERY ROOM
# =========================================================
elif nav == "Mystery Room":
    st.markdown("## 🔐 The Mystery Room")
    st.caption("Read the file, interrogate suspects (in any language), take notes, then make your accusation.")
    solved = st.session_state.solved_cases

    with st.container(border=True):
        st.markdown("#### 🎲 New AI case")
        st.caption("A brand-new case every time: different story, clues, suspects and culprit.")
        g1, g2, g3 = st.columns([1, 2, 1])
        gen_level = g1.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="gen_level")
        gen_theme = g2.text_input("Theme (optional)", key="gen_theme",
                                  placeholder="haunted school, space station, wedding... (blank = random)")
        use_universe = g3.checkbox("Use universe characters", value=True, key="gen_universe")
        if st.button("✨ Generate a new case", type="primary", use_container_width=True, key="gen_case_btn"):
            try:
                with st.spinner("The detective agency is writing a new case..."):
                    new_case = generate_case(gen_level, gen_theme, use_universe)
                st.session_state.ai_cases.append(new_case)
                st.session_state.case_pick = new_case["id"]
                st.toast("New case ready!", icon="🕵️")
            except CaseError:
                notice("error", "The AI's case wasn't valid this time. Please press Generate again.")
            except Exception as error:
                show_error(error)

    case_ids = [c["id"] for c in all_cases()]
    if st.session_state.case_pick not in case_ids:
        st.session_state.case_pick = case_ids[0]

    def case_label(cid):
        c = get_case(cid)
        stars = solved.get(cid)
        return (f"{c['emoji']} {c['title']} · {c['level']}" + ("  🤖 AI" if c.get("ai") else "")
                + (f"   ✅ {'⭐' * int(stars)}" if stars else ""))

    case_id = st.selectbox(f"Choose a case ({len(case_ids)} available)", case_ids, format_func=case_label, key="case_pick")
    case = get_case(case_id)
    names = list(case["suspects"].keys())
    if case.get("ai"):
        st.button("🗑️ Remove this AI case", key=f"rm_{case_id}", on_click=remove_case, args=(case_id,))

    tab_file, tab_ask, tab_notes, tab_accuse = st.tabs(["📜 Case file", "🗣️ Interrogate", "📝 Notebook", "⚖️ Accuse"])

    with tab_file:
        clues = "".join(f'<div class="clue"><b>🔎 Clue {i + 1}</b><span>{esc(t)}</span></div>' for i, t in enumerate(case["clues"]))
        st.markdown(f"""
        <div class="panel">
          <div><span class="lvl {esc(case['level']).lower()}">{esc(case['level'])}</span>{'<span class="lvl ai">AI case</span>' if case.get('ai') else ''}</div>
          <div style="font-size:26px;font-weight:800;color:white;margin:4px 0 8px">{case['emoji']} {esc(case['title'])}</div>
          <p style="margin:0 0 10px">{esc(case['story'])}</p>{clues}
        </div>""", unsafe_allow_html=True)
        st.markdown("### 🕵️ Suspects")
        per_row = 3 if len(case["suspects"]) == 3 else 2
        scols = st.columns(per_row)
        for i, (nm, s) in enumerate(case["suspects"].items()):
            scols[i % per_row].markdown(
                f'<div class="suspect"><div class="sav">{esc(s["emoji"])}</div><div class="nm">{esc(nm)}</div>'
                f'<div class="st">{esc(s["statement"])}</div><div class="ev">👁️ {esc(s["evidence"])}</div></div>',
                unsafe_allow_html=True)

    with tab_ask:
        who = st.selectbox("Who do you want to question?", names, key=f"who_{case_id}",
                           format_func=lambda n: f"{case['suspects'][n]['emoji']} {n}")
        hkey = f"{case_id}:{who}"
        hist = st.session_state.interrogations.setdefault(hkey, [])
        for m in hist:
            is_user = m["role"] == "user"
            with st.chat_message("user" if is_user else "assistant", avatar="🕵️" if is_user else case["suspects"][who]["emoji"]):
                st.markdown(m["content"])
        st.markdown('<div class="small-muted">Quick questions</div>', unsafe_allow_html=True)
        qcols = st.columns(3)
        for i, q in enumerate(["Where were you at the time?", "What did you notice about the others?", "Do you want to change your story?"]):
            qcols[i].button(q, key=f"qq_{case_id}_{i}", use_container_width=True, on_click=set_ask, args=(hkey, q))
        with st.form(f"ask_form_{case_id}", clear_on_submit=True):
            typed_q = st.text_input("Your question", placeholder=f"Ask {who} anything...", key=f"q_{case_id}")
            asked = st.form_submit_button("🗣️ Ask", use_container_width=True)
        question = typed_q.strip() if asked and typed_q.strip() else None
        pend = st.session_state.ask_pending
        if pend and pend[0] == hkey:
            question = pend[1]
        st.session_state.ask_pending = None
        if question:
            with st.chat_message("user", avatar="🕵️"):
                st.markdown(question)
            ok = False
            with st.chat_message("assistant", avatar=case["suspects"][who]["emoji"]):
                try:
                    reply = st.write_stream(stream_ai_response(build_suspect_messages(case, who, hist, question)))
                    hist.append({"role": "user", "content": question})
                    hist.append({"role": "assistant", "content": str(reply).strip()})
                    ok = True
                except Exception as error:
                    show_error(error)
            if ok:
                st.rerun()

    with tab_notes:
        st.text_area("Detective notes", value=st.session_state.notes.get(case_id, ""), key=f"notes_{case_id}", height=220,
                     placeholder="Who has an alibi? Whose evidence doesn't match?", on_change=save_notes, args=(case_id,))
        st.caption("Notes are saved automatically for this case.")

    with tab_accuse:
        attempts = st.session_state.case_attempts.get(case_id, 0)
        stars = solved.get(case_id)
        if stars:
            notice("success", f"You solved this case {'⭐' * int(stars)}. {case['solution']}")
        guess = st.radio("Who did it?", names, index=None, key=f"guess_{case_id}",
                         format_func=lambda n: f"{case['suspects'][n]['emoji']} {n}  —  {case['suspects'][n]['statement']}")
        if attempts:
            st.markdown(f'<div class="small-muted">Attempts so far: {attempts}</div>', unsafe_allow_html=True)
        if st.button("⚖️ Submit accusation", type="primary", use_container_width=True, key=f"acc_{case_id}"):
            if not guess:
                notice("warning", "Choose a suspect first.")
            else:
                st.session_state.case_attempts[case_id] = attempts + 1
                if case["suspects"][guess]["guilty"]:
                    if not stars:
                        solved[case_id] = max(1, 3 - attempts)
                    st.balloons()
                    notice("success", f"Case solved! {case['solution']}")
                else:
                    notice("warning", f"{guess} is innocent. Re-read the evidence and try again.")
                    if attempts + 1 >= 2:
                        notice("info", f"Hint: {case['hint']}")

# =========================================================
# ACHIEVEMENTS
# =========================================================
elif nav == "Achievements":
    st.markdown("## 🏆 Achievements")
    earned = st.session_state.achievements
    st.progress(len(earned) / len(ACHIEVEMENTS))
    st.caption(f"{len(earned)} of {len(ACHIEVEMENTS)} unlocked")
    cols = st.columns(3)
    for i, (aid, (emoji, title, desc)) in enumerate(ACHIEVEMENTS.items()):
        locked = "" if aid in earned else " locked"
        cols[i % 3].markdown(
            f'<div class="badge{locked}"><div class="e">{emoji}</div><div class="t">{esc(title)}</div>'
            f'<div class="d">{esc(desc)}</div></div>', unsafe_allow_html=True)

# ---------- Footer ----------
check_achievements()
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#8994b7;font-size:12px'>"
    "🌌 THE UNKNOWN · Meet characters. Discover secrets. Make a little chaos. "
    "<br>Powered by Ollama Cloud & Streamlit</div>",
    unsafe_allow_html=True,
)
