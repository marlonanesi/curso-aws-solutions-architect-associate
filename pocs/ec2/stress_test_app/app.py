import streamlit as st
import requests
import subprocess
import psutil
import os
import time
from datetime import datetime

# Função para identificar a instância EC2 (mantida para compatibilidade)
def get_instance_id():
    return get_metadata("instance-id") or "ID não disponível"

def get_metadata(endpoint):
    """Função auxiliar para obter metadata com suporte a IMDSv1 e IMDSv2"""
    base_url = "http://169.254.169.254/latest/meta-data/"
    
    # Tentar IMDSv1 primeiro
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=3)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    
    # Tentar IMDSv2
    try:
        # Obter token
        token_response = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=3
        )
        if token_response.status_code == 200:
            token = token_response.text
            response = requests.get(
                f"{base_url}{endpoint}",
                headers={"X-aws-ec2-metadata-token": token},
                timeout=3
            )
            if response.status_code == 200:
                return response.text.strip()
    except:
        pass
    
    return None

def get_instance_info():
    """Obter informações completas da instância EC2"""
    try:
        # Obter informações usando a função auxiliar
        instance_id = get_metadata("instance-id") or "ID não disponível"
        hostname = get_metadata("hostname") or get_metadata("public-hostname") or "hostname não disponível"
        private_ip = get_metadata("local-ipv4") or "IP não disponível"
        az = get_metadata("placement/availability-zone") or "AZ não disponível"
        
        # Se hostname ainda estiver vazio, usar instance-id
        if hostname == "hostname não disponível" and instance_id != "ID não disponível":
            hostname = f"ip-{private_ip.replace('.', '-')}" if private_ip != "IP não disponível" else instance_id
        
        return {
            "instance_id": instance_id,
            "hostname": hostname,
            "private_ip": private_ip,
            "availability_zone": az
        }
    except Exception as e:
        return {
            "instance_id": "Erro ao obter",
            "hostname": "Erro ao obter", 
            "private_ip": "Erro ao obter",
            "availability_zone": "Erro ao obter"
        }

