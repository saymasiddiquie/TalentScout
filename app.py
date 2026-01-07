import os
import uuid
import json
import datetime
import random
import streamlit as st
from openai import OpenAI

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def is_end_message(text: str) -> bool:
    """Checks if the user wants to end the conversation."""
    if not text: return False
    triggers = ["bye", "exit", "quit", "stop", "thank you", "thanks", "done", "end"]
    return text.lower().strip().strip(".,!") in triggers

def analyze_sentiment(text: str) -> str:
    """Simple rule-based sentiment analysis."""
    if not text: return "neutral"
    text = text.lower()
    positive = ["yes", "sure", "confident", "good", "great", "love", "proficient", "experienced", "excited", "definitely", "absolutely", "strong", "enjoy", "passionate", "proud", "expert", "skilled", "start"]
    negative = ["no", "not", "bad", "hate", "struggle", "unsure", "weak", "never", "confused", "difficult", "boring", "scared", "worst", "don't know"]
    pos_score = sum(1 for w in positive if w in text)
    neg_score = sum(1 for w in negative if w in text)
    if pos_score > neg_score: return "positive"
    elif neg_score > pos_score: return "negative"
    return "neutral"

def detect_language_input(user_text: str):
    """Detects language choice from user input."""
    text = user_text.lower().strip()
    
    # Map common keywords to language keys
    if any(x in text for x in ["english", "eng", "inglés"]): return "English"
    if any(x in text for x in ["spanish", "español", "esp", "castellano"]): return "Spanish"
    if any(x in text for x in ["french", "français", "francais", "french"]): return "French"
    if any(x in text for x in ["hindi", "hind", "हिंदी"]): return "Hindi"
    
    return None

def persist_candidate(session_id: str, profile: dict, chat_history: list):
    """Saves candidate data to local JSON."""
    if not os.path.exists("data"): os.makedirs("data")
    filename = f"data/{session_id}.json"
    data = {"timestamp": str(datetime.datetime.now()), "profile": profile, "chat_history": chat_history}
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Save failed: {e}")

