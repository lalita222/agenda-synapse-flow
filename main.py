import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURACIÓN IA (VERSIÓN COMPATIBLE) ---
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Configura la GOOGLE_API_KEY en los Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# Usamos 'gemini-pro', que es el nombre más estable y compatible
try:
    model = genai.GenerativeModel("gemini-pro")
except:
    model = genai.GenerativeModel("models/gemini-pro")

# --- 2. CONFIGURACIÓN DE BLOQUES FIJOS ---
BLOQUES_FIJOS = [
    {"dia": "Lunes", "tarea": "Clases", "hora": "18:00 - 20:00"},
    {"dia": "Martes", "tarea": "Clases", "hora": "18:00 - 20:00"},
    {"dia": "Miércoles", "tarea": "Pole Dance", "hora": "16:00 - 18:00"},
    {"dia": "Miércoles", "tarea": "Clases", "hora": "18:00 - 20:00"},
    {"dia": "Jueves", "tarea": "Universidad (B1)", "hora": "13:00 - 15:00"},
    {"dia": "Jueves", "tarea": "Universidad (B2)", "hora": "20:00 - 22:00"},
    {"dia": "Viernes", "tarea": "Clases", "hora": "18:00 - 20:00"},
]

if 'agenda' not in st.session_state:
    st.session_state.agenda = BLOQUES_FIJOS.copy()

# --- 3. DISEÑO VISUAL ---
st.set_page_config(page_title="Synapse & Flow", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0a0b1e; color: white; }
    .stApp { background: #0a0b1e; }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 15px;
        border-left: 5px solid #06b6d4;
        margin-bottom: 10px;
    }
    .fixed-card { border-left: 5px solid #d946ef; }
    .gradient-text {
        background: linear-gradient(90deg, #d946ef, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 40px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFAZ ---
st.markdown('<p class="gradient-text">✨ Synapse & Flow</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Nueva Tarea")
    with st.form("agenda_form"):
        tarea = st.text_input("¿Qué quieres hacer?")
        duracion = st.selectbox("Duración", ["15 min", "30 min", "45 min", "1h", "1h 30min", "2h", "3h"])
        prioridad = st.select_slider("Prioridad", ["Baja", "Media", "Alta"])
        btn_agendar = st.form_submit_button("AGENDAR CON IA")

    if btn_agendar and tarea:
        if not api_key:
            st.error("Falta la API Key en Secrets")
        else:
            with st.spinner("IA organizando tu semana..."):
                viejas = "\n".join([f"{t['dia']} {t['hora']}: {t['tarea']}" for t in st.session_state.agenda])
                prompt = f"Asistente: Bloqueos: {viejas}. Nueva: {tarea} ({duracion}). Prioridad: {prioridad}. Responde corto: Día | Hora | Razón."
                
                try:
                    # Añadimos una configuración de generación para que sea más rápida
                    response = model.generate_content(
                        prompt,
                        generation_config={"max_output_tokens": 100, "temperature": 0.5}
                    )
                    
                    res_text = response.text
                    
                    if "|" in res_text:
                        partes = res_text.split("|")
                        dia_sug = partes[0].replace("Día:", "").strip()
                        hora_sug = partes[1].strip()
                        st.session_state.agenda.append({"dia": dia_sug, "tarea": tarea, "hora": hora_sug})
                        st.rerun() # Esto refresca la pantalla de inmediato
                    else:
                        st.warning("La IA respondió en un formato extraño. Intenta de nuevo.")
                        
                except Exception as e:
                    st.error(f"Se agotó el tiempo o hubo un error: {e}")
    if st.button("🗑️ REINICIAR SEMANA"):
        st.session_state.agenda = BLOQUES_FIJOS.copy()
        st.rerun()

with col2:
    st.subheader("📅 Cronograma Semanal")
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    for d in dias_semana:
        tareas_dia = [t for t in st.session_state.agenda if d in t['dia']]
        if tareas_dia:
            st.markdown(f"### {d}")
            for t in tareas_dia:
                estilo = "fixed-card" if any(f['tarea'] == t['tarea'] for f in BLOQUES_FIJOS) else ""
                st.markdown(f"""
                <div class="glass-card {estilo}">
                    <strong>{t['hora']}</strong> - {t['tarea']}
                </div>
                """, unsafe_allow_html=True)
