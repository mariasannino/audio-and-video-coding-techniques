import streamlit as st
import requests
import os
import json

# GUI accesible en http://localhost:8000

# ==============================================================================
# 1. CONFIGURACION Y FUNCIONES DE LA API
# ==============================================================================

# Usamos el nombre del servicio de Docker Compose ('api') como hostname
# para comunicarnos entre contenedores.
API_HOST = os.getenv("API_HOST", "http://api:80")

def call_convert(codec_name):
    """Llama al endpoint /video/convert."""
    url = f"{API_HOST}/video/convert"
    payload = {"codec": codec_name}
    st.info(f"Enviando solicitud POST a {url} con codec: {codec_name}")
    try:
        # 5 minutos de timeout para la conversion
        response = requests.post(url, json=payload, timeout=300) 
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexion con la API: {e}")
        return None

def call_ladder(profiles_data):
    """Llama al endpoint /video/ladder."""
    url = f"{API_HOST}/video/ladder"
    payload = {"profiles": profiles_data}
    st.info(f"Enviando solicitud POST a {url} con {len(profiles_data)} perfiles.")
    try:
        # 10 minutos de timeout para la escalera de codificacion
        response = requests.post(url, json=payload, timeout=600) 
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexion con la API: {e}")
        return None

# ==============================================================================
# 2. INTERFAZ GRAFICA (STREAMLIT)
# ==============================================================================

st.set_page_config(layout="wide", page_title="Monster API GUI")

st.title("Monster API - Video Processing Interface")
st.markdown("Use esta interfaz para interactuar con su API de conversion y encoding ladder.")

tab1, tab2 = st.tabs(["Conversion Simple", "Encoding Ladder"])

# --- Tab 1: Conversion Simple ---
with tab1:
    st.header("Conversion a un solo Codec")
    st.markdown("El video de entrada es siempre **`input_files/input.mp4`** (en el volumen compartido).")
    
    codecs = ["vp8", "vp9", "h265", "av1"]
    
    selected_codec = st.selectbox(
        "Seleccione el Codec de Salida:",
        options=codecs,
        index=0
    )
    
    if st.button("Iniciar Conversion Simple", key="convert_button"):
        st.write(f"Iniciando conversion a **{selected_codec.upper()}**...")
        
        with st.spinner("Procesando video... Esto puede tardar varios segundos."):
            response = call_convert(selected_codec)
        
        if response and response.status_code == 200:
            try:
                result = response.json()
                st.success("¡Conversion completada exitosamente!")
                st.json(result)
                st.markdown(f"**Archivo de salida generado en la carpeta compartida:** `{result['output']}`")
            except json.JSONDecodeError:
                st.error("La API devolvio una respuesta no JSON (Internal Server Error)")
                st.code(response.text)
        elif response and response.status_code != 200:
            st.error(f"Error en la API (Status: {response.status_code})")
            try:
                st.json(response.json())
            except json.JSONDecodeError:
                st.code(response.text)

# --- Tab 2: Encoding Ladder ---

# Estado para gestionar los perfiles de la escalera
if 'profiles' not in st.session_state:
    st.session_state.profiles = []

with tab2:
    st.header("Configuracion de Encoding Ladder")
    st.markdown("Defina multiples perfiles de salida (bitrate y resolucion).")
    
    # Formulario para agregar un nuevo perfil
    with st.form(key='add_profile_form'):
        col1, col2, col3, col4 = st.columns(4)
        
        new_codec = col1.selectbox("Codec:", options=["vp8", "vp9", "h265", "av1"], index=0, key="new_codec")
        new_bitrate = col2.text_input("Bitrate (ej: 1000k):", value="1500k", key="new_bitrate")
        new_resolution = col3.text_input("Resolucion (ej: 1280x720):", value="1280x720", key="new_resolution")
        new_prefix = col4.text_input("Prefijo de Salida (ej: HD):", value="HD", key="new_prefix")
        
        submit_profile = st.form_submit_button("Agregar Perfil")
        
        if submit_profile:
            profile = {
                "codec": new_codec,
                "bitrate": new_bitrate,
                "resolution": new_resolution,
                "output_prefix": new_prefix
            }
            # Validacion simple
            if new_bitrate and new_resolution and new_prefix:
                st.session_state.profiles.append(profile)
                st.success(f"Perfil '{new_prefix}' agregado.")
            else:
                st.warning("Debe rellenar todos los campos del perfil.")

    st.subheader("Perfiles de la Escalera Actual:")
    
    # Mostrar y gestionar perfiles
    if st.session_state.profiles:
        st.dataframe(st.session_state.profiles, use_container_width=True)
        
        if st.button("Limpiar Todos los Perfiles", key="clear_profiles"):
            st.session_state.profiles = []
            st.rerun() 
            
    else:
        st.warning("No hay perfiles configurados. Por favor, agregue uno.")

    # Boton principal para iniciar el Ladder
    if st.session_state.profiles:
        st.markdown("---")
        if st.button("Iniciar Encoding Ladder", key="ladder_button"):
            
            # Mapear los perfiles a la estructura JSON que espera la API
            profiles_to_send = st.session_state.profiles
            
            with st.spinner(f"Procesando {len(profiles_to_send)} videos en la escalera..."):
                response = call_ladder(profiles_to_send)
            
            if response and response.status_code == 200:
                try:
                    result = response.json()
                    st.balloons()
                    st.success("Encoding Ladder completado exitosamente.")
                    st.dataframe(result['results'], use_container_width=True)
                except json.JSONDecodeError:
                    st.error("La API devolvio una respuesta no JSON (Internal Server Error)")
                    st.code(response.text)

            elif response and response.status_code != 200:
                st.error(f"Error en la API (Status: {response.status_code})")
                try:
                    st.json(response.json())
                except json.JSONDecodeError:
                    st.code(response.text)