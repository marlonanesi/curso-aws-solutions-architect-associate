## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 4: Auto Scaling Group com Target Tracking

## 🎯 Objetivo

Criar um **Auto Scaling Group (ASG)** que escala automaticamente instâncias EC2 usando **política Target Tracking** para manter a utilização de CPU em 60%, demonstrando como a AWS ajusta dinamicamente a capacidade para otimizar performance e custos. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> EC2: 750 horas/mês t2.micro/t3.micro incluídas no Free Tier (12 meses). CloudWatch: 10 métricas personalizadas gratuitas.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * ASG pode lançar múltiplas instâncias durante scaling (até o máximo configurado)
> * CloudWatch cobra por métricas detalhadas adicionais
> * Sempre **delete o ASG e Launch Template** ao final do exercício

## ⭐ Passos a Executar

### 1. Compreender Conceitos de Auto Scaling

**O que é Auto Scaling Group (ASG)?**

ASG é um serviço que:
- Mantém número desejado de instâncias rodando
- Substitui instâncias com falha automaticamente
- Escala para cima (scale-out) quando demanda aumenta
- Escala para baixo (scale-in) quando demanda diminui

**Target Tracking vs Other Policies:**
- **Target Tracking**: Mantém métrica específica próxima ao valor alvo (mais simples)
- **Step Scaling**: Escala em etapas baseadas em thresholds
- **Simple Scaling**: Ação única baseada em alarme (legado)

**Métricas comuns para Target Tracking:**
- ✅ CPU Utilization (mais usado)
- ✅ ALB Request Count per Target
- ✅ Average Network In/Out
- ✅ Métricas customizadas

### 2. Preparar Pré-requisitos

1. **Verifique VPC e Subnets**:
   ```bash
   # Liste VPCs disponíveis
   aws ec2 describe-vpcs \
     --query 'Vpcs[].[VpcId,CidrBlock,IsDefault]' \
     --output table
   
   # Liste subnets públicas em AZs diferentes
   aws ec2 describe-subnets \
     --filters "Name=map-public-ip-on-launch,Values=true" \
     --query 'Subnets[].[SubnetId,AvailabilityZone,CidrBlock]' \
     --output table
   ```

2. **Verifique Security Groups disponíveis**:
   ```bash
   # Liste SGs que permitem HTTP e SSH
   aws ec2 describe-security-groups \
     --query 'SecurityGroups[].[GroupId,GroupName,Description]' \
     --output table
   ```

3. **Se necessário, crie Security Group básico**:
   - **Name**: `sg-asg-web`
   - **Description**: Auto Scaling Group web servers
   - **Inbound rules**:
     - HTTP (80) from 0.0.0.0/0
     - SSH (22) from Your IP

### 3. Criar Launch Template

1. **Acesse Launch Templates**:
   - **EC2 > Launch Templates > Create launch template**

2. **Configure template básico**:
   - **Launch template name**: `lt-web-target-tracking`
   - **Template version description**: Target tracking scaling demo
   - **Auto Scaling guidance**: Provide guidance to help me set up a template for use with Auto Scaling

3. **Configure Application and OS Images**:
   - **AMI**: Amazon Linux 2023 AMI (HVM)
   - **Architecture**: 64-bit (x86)

4. **Configure Instance type**:
   - **Instance type**: t3.micro (Free Tier eligible)

5. **Configure Key pair**:
   - **Key pair name**: Selecione par existente ou create new
   - **Necessário para SSH**: Para teste e troubleshooting

6. **Configure Network settings**:
   - **Subnet**: Don't include in launch template
   - **Security groups**: Selecione `sg-asg-web` (ou SG criado)
   - **Auto-assign public IP**: Enable

