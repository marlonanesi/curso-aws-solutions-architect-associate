## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#

# 🔧 Lab 5: Auto Scaling Group + Application Load Balancer Completo

## 🎯 Objetivo

Criar uma arquitetura completa de **alta disponibilidade e escalabilidade automática** integrando Application Load Balancer (ALB) com Auto Scaling Group (ASG), demonstrando distribuição de tráfego inteligente, escalabilidade dinâmica baseada em métricas, e resiliência a falhas. **Nível: Avançado**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> ALB: 750 horas/mês incluídas. EC2: 750 horas/mês t2/t3.micro incluídas. CloudWatch: 10 métricas personalizadas gratuitas.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * ASG pode escalar até 4 instâncias durante alta carga
> * ALB cobra por hora + por requisições processadas
> * Sempre **delete ASG, ALB e Target Groups** ao final do exercício

## ⭐ Passos a Executar

### 1. Compreender Arquitetura ALB + ASG

**Componentes da Solução:**
- **Application Load Balancer**: Ponto de entrada, distribui tráfego
- **Target Group**: Conecta ALB ao ASG, gerencia health checks
- **Auto Scaling Group**: Gerencia instâncias dinamicamente
- **Launch Template**: Define configuração das instâncias
- **CloudWatch**: Monitora métricas e triggers scaling

**Fluxo de Funcionamento:**
1. **Usuário** → ALB (porta 80)
2. **ALB** → Target Group → Instâncias EC2 (porta 8501)
3. **CloudWatch** monitora CPU das instâncias
4. **ASG** escala baseado em Target Tracking (60% CPU)
5. **ALB** automatically registra/remove novas instâncias

**Benefícios:**
- ✅ Alta disponibilidade multi-AZ
- ✅ Escalabilidade automática baseada em demanda
- ✅ Health checks em múltiplas camadas
- ✅ Distribuição de carga inteligente

### 2. Preparar Security Groups

1. **Crie Security Group para ALB**:
   - **Name**: `sg-alb-asg-demo`
   - **Description**: Security group for ALB in ASG demo
   - **VPC**: Default VPC
   
   **Inbound rules**:
   - Type: HTTP, Port: 80, Source: 0.0.0.0/0
   
   **Outbound rules**:
   - Type: Custom TCP, Port: 8501, Destination: `sg-ec2-asg-demo` (criar depois)

2. **Crie Security Group para EC2**:
   - **Name**: `sg-ec2-asg-demo`
   - **Description**: Security group for EC2 instances in ASG demo
   - **VPC**: Default VPC
   
   **Inbound rules**:
   - Type: Custom TCP, Port: 8501, Source: `sg-alb-asg-demo`
   - Type: SSH, Port: 22, Source: Your IP

3. **Atualize SG do ALB**:
   - Edite outbound rule do `sg-alb-asg-demo`
   - Destination: `sg-ec2-asg-demo`

### 3. Criar Target Group

1. **Acesse Target Groups**:
   - **EC2 > Target Groups > Create target group**

2. **Configure target group básico**:
   - **Choose a target type**: Instances
   - **Target group name**: `tg-asg-stress-demo`
   - **Protocol**: HTTP
   - **Port**: 8501
   - **VPC**: Default VPC (ou sua VPC)
   - **Protocol version**: HTTP1

3. **Configure health check**:
   - **Health check protocol**: HTTP
   - **Health check path**: `/`
   - **Health check port**: Traffic port
   - **Healthy threshold**: 2
   - **Unhealthy threshold**: 3
   - **Timeout**: 10 seconds
   - **Interval**: 30 seconds
   - **Success codes**: 200

4. **Skip target registration**:
   - Não registre targets manualmente
   - ASG fará isso automaticamente
   - **Create target group**

### 4. Criar Application Load Balancer

1. **Acesse Load Balancers**:
   - **EC2 > Load Balancers > Create load balancer**

2. **Selecione tipo**:
   - **Application Load Balancer > Create**

