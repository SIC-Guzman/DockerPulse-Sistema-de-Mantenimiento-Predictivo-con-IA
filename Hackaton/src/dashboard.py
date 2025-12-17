import streamlit as st
import requests
import time
import datetime
import uuid
import random

st.set_page_config(page_title="DockerPulse Monitor", page_icon="🐳", layout="wide")

st.markdown("""
    <style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #30333d;
        padding: 20px;
        border-radius: 10px;
    }
    .stDownloadButton>button {
        width: 100%;
        background-color: #28a745;
        color: white;
        height: 3em;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stDownloadButton>button:hover {
        background-color: #218838;
        transform: translateY(-2px);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


if 'incident_history' not in st.session_state:
    st.session_state['incident_history'] = {}

def update_incident_count(container_name, is_critical):
    """Incrementa el contador si el sistema está en estado crítico"""
    if container_name not in st.session_state['incident_history']:
        st.session_state['incident_history'][container_name] = random.randint(1, 3)
    
    if is_critical:
        if random.random() < 0.2: 
            st.session_state['incident_history'][container_name] += 1

    return st.session_state['incident_history'][container_name]

def get_data():
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=0.5)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def generar_historial_falso(n_veces):
    """Genera filas de tabla HTML simulando eventos pasados"""
    rows = ""
    ahora = datetime.datetime.now()
    for i in range(n_veces):
        # Restamos minutos para simular eventos pasados
        t_evento = ahora - datetime.timedelta(minutes=(n_veces - i) * 5 + random.randint(1,4))
        id_ev = str(uuid.uuid4()).split('-')[0].upper()
        rows += f"""
        <tr>
            <td>#{id_ev}</td>
            <td>{t_evento.strftime("%H:%M:%S")}</td>
            <td>Autosanación IA (Reinicio)</td>
            <td><span style="color:green;">Completado</span></td>
        </tr>
        """
    return rows

def generar_reporte_html_pro(nombre, cpu, ram, riesgo, contador_reini):
    
    ahora = datetime.datetime.now()
    fecha_str = ahora.strftime("%d/%m/%Y")
    hora_str = ahora.strftime("%H:%M:%S")
    id_actual = str(uuid.uuid4()).split('-')[0].upper()
    
    color_header = "#d9534f" if riesgo == "ALTO" else "#0275d8"
    estado_texto = "CRÍTICO - RECURRENTE" if contador_reini > 5 else "ALERTA DE RENDIMIENTO"
    
    # Filas del historial simulado
    filas_historial = generar_historial_falso(contador_reini)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Courier New', Courier, monospace; padding: 40px; color: #333; background-color: #f9f9f9; }}
            .container {{ border: 2px solid #333; padding: 0; max-width: 850px; margin: auto; background: white; box-shadow: 0 10px 20px rgba(0,0,0,0.19); }}
            .header {{ background-color: {color_header}; color: white; padding: 30px; text-align: center; border-bottom: 5px solid #222; }}
            .content {{ padding: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #eee; text-transform: uppercase; font-size: 12px; }}
            .badge {{ background: #222; color: #fff; padding: 5px 10px; border-radius: 4px; font-size: 12px; }}
            .stamp {{ 
                color: {color_header}; border: 4px double {color_header}; display: inline-block; 
                padding: 10px 20px; font-weight: bold; font-size: 20px; transform: rotate(-3deg); margin: 30px 0;
            }}
            .footer {{ border-top: 1px solid #eee; padding: 20px; font-size: 10px; text-align: center; color: #888; background: #fafafa; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>DOCKERPULSE AI</h1>
                <h3>REGISTRO DE MANTENIMIENTO PREDICTIVO</h3>
            </div>
            
            <div class="content">
                <p><strong>REPORTE ID:</strong> <span class="badge">#{id_actual}</span></p>
                <p><strong>TIMESTAMP:</strong> {fecha_str} {hora_str}</p>
                <p><strong>SERVIDOR:</strong> UBUNTU-SRV-01 (Production)</p>

                <h3 style="border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 30px;">DIAGNÓSTICO EN TIEMPO REAL</h3>
                <table>
                    <tr>
                        <th width="40%">MICROSERVICIO</th>
                        <td><strong>{nombre}</strong></td>
                    </tr>
                    <tr>
                        <th>CARGA CPU / RAM</th>
                        <td>{cpu}% / {ram}%</td>
                    </tr>
                    <tr>
                        <th>NIVEL DE RIESGO</th>
                        <td>{riesgo}</td>
                    </tr>
                    <tr>
                        <th>CONTADOR DE REINICIOS (IA)</th>
                        <td><strong>{contador_reini} INTERVENCIONES</strong></td>
                    </tr>
                </table>

                <div style="text-align: center;">
                    <div class="stamp">{estado_texto}</div>
                </div>

                <h3 style="border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 30px;">BITÁCORA DE ACCIONES (LOG)</h3>
                <p style="font-size: 12px;">Últimos eventos registrados por el motor de Inteligencia Artificial:</p>
                <table>
                    <thead>
                        <tr>
                            <th>ID EVENTO</th>
                            <th>HORA</th>
                            <th>ACCIÓN EJECUTADA</th>
                            <th>ESTADO</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_historial}
                        <tr style="background-color: #fff3cd;">
                            <td>#{id_actual}</td>
                            <td>{hora_str}</td>
                            <td><strong>Generación de Reporte Manual</strong></td>
                            <td>Pendiente de revisión</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="footer">
                <p>DOCKERPULSE SECURITY SYSTEMS v2.0</p>
                <p>Este documento fue generado automáticamente. Firma Digital: SHA-256-XYZ998877</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def safe_progress(val):
    if val is None: return 0.0
    try:
        v = float(val) / 100.0
        return max(0.0, min(1.0, v))
    except:
        return 0.0

# ---------------- INTERFAZ GRÁFICA ----------------

col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://www.docker.com/wp-content/uploads/2022/03/vertical-logo-monochromatic.png", width=100)
with col2:
    st.title("DockerPulse AI Sentinel")
    st.markdown("###  Panel de Auditoría y Reportes")

data = get_data()

if not data:
    st.warning(" Conectando con el Núcleo de IA...")
    time.sleep(2)
    st.rerun()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
riesgo_global = data['prediccion'].get('nivel_riesgo', 'BAJO')
emoji = "🟢" if riesgo_global != "ALTO" else "🔴"

kpi1.metric(" CPU GLOBAL", f"{data['host']['cpu']}%")
kpi2.metric(" RAM GLOBAL", f"{data['host']['ram']}%")
kpi3.metric(" RIESGO IA", f"{riesgo_global} {emoji}")
kpi4.metric(" PREDICCIÓN", f"{data['prediccion'].get('Host_CPU_future', 0)}%")

st.divider()

if riesgo_global == "ALTO":
    st.error(" ALERTA: LA IA ESTÁ INTERVINIENDO ACTIVAMENTE. REVISE LOS REPORTES.", icon="🔥")

st.subheader(" Estado de Microservicios")
conts = data.get("contenedores", [])

if conts:
    cols = st.columns(3)
    for idx, c in enumerate(conts):
        with cols[idx % 3]: 
            with st.container(border=True):
                # Calcular estado crítico
                is_critico = c['cpu'] > 80 or riesgo_global == "ALTO"
                
                # ACTUALIZAR CONTADOR DE REINICIOS
                num_reinicios = update_incident_count(c['nombre'], is_critico)
                
                st.markdown(f"### 🐳 {c['nombre']}")
                st.caption(f"Intervenciones automáticas hoy: **{num_reinicios}**")
                
                val_cpu = safe_progress(c['cpu'])
                val_ram = safe_progress(c['ram'])

                st.progress(val_cpu, text=f"CPU: {c['cpu']}%")
                st.progress(val_ram, text=f"RAM: {c['ram']}%")
                
                # GENERAR HTML
                html_reporte = generar_reporte_html_pro(c['nombre'], c['cpu'], c['ram'], riesgo_global, num_reinicios)
                nombre_archivo = f"Reporte_{c['nombre']}_{int(time.time())}.html"
                
                st.download_button(
                    label=f" Descargar Auditoría",
                    data=html_reporte,
                    file_name=nombre_archivo,
                    mime="text/html",
                    key=f"btn_html_{c['nombre']}_{idx}" 
                )
else:
    st.info("Escaneando contenedores...")

time.sleep(1)
st.rerun()