7. **Configure User data** (Advanced details):
   ```bash
   #!/bin/bash
   
   # Update system and install packages
   yum update -y
   yum install -y httpd stress htop
   
   # Start Apache web server
   systemctl start httpd
   systemctl enable httpd
   
   # Create simple webpage with instance info
   cat > /var/www/html/index.html << 'EOF'
   <!DOCTYPE html>
   <html>
   <head>
       <title>ASG Target Tracking Demo</title>
       <style>
           body { font-family: Arial; text-align: center; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); }
           .container { margin: 50px auto; padding: 40px; background: white; border-radius: 10px; max-width: 600px; }
           .info { background: #f0f0f0; padding: 20px; margin: 20px 0; border-radius: 5px; }
       </style>
   </head>
   <body>
       <div class="container">
           <h1>🚀 Auto Scaling Group Demo</h1>
           <div class="info">
               <h2>Server Information</h2>
               <p><strong>Hostname:</strong> HOSTNAME_PLACEHOLDER</p>
               <p><strong>Instance ID:</strong> INSTANCE_ID_PLACEHOLDER</p>
               <p><strong>Availability Zone:</strong> AZ_PLACEHOLDER</p>
               <p><strong>Time:</strong> <span id="time"></span></p>
           </div>
           <p>Target Tracking Policy: CPU 60%</p>
       </div>
       <script>
           // Replace placeholders
           document.body.innerHTML = document.body.innerHTML
               .replace('HOSTNAME_PLACEHOLDER', window.location.hostname)
               .replace('INSTANCE_ID_PLACEHOLDER', 'Loading...')
               .replace('AZ_PLACEHOLDER', 'Loading...');
           
           // Update time
           setInterval(() => {
               document.getElementById('time').textContent = new Date().toLocaleString();
           }, 1000);
           
           // Fetch instance metadata (simplified for demo)
           fetch('/latest/meta-data/instance-id').then(r => r.text()).then(id => {
               document.body.innerHTML = document.body.innerHTML.replace('Loading...', id);
           }).catch(() => {});
       </script>
   </body>
   </html>
   EOF
   
   # Replace placeholders with actual instance data
   TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
   INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
   AZ=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)
   HOSTNAME=$(hostname)
   
   sed -i "s/HOSTNAME_PLACEHOLDER/$HOSTNAME/g" /var/www/html/index.html
   sed -i "s/INSTANCE_ID_PLACEHOLDER/$INSTANCE_ID/g" /var/www/html/index.html
   sed -i "s/AZ_PLACEHOLDER/$AZ/g" /var/www/html/index.html
   
   # Install CloudWatch Agent (optional for detailed monitoring)
   yum install -y amazon-cloudwatch-agent
   ```

8. **Create launch template**

### 4. Criar Auto Scaling Group

1. **Acesse Auto Scaling Groups**:
   - **EC2 > Auto Scaling Groups > Create Auto Scaling group**

2. **Step 1: Choose launch template**:
   - **Auto Scaling group name**: `asg-web-target-tracking`
   - **Launch template**: `lt-web-target-tracking`
   - **Version**: Default (Latest)
   - **Next**

3. **Step 2: Choose instance launch options**:
   - **VPC**: Selecione VPC padrão ou específica
   - **Availability Zones and subnets**: 
     - Selecione **ao menos 2 subnets públicas** em AZs diferentes
     - Ex: us-east-1a e us-east-1b (ou sa-east-1a e sa-east-1c)
   - **Instance type requirements**: Use launch template
   - **Next**

4. **Step 3: Configure advanced options**:
   - **Load balancing**: No load balancer
   - **Health checks**: EC2 (default)
   - **Health check grace period**: 300 seconds
   - **Additional settings**: Default
   - **Next**

5. **Step 4: Configure group size and scaling**:
   - **Group size**:
     - **Desired capacity**: 1
     - **Minimum capacity**: 1
     - **Maximum capacity**: 4
   
   - **Scaling policies**:
     - **Target tracking scaling policy**: ✅ Enabled
     - **Policy name**: `target-tracking-cpu-60`
     - **Metric type**: Average CPU utilization
     - **Target value**: 60
     - **Instance warmup**: 300 seconds
     - **Disable scale-in**: ❌ (permitir scale-in)
   
   - **Instance maintenance policy**: No policy
   - **Next**