3. **Configure básico**:
   - **Load balancer name**: `alb-asg-stress-demo`
   - **Scheme**: Internet-facing
   - **IP address type**: IPv4

4. **Configure network mapping**:
   - **VPC**: Default VPC
   - **Mappings**: Selecione **ao menos 2 AZs**
   - **Availability Zones**: us-east-1a, us-east-1b (ajuste conforme região)
   - **Subnets**: Selecione subnets públicas

5. **Configure security groups**:
   - Remove default security group
   - Selecione `sg-alb-asg-demo`

6. **Configure listeners and routing**:
   - **Protocol**: HTTP
   - **Port**: 80
   - **Default actions**: Forward to target group
   - **Target group**: `tg-asg-stress-demo`

7. **Create load balancer**

8. **Aguarde ALB ficar ativo** (~3-5 minutos):
   - Status deve mudar de "provisioning" para "active"

### 5. Preparar AMI Customizada (Opcional)

**Se você não tem uma AMI com aplicação de stress:**

1. **Lance instância temporária**:
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t3.micro
   - **Security group**: Permita SSH (22)

2. **Configure aplicação de stress**:
   ```bash
   # SSH para instância
   ssh -i sua-chave.pem ec2-user@ip-publico
   
   # Update e instale dependências
   sudo yum update -y
   sudo yum install -y python3 python3-pip stress htop
   
   # Instale Streamlit
   pip3 install streamlit psutil
   
   # Crie aplicação de stress test
   cat > /home/ec2-user/stress_app.py << 'EOF'
   import streamlit as st
   import subprocess
   import psutil
   import time
   import threading
   import requests
   
   st.set_page_config(page_title="ASG Stress Demo", layout="wide")
   
   st.title("🚀 Auto Scaling Group Demo")
   
   # Instance information
   try:
       instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=3).text
       az = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone', timeout=3).text
       private_ip = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout=3).text
   except:
       instance_id = "Unable to fetch"
       az = "Unable to fetch"
       private_ip = "Unable to fetch"
   
   col1, col2 = st.columns(2)
   
   with col1:
       st.subheader("📊 Instance Information")
       st.write(f"**Instance ID:** {instance_id}")
       st.write(f"**Availability Zone:** {az}")
       st.write(f"**Private IP:** {private_ip}")
       st.write(f"**CPU Count:** {psutil.cpu_count()}")
   
   with col2:
       st.subheader("📈 Current Metrics")
       cpu_percent = psutil.cpu_percent(interval=1)
       memory = psutil.virtual_memory()
       
       st.metric("CPU Usage", f"{cpu_percent:.1f}%")
       st.metric("Memory Usage", f"{memory.percent:.1f}%")
       st.metric("Load Average", f"{psutil.getloadavg()[0]:.2f}")
   
   st.subheader("🔥 Stress Test Controls")
   
   col3, col4, col5 = st.columns(3)
   
   with col3:
       cpu_cores = st.slider("CPU Cores", 1, psutil.cpu_count(), 1)
       duration = st.slider("Duration (minutes)", 1, 15, 5)
   
   with col4:
       if st.button("🚀 Start CPU Stress"):
           cmd = f"stress --cpu {cpu_cores} --timeout {duration*60}"
           subprocess.Popen(cmd, shell=True)
           st.success(f"Started CPU stress: {cpu_cores} cores for {duration} minutes")
   
   with col5:
       if st.button("🛑 Stop All Stress"):
           subprocess.run("pkill stress", shell=True)
           st.success("Stopped all stress processes")
   
   # Real-time metrics
   if st.checkbox("📊 Real-time Monitoring"):
       placeholder = st.empty()
       
       for i in range(10):
           cpu = psutil.cpu_percent(interval=1)
           memory = psutil.virtual_memory().percent
           load = psutil.getloadavg()[0]
           
           with placeholder.container():
               col_a, col_b, col_c = st.columns(3)
               col_a.metric("Live CPU", f"{cpu:.1f}%", f"{cpu-50:.1f}%")
               col_b.metric("Live Memory", f"{memory:.1f}%")
               col_c.metric("Live Load", f"{load:.2f}")
           
           time.sleep(2)
   EOF
   
   # Crie systemd service
   sudo tee /etc/systemd/system/stress-app.service << 'EOF'
   [Unit]
   Description=Streamlit Stress Test App
   After=network.target
   
   [Service]
   Type=simple
   User=ec2-user
   WorkingDirectory=/home/ec2-user
   ExecStart=/usr/local/bin/streamlit run stress_app.py --server.port 8501 --server.address 0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   # Enable e start service
   sudo systemctl daemon-reload
   sudo systemctl enable stress-app
   sudo systemctl start stress-app
   
   # Teste aplicação
   curl http://localhost:8501
   ```