def chat_completion(messages, model="gpt-4o-mini", temperature=0.7, max_tokens=150):
    """Wrapper for OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if not api_key: return None
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM Error: {e}")
        return None

# ==========================================
# 2. CONFIGURATION & TRANSLATIONS
# ==========================================

st.set_page_config(page_title="TalentScout | AI Hiring Assistant", page_icon="🤖", layout="centered", initial_sidebar_state="expanded")

TRANSLATIONS = {
    "English": {
        "greeting": "Hello! I’m TalentScout. I’ll collect a few details and then conduct a technical assessment. Say **bye** to exit.\n\n**Shall we start?**",
        "q_name": "First, what is your full name?",
        "q_email": "What is your email address?",
        "q_phone": "What is your phone number?",
        "q_role": "What position are you applying for?",
        "q_yoe": "How many years of experience do you have?",
        "q_loc": "Where are you currently located?",
        "q_stack": "Finally, please list your Tech Stack (e.g., Python, SQL, React).",
        "end": "Thank you! The interview is complete. A recruiter will be in touch.",
        "wait": "Okay, standing by. Type **'start'** when ready.",
        "download": "📥 Download Transcript"
    },
    "Spanish": {
        "greeting": "¡Hola! Soy TalentScout. Recopilaré algunos detalles y haré una evaluación técnica. Di **adiós** para salir.\n\n**¿Empezamos?**",
        "q_name": "Primero, ¿cuál es tu nombre completo?",
        "q_email": "¿Cuál es tu correo electrónico?",
        "q_phone": "¿Cuál es tu número de teléfono?",
        "q_role": "¿A qué puesto estás aplicando?",
        "q_yoe": "¿Cuántos años de experiencia tienes?",
        "q_loc": "¿Dónde te encuentras actualmente?",
        "q_stack": "Finalmente, lista tu Tech Stack (ej. Python, SQL, React).",
        "end": "¡Gracias! La entrevista ha terminado. Un reclutador te contactará.",
        "wait": "Bien, espera. Escribe **'empezar'** cuando estés listo.",
        "download": "📥 Descargar Transcripción"
    },
    "French": {
        "greeting": "Bonjour! Je suis TalentScout. Je vais recueillir quelques détails puis effectuer une évaluation technique. Dites **au revoir** pour quitter.\n\n**On commence?**",
        "q_name": "Tout d'abord, quel est votre nom complet?",
        "q_email": "Quel est votre adresse email?",
        "q_phone": "Quel est votre numéro de téléphone?",
        "q_role": "Pour quel poste postulez-vous?",
        "q_yoe": "Combien d'années d'expérience avez-vous?",
        "q_loc": "Où êtes-vous actuellement situé?",
        "q_stack": "Enfin, veuillez lister votre Tech Stack (ex. Python, SQL, React).",
        "end": "Merci! L'entretien est terminé. Un recruteur vous contactera.",
        "wait": "D'accord. Tapez **'commencer'** quand vous êtes prêt.",
        "download": "📥 Télécharger la transcription"
    },
    "Hindi": {
        "greeting": "नमस्ते! मैं TalentScout हूँ। मैं कुछ विवरण एकत्र करूँगा और फिर तकनीकी मूल्यांकन करूँगा। बाहर निकलने के लिए **bye** कहें।\n\n**क्या हम शुरू करें?**",
        "q_name": "सबसे पहले, आपका पूरा नाम क्या है?",
        "q_email": "आपका ईमेल पता क्या है?",
        "q_phone": "आपका फोन नंबर क्या है?",
        "q_role": "आप किस पद के लिए आवेदन कर रहे हैं?",
        "q_yoe": "आपके पास कितने साल का अनुभव है?",
        "q_loc": "आप वर्तमान में कहाँ स्थित हैं?",
        "q_stack": "अंत में, कृपया अपनी Tech Stack बताएं (जैसे Python, SQL, React)।",
        "end": "धन्यवाद! साक्षात्कार पूरा हो गया है। एक रिक्रूटर आपसे संपर्क करेगा।",
        "wait": "ठीक है। तैयार होने पर **'start'** टाइप करें।",
        "download": "📥 ट्रांसक्रिप्ट डाउनलोड करें"
    }
}

# ==========================================
# 3. SESSION STATE
# ==========================================
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state: st.session_state.messages = []
if "profile" not in st.session_state: st.session_state.profile = {"full_name": "", "email": "", "phone": "", "desired_positions": "", "years_of_experience": "", "current_location": "", "tech_stack": ""}
if "ended" not in st.session_state: st.session_state.ended = False
if "intro_ack" not in st.session_state: st.session_state.intro_ack = False
if "current_field" not in st.session_state: st.session_state.current_field = None
if "sentiments" not in st.session_state: st.session_state.sentiments = []
if "asked_questions_set" not in st.session_state: st.session_state.asked_questions_set = set()
if "phase" not in st.session_state: st.session_state.phase = "personal"
if "tech_start_idx" not in st.session_state: st.session_state.tech_start_idx = 0
if "language" not in st.session_state: st.session_state.language = "English"
# NEW STATE: To track if language is selected via chat
if "language_confirmed" not in st.session_state: st.session_state.language_confirmed = False

# Defaults
if "consent" not in st.session_state: st.session_state.consent = False
if "base_url" not in st.session_state: st.session_state.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
if "model" not in st.session_state: st.session_state.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=60)
    st.title("Settings")
    
    # You can still use the sidebar, but chat takes precedence
    st.session_state.language = st.selectbox("Current Language", list(TRANSLATIONS.keys()), index=list(TRANSLATIONS.keys()).index(st.session_state.language))
    
    st.markdown("---")
    st.caption("Configuration")
    st.session_state.base_url = st.text_input("API Base URL", value=st.session_state.base_url)
    st.session_state.model = st.text_input("Model", value=st.session_state.model)
    st.session_state.consent = st.checkbox("I consent to data processing (GDPR)", value=st.session_state.consent)
    
    st.markdown("---")
    st.subheader("Profile Progress")
    filled = sum(1 for k, v in st.session_state.profile.items() if v)
    st.progress(filled / 7)
    
    if st.button("🔄 Restart Interview", type="primary", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# ==========================================
# 5. UI STYLING
# ==========================================
st.markdown("""
<style>
  @keyframes twinkle {0%,100%{opacity:.8}50%{opacity:.3}}
  @keyframes shoot { 0% { transform: rotate(45deg) translateX(0); opacity: 0; } 15% { opacity: 1; } 100% { transform: rotate(45deg) translateX(120vw); opacity: 0; } }
  .stApp { background-color: transparent !important; }
  header[data-testid="stHeader"] { background-color: transparent !important; }
  div[data-testid="stBottom"] { background-color: transparent !important; border-top: none !important; }
  .bg-sky { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; overflow: hidden; background: linear-gradient(to bottom, #020105 0%, #0f172a 100%); }
  .stars { position:absolute; inset:0; background-image: radial-gradient(1.5px 1.5px at 10% 10%, white 50%, transparent 51%), radial-gradient(1px 1px at 20% 80%, white 50%, transparent 51%); background-size: 550px 550px; animation: twinkle 4s ease-in-out infinite alternate; opacity: 0.8; }
  .shooting-star { position: absolute; top: -50px; left: 20%; width: 4px; height: 4px; background: #fff; border-radius: 50%; box-shadow: 0 0 0 4px rgba(255,255,255,0.1), 0 0 0 8px rgba(255,255,255,0.1), 0 0 20px rgba(255,255,255,1); animation: shoot 7s linear infinite; opacity: 0; }
  .shooting-star::before { content: ''; position: absolute; top: 50%; transform: translateY(-50%); width: 200px; height: 1px; background: linear-gradient(90deg, #fff, transparent); right: 1px; }
  
  /* Header & Chips */
  .header-wrap { padding: 30px; border-radius: 20px; background: linear-gradient(135deg, rgba(14, 165, 233, 0.9) 0%, rgba(99, 102, 241, 0.9) 100%); backdrop-filter: blur(10px); border: 2px solid rgba(255,255,255,0.3); text-align: center; margin-bottom: 30px; box-shadow: 0 0 30px rgba(99, 102, 241, 0.5); }
  .header-wrap.technical { background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%); box-shadow: 0 0 30px rgba(236, 72, 153, 0.5); }
  .title { font-size: 3rem; font-weight: 900; margin-bottom: 5px; color: white; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
  .subtle { opacity: 0.95; font-size: 1.3rem; color: white; font-weight: 500; }
  .chips-container { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 20px; }
  .chip { padding: 8px 16px; border-radius: 50px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); font-size: 1rem; color: white; }
  .chip.filled { background: linear-gradient(90deg, #00c6ff, #0072ff); border: 1px solid #00c6ff; box-shadow: 0 0 15px rgba(0, 198, 255, 0.6); font-weight: bold; transform: scale(1.05); }

  /* Chat */
  [data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; margin-bottom: 10px; overflow: visible !important; }
  .chat-bubble { padding: 1.5rem; border-radius: 18px; position: relative; display: inline-block; max-width: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.2); backdrop-filter: blur(5px); font-size: 1.1rem; line-height: 1.5; }
  .chat-bubble.assistant { background: rgba(240, 248, 255, 0.95); color: #0f172a; border-top-left-radius: 4px; border: 1px solid rgba(255,255,255,0.8); }
  .chat-bubble.user { background: rgba(15, 17, 42, 0.9); color: #f1f5f9; border-top-right-radius: 4px; border: 1px solid rgba(100, 150, 255, 0.3); }
  .sent-badge { font-size: 0.75rem; padding: 3px 8px; border-radius: 8px; margin-top: 8px; display: inline-block; font-weight: bold; opacity: 0.9; }
  .sent-positive { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
  .sent-neutral { background-color: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid #94a3b8; }
  .sent-negative { background-color: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid #ef4444; }
  [data-testid="stSidebar"] { background-color: #f0f2f6; border-right: 1px solid #e5e7eb; }
</style>
<div class='bg-sky'><div class='stars'></div><div class='shooting-star'></div></div>
""", unsafe_allow_html=True)

# ==========================================
# 6. HEADER RENDERING
# ==========================================
header_title = "TalentScout 🤖"
header_sub = "Hiring Assistant"
header_class = ""
if st.session_state.phase == "technical":
    header_title = "Technical Assessment"
    header_sub = f"Evaluating: {st.session_state.profile.get('tech_stack', 'Tech Stack')}"
    header_class = "technical"

chip_html = ""
labels = {"full_name": "Name", "email": "Email", "phone": "Phone", "desired_positions": "Role", "years_of_experience": "YoE", "current_location": "Loc", "tech_stack": "Stack"}
for k, l in labels.items():
    v = str(st.session_state.profile.get(k) or "").strip()
    status = "filled" if v else "empty"
    icon = "✓" if v else "○"
    chip_html += f"<span class='chip {status}'>{icon} {l}</span>"

st.markdown(f"<div class='header-wrap {header_class}'><div class='title'>{header_title}</div><div class='subtle'>{header_sub}</div><div class='chips-container'>{chip_html}</div></div>", unsafe_allow_html=True)

# ==========================================
# 7. LOGIC
# ==========================================
def get_text(key): return TRANSLATIONS.get(st.session_state.language, TRANSLATIONS["English"]).get(key, "")

def generate_local_fallback_question(tech_list):
    if not tech_list: tech_list = ["software development", "problem solving"]
    tech = random.choice(tech_list)
    return f"How do you handle debugging in {tech}?"

def generate_unique_question(tech_stack, history):
    lang = st.session_state.language
    tech_list = [t.strip() for t in tech_stack.replace(",", " ").split() if t.strip()] if tech_stack else ["General Programming"]
    for _ in range(5):
        try:
            tech = random.choice(tech_list)
            prompt = f"Ask a specific technical question about '{tech}' in {lang}. Short and direct."
            resp = chat_completion([{"role": "system", "content": prompt}], model=st.session_state.model, max_tokens=60)
            if resp and resp not in history: return resp
        except: pass
    return generate_local_fallback_question(tech_list)

def get_next_response(user_text):
    p = st.session_state.profile
    if st.session_state.current_field:
        val = user_text.strip()
        if val: p[st.session_state.current_field] = val
        st.session_state.current_field = None

    checks = [
        ("full_name", "q_name"), ("email", "q_email"), ("phone", "q_phone"),
        ("desired_positions", "q_role"), ("years_of_experience", "q_yoe"),
        ("current_location", "q_loc"), ("tech_stack", "q_stack")
    ]
    for key, text_key in checks:
        if not p.get(key):
            st.session_state.current_field = key
            return get_text(text_key)

    if st.session_state.phase == "personal":
        st.session_state.phase = "technical"
        st.session_state.tech_start_idx = len(st.session_state.messages)

    if len(st.session_state.asked_questions_set) >= 5:
        st.session_state.ended = True
        if st.session_state.consent: persist_candidate(st.session_state.session_id, p, st.session_state.messages)
        return get_text("end")

    q = generate_unique_question(p["tech_stack"], st.session_state.asked_questions_set)
    st.session_state.asked_questions_set.add(q)
    return f"Q{len(st.session_state.asked_questions_set)}: {q}"

# ==========================================
# 8. MAIN LOOP
# ==========================================

# A. Language Negotiation Phase
if not st.session_state.language_confirmed:
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "👋 Hello! In which language would you like to continue? (English, Spanish, French, Hindi)"})

    # Show existing messages (likely just the prompt)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(f"<div class='chat-bubble {m['role']}'>{m['content']}</div>", unsafe_allow_html=True)
    
    # Input for Language Selection
    lang_input = st.chat_input("Type your language...")
    if lang_input:
        detected = detect_language_input(lang_input)
        st.session_state.messages.append({"role": "user", "content": lang_input})
        
        if detected:
            st.session_state.language = detected
            st.session_state.language_confirmed = True
            # Add the actual Greeting
            st.session_state.messages.append({"role": "assistant", "content": get_text("greeting")})
            st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": "I didn't catch that. Please choose: English, Spanish, French, or Hindi."})
            st.rerun()

# B. Main Interview Phase (Only after language is set)
else:
    visible_messages = st.session_state.messages
    if st.session_state.phase == "technical":
        start = st.session_state.tech_start_idx
        if start < len(st.session_state.messages):
            visible_messages = st.session_state.messages[start:]

    for m in visible_messages:
        with st.chat_message(m["role"]):
            role = "user" if m["role"] == "user" else "assistant"
            sent_html = ""
            if st.session_state.phase == "personal" and role == "user":
                try:
                    u_msgs = [x for x in st.session_state.messages if x['role'] == 'user']
                    if m in u_msgs:
                        idx = u_msgs.index(m)
                        if idx < len(st.session_state.sentiments):
                            s = st.session_state.sentiments[idx]
                            sent_html = f"<div class='sent-badge sent-{s}'>{s.upper()}</div>"
                except: pass
            st.markdown(f"<div class='chat-bubble {role}'>{m['content']}{sent_html}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your answer here...")

    if user_input and not st.session_state.ended:
        st.session_state.sentiments.append(analyze_sentiment(user_input))

        if is_end_message(user_input):
            st.session_state.ended = True
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": get_text("end")})
            if st.session_state.consent: persist_candidate(st.session_state.session_id, st.session_state.profile, st.session_state.messages)
            st.rerun()

        st.session_state.messages.append({"role": "user", "content": user_input})
        
        if not st.session_state.intro_ack:
            triggers = ["yes", "y", "start", "sure", "ok", "go", "empezar", "commencer", "shuru", "si", "oui", "haan"]
            if any(x in user_input.lower() for x in triggers):
                st.session_state.intro_ack = True
                reply = get_next_response("")
            else:
                reply = get_text("wait")
        else:
            reply = get_next_response(user_input)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ==========================================
# 9. DOWNLOAD
# ==========================================
if st.session_state.ended:
    transcript = json.dumps({"profile": st.session_state.profile, "chat": st.session_state.messages, "timestamp": str(datetime.datetime.now())}, indent=2)
    st.download_button(label=get_text("download"), data=transcript, file_name=f"interview_{st.session_state.profile.get('full_name','candidate')}.json", mime="application/json", type="primary")