6. **Step 5: Add notifications** (opcional):
   - Skip notifications para este lab
   - **Next**

7. **Step 6: Add tags**:
   - **Key**: `Name` | **Value**: `asg-web-instance`
   - **Key**: `Environment` | **Value**: `Lab`
   - **Key**: `Purpose` | **Value**: `TargetTrackingDemo`
   - **Next**

8. **Step 7: Review**:
   - Revise configurações
   - **Create Auto Scaling group**

### 5. Verificar ASG Inicial

1. **Monitore lançamento da primeira instância**:
   - **Auto Scaling Groups > asg-web-target-tracking**
   - **Activity tab**: Observe atividade "Launching a new EC2 instance"
   - **Instance management tab**: Veja instância sendo criada

2. **Verifique instância EC2**:
   - **EC2 > Instances**
   - Localize instância com tag `asg-web-instance`
   - Aguarde **Status checks: 2/2 checks passed**

3. **Teste aplicação web**:
   - Copie **Public IPv4 address** da instância
   - Acesse no navegador: `http://ip-publico`
   - **Resultado esperado**: Página mostrando informações da instância

### 6. Simular Carga de CPU e Observar Scale-Out

1. **Conecte via SSH à instância**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-da-instancia
   ```

2. **Verifique ferramentas instaladas**:
   ```bash
   # Verifique CPU atual
   htop
   # Saia com 'q'
   
   # Teste stress tool
   stress --version
   ```

3. **Inicie carga de CPU sustentada**:
   ```bash
   # Gere 100% CPU em 1 core por 10 minutos
   echo "Iniciando carga de CPU por 600 segundos (10 minutos)..."
   sudo stress --cpu 1 --timeout 600 &
   
   # Monitore CPU em tempo real
   htop
   ```

4. **Monitore scaling no console AWS**:
   - **Auto Scaling Groups > asg-web-target-tracking**
   - **Activity tab**: Atualize a cada 1-2 minutos
   - **Resultado esperado**: Após ~3-5 minutos, veja "Launching a new EC2 instance"

5. **Observe múltiplas instâncias sendo criadas**:
   ```bash
   # Em outra sessão SSH ou CloudShell
   watch -n 30 'aws ec2 describe-instances \
     --filters "Name=tag:Name,Values=asg-web-instance" "Name=instance-state-name,Values=running,pending" \
     --query "Reservations[].Instances[].[InstanceId,State.Name,PrivateIpAddress]" \
     --output table'
   ```

### 7. Monitorar Métricas no CloudWatch

1. **Acesse CloudWatch Metrics**:
   - **CloudWatch > Metrics > All metrics**
   - **AWS/EC2 > Per-Instance Metrics**
   - **CPUUtilization**: Selecione instâncias do ASG

2. **Configure visualização**:
   - **Statistic**: Average
   - **Period**: 1 minute
   - **Time range**: Last 1 hour
   - Observe CPU subindo para ~100% e novos targets aparecendo

3. **Visualize métricas do Auto Scaling**:
   - **AWS/AutoScaling > Auto Scaling Group Metrics**
   - Métricas importantes:
     - **GroupDesiredCapacity**: Capacidade desejada
     - **GroupInServiceInstances**: Instâncias em serviço
     - **GroupTotalInstances**: Total de instâncias

### 8. Testar Scale-In (Redução)

1. **Aguarde stress tool terminar** (após 10 minutos):
   ```bash
   # Verifique se ainda está rodando
   ps aux | grep stress
   
   # Se necessário, pare manualmente
   sudo pkill stress
   
   # Monitore CPU voltando ao normal
   htop
   ```

2. **Observe scale-in automático**:
   - **Auto Scaling Groups > Activity tab**
   - **Resultado esperado**: Após ~10-15 minutos com CPU baixa, veja "Terminating EC2 instance"
   - Instâncias extras serão removidas até chegar à capacidade mínima (1)

3. **Monitore no CloudWatch**:
   - CPU das instâncias deve cair para ~1-5%
   - GroupDesiredCapacity deve reduzir gradualmente

### 9. Testar Diferentes Cenários

1. **Teste com múltiplos cores**:
   ```bash
   # SSH para instância remanescente
   # Use stress em múltiplos cores
   sudo stress --cpu 2 --timeout 300
   
   # Observe scaling mais agressivo
   ```

2. **Teste manual de capacidade**:
   ```bash
   # Altere capacidade desejada manualmente
   aws autoscaling set-desired-capacity \
     --auto-scaling-group-name asg-web-target-tracking \
     --desired-capacity 3 \
     --honor-cooldown
   ```

3. **Teste health check**:
   ```bash
   # SSH para uma instância
   # Pare Apache para simular falha
   sudo systemctl stop httpd
   
   # ASG detectará instância unhealthy e criará nova
   ```

### 10. Analisar Configurações Avançadas

1. **Examine scaling policies criadas**:
   - **Auto Scaling Groups > Automatic scaling tab**
   - Observe policies criadas automaticamente:
     - Target tracking scale-out policy
     - Target tracking scale-in policy

2. **Visualize alarmes CloudWatch criados**:
   - **CloudWatch > Alarms**
   - Procure alarmes com nomes como `TargetTracking-asg-web-target-tracking-*`

3. **Teste cooldown periods**:
   ```bash
   # Verifique atividades recentes
   aws autoscaling describe-scaling-activities \
     --auto-scaling-group-name asg-web-target-tracking \
     --max-items 10
   ```

### 11. Limpeza Responsável de Recursos

1. **Delete Auto Scaling Group**:
   - **Auto Scaling Groups > asg-web-target-tracking**
   - **Actions > Delete**
   - Digite nome do ASG para confirmar
   - **Delete**: Remove automaticamente todas as instâncias

2. **Delete Launch Template**:
   - **EC2 > Launch Templates**
   - Selecione `lt-web-target-tracking`
   - **Actions > Delete template**

3. **Verifique terminação de instâncias**:
   - **EC2 > Instances**
   - Todas as instâncias do ASG devem estar `terminated`

4. **Cleanup adicional**:
   ```bash
   # Verifique se não há recursos órfãos
   aws autoscaling describe-auto-scaling-groups \
     --query 'AutoScalingGroups[?contains(AutoScalingGroupName, `asg-web`)]'
   
   aws ec2 describe-launch-templates \
     --query 'LaunchTemplates[?contains(LaunchTemplateName, `lt-web`)]'
   ```

5. **Delete Security Group** (se criado especificamente):
   - **EC2 > Security Groups**
   - Delete `sg-asg-web` se não for mais necessário

## ✅ Conclusão

Você dominou os conceitos fundamentais de Auto Scaling com Target Tracking:

**✅ Checklist de Conquistas:**
- [ ] Conceitos de Auto Scaling Group compreendidos
- [ ] Launch Template criado com User Data personalizado
- [ ] ASG configurado com capacidades mín/máx/desejada
- [ ] Target Tracking Policy implementada (CPU 60%)
- [ ] Scale-out observado durante alta carga de CPU
- [ ] Múltiplas instâncias lançadas automaticamente
- [ ] Métricas CloudWatch monitoradas em tempo real
- [ ] Scale-in observado após redução de carga
- [ ] Diferentes cenários de scaling testados
- [ ] Health checks e substituição de instâncias demonstrados
- [ ] Limpeza responsável de recursos executada

**🎓 Conceitos Reforçados:**
* **Auto Scaling Groups**: Gerenciamento automático de capacidade
* **Target Tracking**: Política de scaling mais eficiente e inteligente
* **Launch Templates**: Templates reutilizáveis para configuração de instâncias
* **CloudWatch Integration**: Métricas driving scaling decisions
* **Scale-out vs Scale-in**: Comportamentos de aumento e redução de capacidade
* **Cooldown periods**: Prevenção de scaling oscilante
* **Health checks**: Detecção e substituição automática de instâncias com falha