3. **Crie AMI**:
   - **EC2 > Instances > Selecione instância**
   - **Actions > Image and templates > Create image**
   - **Image name**: `ami-stress-app-demo`
   - **Create image**

4. **Termine instância temporária** após AMI ficar disponível

### 6. Criar Launch Template

1. **Acesse Launch Templates**:
   - **EC2 > Launch Templates > Create launch template**

2. **Configure template**:
   - **Launch template name**: `lt-asg-stress-demo`
   - **Template version description**: ASG demo with stress test app
   - **Auto Scaling guidance**: ✅ Enabled

3. **Configure Application and OS Images**:
   - **AMI**: `ami-stress-app-demo` (sua AMI customizada)
   - **Architecture**: 64-bit (x86)

4. **Configure Instance type**:
   - **Instance type**: t3.micro

5. **Configure Key pair**:
   - **Key pair**: Selecione seu key pair existente

6. **Configure Network settings**:
   - **Subnet**: Don't include in launch template
   - **Security groups**: `sg-ec2-asg-demo`
   - **Auto-assign public IP**: Enable

7. **Configure User data** (para garantir que serviço está rodando):
   ```bash
   #!/bin/bash
   
   # Garantir que serviço está rodando
   systemctl start stress-app
   systemctl enable stress-app
   
   # Install CloudWatch agent (opcional)
   yum install -y amazon-cloudwatch-agent
   ```

8. **Create launch template**

### 7. Criar Auto Scaling Group

1. **Acesse Auto Scaling Groups**:
   - **EC2 > Auto Scaling Groups > Create Auto Scaling group**

2. **Step 1: Choose launch template**:
   - **Auto Scaling group name**: `asg-stress-demo`
   - **Launch template**: `lt-asg-stress-demo`
   - **Version**: Default (Latest)
   - **Next**

3. **Step 2: Choose instance launch options**:
   - **VPC**: Default VPC
   - **Availability Zones and subnets**: 
     - Selecione **mesmas AZs e subnets do ALB**
     - Ao menos 2 AZs diferentes
   - **Instance type requirements**: Use launch template
   - **Next**

4. **Step 3: Configure advanced options**:
   - **Load balancing**: Attach to an existing load balancer
   - **Load balancer target groups**: `tg-asg-stress-demo`
   - **Health checks**: ELB + EC2
   - **Health check grace period**: 300 seconds
   - **Additional settings**: Enable group metrics collection in CloudWatch
   - **Next**

5. **Step 4: Configure group size and scaling**:
   - **Group size**:
     - **Desired capacity**: 1
     - **Minimum capacity**: 1
     - **Maximum capacity**: 4
   
   - **Scaling policies**:
     - **Target tracking scaling policy**: ✅ Enabled
     - **Policy name**: `CPU-Target-Tracking-60`
     - **Metric type**: Average CPU utilization
     - **Target value**: 60
     - **Instance warmup**: 300 seconds
     - **Disable scale-in**: ❌ (permitir scale-in)
   
   - **Instance maintenance policy**: No policy
   - **Next**

