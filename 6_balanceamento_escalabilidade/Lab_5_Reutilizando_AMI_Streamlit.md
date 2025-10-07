## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 6: Reutilizando AMI com Streamlit - Deployment Ágil

## 🎯 Objetivo

Demonstrar como reutilizar uma AMI pré-configurada com Streamlit para deploy ágil de aplicações, substituindo arquivos de aplicação e dependências, executando scripts de inicialização automatizados para um workflow eficiente de desenvolvimento e deployment. **Nível: Básico**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> EC2: 750 horas/mês t2.micro/t3.micro incluídas no Free Tier (12 meses). AMI storage: EBS snapshots podem gerar custos mínimos.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * AMI storage cobra por GB/mês dos snapshots
> * Instâncias deixadas rodando geram custo contínuo
> * Sempre **termine instâncias** ao final do exercício

## ⭐ Passos a Executar

### 1. Compreender Vantagens de AMIs Customizadas

**O que são AMIs Customizadas?**

Uma AMI (Amazon Machine Image) customizada é um snapshot de uma instância EC2 configurada com:
- Sistema operacional pré-configurado
- Aplicações e dependências instaladas
- Scripts de inicialização configurados
- Configurações de sistema otimizadas

**Vantagens para Desenvolvimento:**
- ✅ **Deploy rápido**: Instâncias inicializam com ambiente pronto
- ✅ **Consistência**: Mesmo ambiente em dev/test/prod
- ✅ **Redução de tempo**: Elimina etapas de configuração manual
- ✅ **Escalabilidade**: Base para Auto Scaling Groups
- ✅ **Versionamento**: Diferentes versões de ambiente

**Casos de Uso Comuns:**
- Aplicações web com stack específico
- Ambientes de desenvolvimento padronizados
- Base para microserviços
- Templates para equipes

### 2. Verificar Pré-requisitos

1. **Verifique AMI base disponível**:
   ```bash
   # Liste AMIs customizadas disponíveis
   aws ec2 describe-images \
     --owners self \
     --filters "Name=name,Values=*streamlit*" \
     --query 'Images[].[ImageId,Name,CreationDate]' \
     --output table
   ```

2. **Se não tiver AMI base, crie uma rapidamente**:
   - **Lance instância**: Amazon Linux 2023, t3.micro
   - **Configure aplicação básica**:
   ```bash
   # SSH para instância
   sudo yum update -y
   sudo yum install -y python3 python3-pip git
   
   # Instale Streamlit
   pip3 install streamlit psutil requests
   
   # Crie app básico
   cat > /home/ec2-user/app.py << 'EOF'
   import streamlit as st
   import psutil
   import requests
   
   st.title("🚀 Streamlit Demo App")
   
   # Instance info
   try:
       instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=3).text
       st.write(f"Instance ID: {instance_id}")
   except:
       st.write("Instance ID: Unable to fetch")
   
   st.write(f"CPU Count: {psutil.cpu_count()}")
   st.write(f"CPU Usage: {psutil.cpu_percent(1):.1f}%")
   EOF
   
   # Crie requirements.txt
   cat > /home/ec2-user/requirements.txt << 'EOF'
   streamlit==1.28.0
   psutil==5.9.5
   requests==2.31.0
   EOF
   
   # Crie script de start
   cat > /home/ec2-user/start.sh << 'EOF'
   #!/bin/bash
   
   echo "🚀 Starting Streamlit deployment process..."
   
   # Navigate to app directory
   cd /home/ec2-user
   
   # Install/upgrade dependencies
   echo "📦 Installing requirements..."
   pip3 install -r requirements.txt --upgrade
   
   # Kill any existing Streamlit processes
   echo "🛑 Stopping existing Streamlit processes..."
   pkill -f "streamlit run"
   
   # Wait a moment
   sleep 2
   
   # Start Streamlit app
   echo "🎯 Starting Streamlit app..."
   nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
   
   echo "✅ Streamlit started! Access at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
   echo "📝 Logs available at: tail -f ~/streamlit.log"
   EOF
   
   chmod +x start.sh
   ```

   - **Crie AMI**: Actions > Image and templates > Create image
   - **AMI name**: `ami-streamlit-base`
   - **Termine instância temporária**

### 3. Preparar Nova Aplicação para Deploy

