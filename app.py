
import streamlit as st
import ollama

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AI Character Studio",
    page_icon="🎭",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#0f172a,#111827,#1e1b4b);
    color:white;
}

/* Hide Streamlit branding */

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}


/* Main Container */

.main{
    padding-top:20px;
}


/* Hero */

.hero{
    padding:35px;
    border-radius:25px;
    background:rgba(255,255,255,0.08);
    backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,0.15);
    text-align:center;
    margin-bottom:25px;
}

.hero h1{
    font-size:48px;
    margin-bottom:8px;
}

.hero p{
    font-size:18px;
    color:#d1d5db;
}


/* Section Card */

.card{
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.12);
    backdrop-filter:blur(15px);
    padding:25px;
    border-radius:20px;
}


/* Result Card */

.result{
    background:linear-gradient(
        135deg,
        rgba(99,102,241,0.18),
        rgba(168,85,247,0.12)
    );

    border:1px solid rgba(255,255,255,0.15);
    padding:30px;
    border-radius:25px;
    margin-top:20px;
}


/* Input */

.stTextInput input,
.stNumberInput input{
    background:#111827 !important;
    color:white !important;
    border-radius:12px;
}

.stSelectbox div{
    border-radius:12px;
}


/* Button */

.stButton button{
    width:100%;
    border-radius:14px;
    height:52px;
    font-size:18px;
    font-weight:bold;
    border:none;

    background:linear-gradient(
        90deg,
        #7c3aed,
        #2563eb
    );

    color:white;
    transition:0.3s;
}

.stButton button:hover{
    transform:scale(1.02);
}


/* Divider */

hr{
    border-color:rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# HERO
# -------------------------------------------------

st.markdown("""
<div class="hero">

<h1>🎭 AI Character Studio</h1>

<p>
Create legendary heroes, villains and fantasy characters
using Artificial Intelligence.
</p>

</div>
""", unsafe_allow_html=True)


# -------------------------------------------------
# CHARACTER FORM
# -------------------------------------------------

st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("✨ Create Your Character")

col1,col2=st.columns(2)

with col1:

    name=st.text_input(
        "Character Name",
        placeholder="Example: Aria Storm"
    )

    age=st.number_input(
        "Age",
        min_value=1,
        max_value=150,
        value=21
    )

    occupation=st.text_input(
        "Occupation",
        placeholder="Warrior, Detective, Wizard..."
    )

with col2:

    personality=st.text_input(
        "Personality",
        placeholder="Brave, Funny, Intelligent..."
    )

    power=st.text_input(
        "Superpower",
        placeholder="Fire, Ice, Teleport..."
    )

    genre=st.selectbox(
        "World / Genre",
        [
            "Fantasy",
            "Sci-Fi",
            "Superhero",
            "Mystery",
            "Horror",
            "Adventure",
            "Anime"
        ]
    )

st.markdown("<br>",unsafe_allow_html=True)

generate=st.button("✨ Generate AI Character")

st.markdown('</div>',unsafe_allow_html=True)


# -------------------------------------------------
# GENERATE CHARACTER
# -------------------------------------------------

if generate:

    if name=="" or personality=="" or occupation=="" or power=="":

        st.warning("⚠️ Please complete all character details.")

    else:

        prompt=f"""
You are an expert fictional character designer.

Create an original fictional character.

Name: {name}
Age: {age}
Personality: {personality}
Occupation: {occupation}
Superpower: {power}
World: {genre}

Generate a beautiful character profile with:

Character Introduction

Personality

Backstory

Strengths

Weaknesses

Goals

Special Abilities

Enemy or Rival

Famous Dialogue

Use engaging storytelling and attractive formatting.
"""

        with st.spinner("🤖 AI is designing your character..."):

            response=ollama.generate(
                model="llama3.2",
                prompt=prompt
            )

        st.session_state.character=response["response"]
        st.session_state.name=name
        st.session_state.age=age
        st.session_state.genre=genre
        st.session_state.power=power
        st.session_state.personality=personality


# -------------------------------------------------
# DISPLAY RESULT
# -------------------------------------------------

if "character" in st.session_state:

    st.markdown("<br>",unsafe_allow_html=True)

    st.markdown('<div class="result">',unsafe_allow_html=True)

    st.markdown(
        f"""
# 🎭 {st.session_state.name}

**Age:** {st.session_state.age}

**World:** {st.session_state.genre}

**Power:** {st.session_state.power}

**Personality:** {st.session_state.personality}

---
"""
    )

    st.markdown(st.session_state.character)

    st.markdown('</div>',unsafe_allow_html=True)


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown("<br><br>",unsafe_allow_html=True)

st.caption("AI Character Studio • Powered by Ollama & Streamlit")