6. **Step 5: Add notifications** (opcional):
   - Skip para este lab
   - **Next**

7. **Step 6: Add tags**:
   - **Key**: `Name` | **Value**: `asg-stress-instance`
   - **Key**: `Environment` | **Value**: `Lab`
   - **Key**: `Purpose` | **Value**: `ASG-ALB-Demo`
   - **Next**

8. **Step 7: Review**:
   - Revise todas configurações
   - **Create Auto Scaling group**

### 8. Verificar Integração Inicial

1. **Aguarde ASG lançar primeira instância** (~5 minutos):
   - **Auto Scaling Groups > asg-stress-demo**
   - **Activity tab**: Observe "Launching a new EC2 instance"
   - **Instance management tab**: Veja instância sendo criada

2. **Verifique Target Group**:
   - **EC2 > Target Groups > tg-asg-stress-demo**
   - **Targets tab**: Instância deve aparecer como "initial"
   - Aguarde status mudar para "healthy" (~2-3 minutos)

3. **Teste acesso via ALB**:
   - **Load Balancers > alb-asg-stress-demo**
   - Copie **DNS name**
   - Acesse no navegador: `http://dns-name-do-alb`
   - **Resultado esperado**: Interface de stress test carregando

### 9. Testar Escalabilidade Automática

1. **Acesse aplicação via ALB DNS**:
   - Observe informações da instância atual
   - Note Instance ID, AZ, e Private IP

2. **Configure stress test**:
   - **CPU Cores**: 2 (para t3.micro)
   - **Duration**: 10 minutes
   - **Click**: "🚀 Start CPU Stress"

3. **Monitore CPU em tempo real**:
   - Habilite "📊 Real-time Monitoring"
   - Observe CPU subindo para 80-90%

4. **Monitore scaling no console**:
   - **Auto Scaling Groups > asg-stress-demo > Activity**
   - Atualize a cada 1-2 minutos
   - **Resultado esperado**: Após ~3-5 minutos, veja "Launching a new EC2 instance"

5. **Observe múltiplas instâncias**:
   - Continue recarregando página do ALB
   - **Resultado esperado**: Diferentes Instance IDs aparecendo
   - ALB distribui requests entre instâncias disponíveis

6. **Monitore Target Group**:
   - **Target Groups > tg-asg-stress-demo > Targets**
   - Observe novas instâncias sendo registradas automaticamente
   - Status: initial → healthy

### 10. Observar Scale-In

1. **Pare stress test**:
   - Click "🛑 Stop All Stress" na aplicação
   - Ou aguarde 10 minutos terminar automaticamente

2. **Monitore CPU reduzindo**:
   - Use real-time monitoring
   - CPU deve cair para 1-5%

3. **Aguarde cooldown period**:
   - Target tracking tem cooldown padrão
   - Scale-in leva mais tempo que scale-out (~10-15 minutos)

4. **Observe scale-in**:
   - **Auto Scaling Groups > Activity**
   - **Resultado esperado**: "Terminating EC2 instance"
   - Capacidade volta para mínima (1 instância)

### 11. Testar Cenários Avançados

1. **Teste falha de instância**:
   ```bash
   # SSH para uma instância
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   
   # Pare serviço para simular falha
   sudo systemctl stop stress-app
   
   # Ou termine instância via console
   ```
   
   - Observe ALB detectar instância unhealthy
   - ASG substitui instância automaticamente

2. **Teste múltiplas sessões**:
   - Abra múltiplas abas do navegador
   - Execute stress em instâncias diferentes
   - Observe distribuição de carga

3. **Teste scale-out agressivo**:
   - CPU cores: 4 (máximo)
   - Duration: 15 minutes
   - Observe ASG escalando para capacidade máxima

### 12. Monitorar Métricas Detalhadas