1. **Crie nova versão do app.py** (no seu computador local):
   ```python
   # Salve como app_v2.py
   import streamlit as st
   import psutil
   import requests
   import time
   import subprocess
   import threading
   
   st.set_page_config(page_title="Streamlit V2 Demo", layout="wide")
   
   st.title("🎯 Advanced Streamlit Demo - Version 2.0")
   
   # Instance information section
   st.header("📊 Instance Information")
   
   col1, col2, col3 = st.columns(3)
   
   try:
       # Fetch instance metadata
       instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=3).text
       az = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone', timeout=3).text
       private_ip = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout=3).text
       public_ip = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', timeout=3).text
   except:
       instance_id = az = private_ip = public_ip = "Unable to fetch"
   
   with col1:
       st.metric("Instance ID", instance_id)
       st.metric("Availability Zone", az)
   
   with col2:
       st.metric("Private IP", private_ip)
       st.metric("Public IP", public_ip)
   
   with col3:
       st.metric("CPU Cores", psutil.cpu_count())
       st.metric("Memory Total", f"{psutil.virtual_memory().total // (1024**3)} GB")
   
   # Real-time metrics section
   st.header("📈 Real-time System Metrics")
   
   if st.checkbox("🔄 Enable Live Monitoring"):
       placeholder = st.empty()
       
       for i in range(30):  # 30 seconds of monitoring
           cpu_percent = psutil.cpu_percent(interval=1)
           memory = psutil.virtual_memory()
           disk = psutil.disk_usage('/')
           
           with placeholder.container():
               col_a, col_b, col_c = st.columns(3)
               
               with col_a:
                   st.metric(
                       "CPU Usage", 
                       f"{cpu_percent:.1f}%",
                       delta=f"{cpu_percent-50:.1f}%" if cpu_percent > 50 else None
                   )
               
               with col_b:
                   st.metric(
                       "Memory Usage", 
                       f"{memory.percent:.1f}%",
                       delta=f"{memory.percent-50:.1f}%" if memory.percent > 50 else None
                   )
               
               with col_c:
                   st.metric(
                       "Disk Usage", 
                       f"{disk.percent:.1f}%"
                   )
           
           time.sleep(1)
   
   # Tools section
   st.header("🛠️ System Tools")
   
   col_tool1, col_tool2 = st.columns(2)
   
   with col_tool1:
       st.subheader("💻 System Information")
       if st.button("🔍 Get Detailed System Info"):
           sys_info = {
               "Hostname": subprocess.getoutput("hostname"),
               "Uptime": subprocess.getoutput("uptime"),
               "Disk Space": subprocess.getoutput("df -h /"),
               "Memory Info": subprocess.getoutput("free -h"),
               "Network Interfaces": subprocess.getoutput("ip addr show")
           }
           
           for key, value in sys_info.items():
               st.text_area(key, value, height=100)
   
   with col_tool2:
       st.subheader("🔥 Load Testing")
       
       if "stress_running" not in st.session_state:
           st.session_state.stress_running = False
       
       col_stress1, col_stress2 = st.columns(2)
       
       with col_stress1:
           if st.button("🚀 Start CPU Stress (30s)") and not st.session_state.stress_running:
               st.session_state.stress_running = True
               subprocess.Popen("stress --cpu 1 --timeout 30", shell=True)
               st.success("CPU stress started for 30 seconds!")
               threading.Timer(31, lambda: setattr(st.session_state, 'stress_running', False)).start()
       
       with col_stress2:
           if st.button("🛑 Stop All Stress"):
               subprocess.run("pkill stress", shell=True)
               st.session_state.stress_running = False
               st.success("All stress processes stopped!")
   
   # Footer
   st.markdown("---")
   st.markdown("**Version 2.0** - Enhanced with live monitoring and system tools")
   st.markdown(f"*Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}*")
   ```

2. **Crie requirements.txt atualizado**:
   ```bash
   # Salve como requirements_v2.txt
   streamlit==1.28.0
   psutil==5.9.5
   requests==2.31.0
   stress-ng==0.15.0
   ```

### 4. Lançar Instância da AMI Base

1. **Lance instância EC2**:
   - **AMI**: `ami-streamlit-base` (sua AMI customizada)
   - **Instance type**: t3.micro
   - **Key pair**: Selecione seu key pair
   - **Network settings**: 
     - Subnet: Pública
     - Auto-assign public IP: Enable
     - Security group: Crie ou use existente
   
   **Security Group Rules**:
   - SSH (22): Seu IP
   - Custom TCP (8501): 0.0.0.0/0

2. **Configure tags**:
   - **Name**: `streamlit-demo-v2`
   - **Environment**: `Lab`
   - **Purpose**: `AMI-Reuse-Demo`