def start_cpu_stress_background(duration, intensity=1):
    """Inicia stress de CPU em background usando subprocess"""
    try:
        # Comando Python para stress de CPU
        stress_cmd = f"""
import time
import multiprocessing
import os

def cpu_stress():
    end = time.time() + {duration}
    while time.time() < end:
        _ = 12345 ** 12345

# Criar {intensity} processos para stress
processes = []
for i in range({intensity}):
    p = multiprocessing.Process(target=cpu_stress)
    p.start()
    processes.append(p)

# Aguardar todos terminarem
for p in processes:
    p.join()
"""
        
        # Salvar script temporário
        with open('/tmp/stress_cpu.py', 'w') as f:
            f.write(stress_cmd)
        
        # Executar em background
        subprocess.Popen(['python3', '/tmp/stress_cpu.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        st.error(f"Erro ao iniciar stress: {e}")
        return False

def start_memory_stress_background(duration, size_mb=100):
    """Inicia stress de memória em background"""
    try:
        stress_cmd = f"""
import time
import os

def memory_stress():
    data = []
    end = time.time() + {duration}
    try:
        while time.time() < end:
            # Alocar {size_mb}MB
            data.append(bytearray(1024 * 1024 * {size_mb}))
            time.sleep(1)
    except MemoryError:
        pass
    except KeyboardInterrupt:
        pass

memory_stress()
"""
        
        with open('/tmp/stress_memory.py', 'w') as f:
            f.write(stress_cmd)
        
        subprocess.Popen(['python3', '/tmp/stress_memory.py'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        st.error(f"Erro ao iniciar stress de memória: {e}")
        return False

def check_stress_processes():
    """Verifica se há processos de stress rodando"""
    try:
        result = subprocess.run(['pgrep', '-f', 'stress'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except:
        return 0

def kill_stress_processes():
    """Para todos os processos de stress"""
    try:
        subprocess.run(['pkill', '-f', 'stress'], capture_output=True)
        # Limpar arquivos temporários
        for file in ['/tmp/stress_cpu.py', '/tmp/stress_memory.py']:
            if os.path.exists(file):
                os.remove(file)
        return True
    except:
        return False

# Configuração da página
st.set_page_config(
    page_title="ASG Stress Test Demo", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🚀 Auto Scaling Group - Stress Test Demo")
st.markdown("---")

# Informações da instância
info = get_instance_info()

# Layout em colunas para informações da instância
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Informações da Instância")
    st.info(f"**Instance ID:** `{info['instance_id']}`")
    st.info(f"**Hostname:** `{info['hostname']}`")

with col2:
    st.subheader("🌐 Rede & Localização")
    st.info(f"**IP Privado:** `{info['private_ip']}`")
    st.info(f"**Availability Zone:** `{info['availability_zone']}`")

st.markdown("---")

# Status dos recursos em tempo real
st.subheader("📊 Status dos Recursos")

# Métricas em tempo real
col1, col2, col3, col4 = st.columns(4)

cpu_percent = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory()
disk = psutil.disk_usage('/')
stress_procs = check_stress_processes()

col1.metric("🔥 CPU", f"{cpu_percent:.1f}%", 
           delta=f"{cpu_percent-50:.1f}%" if cpu_percent > 50 else None)
col2.metric("💾 RAM", f"{memory.percent:.1f}%",
           delta=f"{memory.percent-50:.1f}%" if memory.percent > 50 else None)
col3.metric("💿 Disco", f"{disk.percent:.1f}%")
col4.metric("⚡ Processos Stress", stress_procs)

st.markdown("---")

# Controles de Stress Test
st.subheader("💥 Controles de Stress Test")

# Sidebar para controles
with st.sidebar:
    st.header("🎛️ Configurações")
    
    test_type = st.selectbox("Tipo de Teste", ["CPU", "Memória"])
    
    if test_type == "CPU":
        duration = st.slider("Duração (minutos)", 1, 30, 5)
        intensity = st.slider("Intensidade (cores)", 1, 4, 1)
        st.info(f"Vai usar {intensity} core(s) por {duration} minutos")
    else:
        duration = st.slider("Duração (minutos)", 1, 15, 3)
        size_mb = st.slider("Tamanho do bloco (MB)", 50, 500, 100)
        st.info(f"Vai alocar {size_mb}MB por {duration} minutos")

# Botões de controle
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Iniciar Stress Test", type="primary"):
        duration_seconds = duration * 60
        
        if test_type == "CPU":
            success = start_cpu_stress_background(duration_seconds, intensity)
            if success:
                st.success(f"✅ Stress de CPU iniciado! ({intensity} cores por {duration} min)")
                st.balloons()
            else:
                st.error("❌ Falha ao iniciar stress de CPU")
        else:
            success = start_memory_stress_background(duration_seconds, size_mb)
            if success:
                st.success(f"✅ Stress de Memória iniciado! ({size_mb}MB por {duration} min)")
                st.balloons()
            else:
                st.error("❌ Falha ao iniciar stress de memória")

with col2:
    if st.button("🛑 Parar Todos os Testes", type="secondary"):
        if kill_stress_processes():
            st.success("✅ Todos os testes foram interrompidos")
        else:
            st.warning("⚠️ Nenhum teste ativo encontrado")

with col3:
    if st.button("🔄 Atualizar Status"):
        st.rerun()

st.markdown("---")


# Footer com timestamp
st.markdown("---")
st.caption(f"🕐 Última atualização: {datetime.now().strftime('%H:%M:%S')} | Recarregue para ver outras instâncias!")

# Auto-refresh a cada 30 segundos se houver stress ativo
if stress_procs > 0:
    time.sleep(30)
    st.rerun()