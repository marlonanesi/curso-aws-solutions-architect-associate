import streamlit as st
import os
import time
import threading
import psutil
import requests

# Função para identificar a instância EC2
def get_instance_id():
    try:
        response = requests.get("http://169.254.169.254/latest/meta-data/instance-id", timeout=2)
        if response.status_code == 200:
            return response.text
    except:
        pass
    try:
        token_response = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        )
        if token_response.status_code == 200:
            token = token_response.text
            response = requests.get(
                "http://169.254.169.254/latest/meta-data/instance-id",
                headers={"X-aws-ec2-metadata-token": token},
                timeout=2
            )
            return response.text
    except:
        pass
    return "ID não disponível"

# Funções de stress
def stress_cpu(duration):
    end = time.time() + duration
    while time.time() < end:
        _ = 12345 ** 12345

def stress_mem(size_mb, duration):
    data = []
    end = time.time() + duration
    try:
        while time.time() < end:
            data.append(bytearray(1024 * 1024 * size_mb))
            time.sleep(1)
    except MemoryError:
        pass

def stress_io(duration):
    end = time.time() + duration
    with open("stress_test.tmp", "wb") as f:
        while time.time() < end:
            f.write(os.urandom(1024 * 1024))  # 1MB
    os.remove("stress_test.tmp")

# Interface Streamlit
st.set_page_config(page_title="Stress Test EC2", layout="centered")
st.title("💥 Stress Test EC2 Instance")

instance_id = get_instance_id()
st.markdown(f"🖥️ **Instância EC2**: `{instance_id}`")

st.header("📊 Status Atual dos Recursos")
col1, col2, col3 = st.columns(3)
col1.metric("CPU (%)", f"{psutil.cpu_percent()}%")
col2.metric("RAM (%)", f"{psutil.virtual_memory().percent}%")
col3.metric("Disco (%)", f"{psutil.disk_usage('/').percent}%")

st.divider()

st.header("⚙️ Rodar Stress Test")

test_type = st.selectbox("Tipo de teste", ["CPU", "Memória", "I/O"])
duration = st.slider("Duração (segundos)", 5, 120, 10)

if test_type == "Memória":
    size_mb = st.slider("Tamanho do bloco (MB)", 10, 500, 100)
else:
    size_mb = None

if st.button("Iniciar Stress Test"):
    st.info("Teste iniciado! Aguarde...")
    def run_stress():
        if test_type == "CPU":
            stress_cpu(duration)
        elif test_type == "Memória":
            stress_mem(size_mb, duration)
        elif test_type == "I/O":
            stress_io(duration)
        st.success("Teste finalizado!")
    thread = threading.Thread(target=run_stress)
    thread.start()