3. **Launch instance**

### 5. Conectar e Verificar Estado Inicial

1. **Conecte via SSH**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-da-instancia
   ```

2. **Verifique aplicação base**:
   ```bash
   # Verifique se há processos Streamlit rodando
   ps aux | grep streamlit
   
   # Liste arquivos da aplicação
   ls -la ~/
   
   # Verifique conteúdo atual
   cat ~/app.py
   cat ~/requirements.txt
   ```

3. **Teste aplicação original**:
   ```bash
   # Se não estiver rodando, start manualmente
   ./start.sh
   
   # Aguarde alguns segundos e teste
   curl http://localhost:8501
   ```

4. **Acesse no navegador**:
   - `http://ip-publico-da-instancia:8501`
   - Verifique que é a versão básica

### 6. Deploy da Nova Versão

1. **Pare aplicação atual**:
   ```bash
   # SSH para instância
   pkill -f "streamlit run"
   
   # Confirme que parou
   ps aux | grep streamlit
   ```

2. **Substitua arquivos via SCP** (do seu computador local):
   ```bash
   # Upload nova versão do app
   scp -i sua-chave.pem app_v2.py ec2-user@ip-publico-da-instancia:~/app.py
   
   # Upload requirements atualizados
   scp -i sua-chave.pem requirements_v2.txt ec2-user@ip-publico-da-instancia:~/requirements.txt
   ```

3. **Ou edite diretamente na instância** (alternativa):
   ```bash
   # SSH para instância
   nano ~/app.py
   # Cole o conteúdo do app_v2.py e salve
   
   nano ~/requirements.txt
   # Atualize requirements e salve
   ```

### 7. Executar Deploy Automatizado

1. **Execute script de deployment**:
   ```bash
   # SSH para instância
   ./start.sh
   ```

2. **Monitore logs de deployment**:
   ```bash
   # Observe instalação de dependências
   tail -f ~/streamlit.log
   
   # Verifique se processo startou
   ps aux | grep streamlit
   ```

3. **Verificar nova aplicação**:
   ```bash
   # Teste local
   curl http://localhost:8501
   
   # Check se porta está ouvindo
   netstat -tlnp | grep 8501
   ```

### 8. Testar Nova Versão

1. **Acesse aplicação atualizada**:
   - `http://ip-publico-da-instancia:8501`
   - **Resultado esperado**: Interface "Version 2.0" com novos recursos

2. **Teste recursos novos**:
   - **Live Monitoring**: Habilite e observe métricas em tempo real
   - **System Information**: Click para ver detalhes do sistema
   - **Load Testing**: Teste stress CPU por 30 segundos
   - **Metrics**: Observe CPU usage durante stress

3. **Verifique informações da instância**:
   - Instance ID deve estar correto
   - AZ, IPs devem estar atualizados
   - Métricas devem ser funcionais

### 9. Automatizar Process com Script Melhorado

1. **Crie script de deploy mais robusto**:
   ```bash
   # SSH para instância
   cat > ~/deploy.sh << 'EOF'
   #!/bin/bash
   
   APP_DIR="/home/ec2-user"
   LOG_FILE="$APP_DIR/deploy.log"
   
   log() {
       echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
   }
   
   log "🚀 Starting deployment process..."
   
   # Navigate to app directory
   cd $APP_DIR
   
   # Backup current version
   if [ -f "app.py" ]; then
       log "💾 Backing up current version..."
       cp app.py app.py.backup.$(date +%s)
       cp requirements.txt requirements.txt.backup.$(date +%s)
   fi
   
   # Install/upgrade dependencies
   log "📦 Installing/upgrading dependencies..."
   pip3 install -r requirements.txt --upgrade >> $LOG_FILE 2>&1
   
   if [ $? -eq 0 ]; then
       log "✅ Dependencies installed successfully"
   else
       log "❌ Failed to install dependencies"
       exit 1
   fi
   
   # Kill existing processes
   log "🛑 Stopping existing Streamlit processes..."
   pkill -f "streamlit run"
   sleep 3
   
   # Verify app.py exists and is valid
   if [ ! -f "app.py" ]; then
       log "❌ app.py not found!"
       exit 1
   fi
   
   # Start new version
   log "🎯 Starting new Streamlit application..."
   nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
   STREAMLIT_PID=$!
   
   # Wait and verify startup
   sleep 5
   
   if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
       log "✅ Streamlit started successfully (PID: $STREAMLIT_PID)"
       log "🌐 Application available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
   else
       log "❌ Streamlit failed to start"
       log "📝 Check logs: tail -f $APP_DIR/streamlit.log"
       exit 1
   fi
   
   log "🎉 Deployment completed successfully!"
   EOF
   
   chmod +x deploy.sh
   ```