1. **CloudWatch métricas do ALB**:
   - **CloudWatch > Metrics > AWS/ApplicationELB**
   - Métricas importantes:
     - RequestCount: Total requests
     - TargetResponseTime: Latência
     - HealthyHostCount: Targets saudáveis
     - HTTPCode_Target_2XX_Count: Responses de sucesso

2. **CloudWatch métricas do ASG**:
   - **AWS/AutoScaling**
   - Métricas importantes:
     - GroupDesiredCapacity: Capacidade desejada
     - GroupInServiceInstances: Instâncias ativas
     - GroupTotalInstances: Total de instâncias

3. **CloudWatch métricas das instâncias**:
   - **AWS/EC2 > Per-Instance Metrics**
   - **CPUUtilization**: Para cada instância
   - Compare com threshold de 60%

4. **Crie dashboard personalizado**:
   - **CloudWatch > Dashboards > Create dashboard**
   - **Dashboard name**: `ASG-ALB-Demo`
   - Adicione widgets para métricas principais

### 13. Limpeza Responsável de Recursos

1. **Delete Auto Scaling Group**:
   - **Auto Scaling Groups > asg-stress-demo**
   - **Actions > Delete**
   - Digite nome do ASG para confirmar
   - Aguarde terminação de todas as instâncias

2. **Delete Load Balancer**:
   - **Load Balancers > alb-asg-stress-demo**
   - **Actions > Delete**
   - Digite "confirm" para confirmar

3. **Delete Target Group**:
   - **Target Groups > tg-asg-stress-demo**
   - **Actions > Delete**

4. **Delete Launch Template**:
   - **Launch Templates > lt-asg-stress-demo**
   - **Actions > Delete template**

5. **Delete Security Groups**:
   - **Security Groups**
   - Delete `sg-alb-asg-demo` e `sg-ec2-asg-demo`
   - (Delete ALB SG primeiro, depois EC2 SG)

6. **Delete AMI** (opcional):
   - **AMIs > ami-stress-app-demo**
   - **Actions > Deregister AMI**
   - **Snapshots**: Delete snapshots associados

7. **Verifique limpeza completa**:
   ```bash
   # Verifique recursos órfãos
   aws elbv2 describe-load-balancers --query 'LoadBalancers[?State.Code==`active`]'
   aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[?contains(AutoScalingGroupName, `asg-stress`)]'
   aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[].Instances[?contains(Tags[?Key==`Name`].Value[], `asg-stress`)]'
   ```

## ✅ Conclusão

Você implementou uma arquitetura completa de alta disponibilidade e escalabilidade:

**✅ Checklist de Conquistas:**
- [ ] Arquitetura ALB + ASG + Target Group implementada
- [ ] Security Groups configurados com princípio de menor privilégio
- [ ] Launch Template criado com User Data personalizado
- [ ] Auto Scaling Group configurado para multi-AZ
- [ ] Target Tracking Policy implementada (CPU 60%)
- [ ] Integração ALB → Target Group → ASG verificada
- [ ] Aplicação de stress test desenvolvida e deployada
- [ ] Scale-out automático demonstrado e testado
- [ ] Scale-in automático observado após cooldown
- [ ] Distribuição de carga entre múltiplas instâncias testada
- [ ] Scenarios de falha e recuperação executados
- [ ] Métricas CloudWatch monitoradas e analisadas
- [ ] Dashboard personalizado criado para monitoramento
- [ ] Limpeza responsável de recursos executada

**🎓 Conceitos Reforçados:**
* **ALB + ASG Integration**: Registro automático de targets via Target Groups
* **Target Tracking Scaling**: Política de scaling mais inteligente e eficiente
* **Multi-AZ High Availability**: Distribuição de recursos entre zonas
* **Health Checks Multi-Layer**: ELB + EC2 health checks combinados
* **Load Distribution**: Algoritmos de balanceamento e sticky sessions
* **CloudWatch Integration**: Métricas driving automated scaling decisions
* **Infrastructure as Code**: Launch Templates para configuração reproduzível
* **Fault Tolerance**: Automatic instance replacement e recovery