2. **Teste script de deploy**:
   ```bash
   ./deploy.sh
   
   # Monitore logs
   tail -f deploy.log
   ```

### 10. Simular Diferentes Cenários

1. **Teste rollback rápido**:
   ```bash
   # Restaure versão anterior
   cp app.py.backup.* app.py
   ./deploy.sh
   ```

2. **Teste com diferentes versões**:
   ```bash
   # Crie versão mínima para teste
   cat > app_minimal.py << 'EOF'
   import streamlit as st
   st.title("Minimal App - Emergency Version")
   st.write("System is operational")
   EOF
   
   cp app_minimal.py app.py
   ./deploy.sh
   ```

3. **Teste falha de deploy**:
   ```bash
   # Requirements inválido para testar tratamento de erro
   echo "invalid-package==999.999.999" >> requirements.txt
   ./deploy.sh
   
   # Observe tratamento de erro
   ```

### 11. Documentar Processo para Equipe

1. **Crie documentação de deploy**:
   ```bash
   cat > ~/DEPLOY_README.md << 'EOF'
   # Streamlit Deployment Guide
   
   ## Quick Deploy Process
   
   1. Upload new files:
      ```bash
      scp -i key.pem app.py ec2-user@instance-ip:~/app.py
      scp -i key.pem requirements.txt ec2-user@instance-ip:~/requirements.txt
      ```
   
   2. Deploy:
      ```bash
      ssh -i key.pem ec2-user@instance-ip
      ./deploy.sh
      ```
   
   ## Monitoring
   - Application: http://instance-ip:8501
   - Logs: `tail -f ~/streamlit.log`
   - Deploy logs: `tail -f ~/deploy.log`
   
   ## Rollback
   ```bash
   cp app.py.backup.TIMESTAMP app.py
   ./deploy.sh
   ```
   
   ## Troubleshooting
   - Check process: `ps aux | grep streamlit`
   - Check port: `netstat -tlnp | grep 8501`
   - Restart: `./deploy.sh`
   EOF
   ```

### 12. Limpeza Responsável de Recursos

1. **Pare aplicação**:
   ```bash
   # SSH para instância
   pkill -f "streamlit run"
   ```

2. **Termine instância EC2**:
   - **EC2 > Instances**
   - Selecione `streamlit-demo-v2`
   - **Instance State > Terminate Instance**

3. **Cleanup opcional da AMI** (se não for reutilizar):
   - **EC2 > AMIs**
   - Selecione `ami-streamlit-base`
   - **Actions > Deregister AMI**
   - **Snapshots**: Delete snapshots associados

4. **Cleanup arquivos locais**:
   ```bash
   # No seu computador
   rm app_v2.py requirements_v2.txt app_minimal.py
   ```

## ✅ Conclusão

Você dominou o workflow de deploy ágil usando AMIs customizadas:

**✅ Checklist de Conquistas:**
- [ ] Conceitos de AMI customizada compreendidos
- [ ] AMI base com Streamlit configurada
- [ ] Nova versão de aplicação desenvolvida
- [ ] Processo de deploy via SCP executado
- [ ] Script de deployment automatizado criado
- [ ] Deploy da versão 2.0 realizado com sucesso
- [ ] Recursos avançados da nova aplicação testados
- [ ] Monitoramento em tempo real demonstrado
- [ ] Scripts de backup e rollback implementados
- [ ] Diferentes cenários de deploy testados
- [ ] Tratamento de erros de deployment verificado
- [ ] Documentação de processo criada
- [ ] Limpeza responsável de recursos executada

**🎓 Conceitos Reforçados:**
* **AMI Reuse**: Reutilização de templates pré-configurados para deploy ágil
* **Deployment Automation**: Scripts automatizados para processo consistente
* **Version Management**: Backup e rollback de versões de aplicação
* **Infrastructure as Code**: AMIs como base para ambientes reproduzíveis
* **Continuous Deployment**: Workflow otimizado para atualizações frequentes
* **Error Handling**: Tratamento robusto de falhas durante deployment
* **Monitoring Integration**: Logs e métricas para visibilidade operacional
* **Team Collaboration**: Documentação e processos padronizados para equipes
