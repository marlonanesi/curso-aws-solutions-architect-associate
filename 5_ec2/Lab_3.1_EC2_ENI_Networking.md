## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 3.1: ENI (Elastic Network Interface) - Networking Avançado

## 🎯 Objetivo

Dominar o uso de ENIs (Elastic Network Interfaces) para criar arquiteturas de rede flexíveis, implementar failover de interfaces de rede e entender como gerenciar múltiplas interfaces em instâncias EC2. **Nível: Avançado**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> ENIs não geram custos adicionais além das instâncias EC2. IPs elásticos são gratuitos quando anexados.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * IPs elásticos não anexados são cobrados (taxa de idle)
> * ENIs órfãs (não anexadas) não geram custos, mas podem confundir gerenciamento
> * Transferência de dados entre AZs pode gerar custos
> * Sempre **remova recursos não utilizados** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender Conceitos Fundamentais de ENI

**O que são ENIs?**

ENIs (Elastic Network Interfaces) são interfaces de rede virtuais que você pode anexar a instâncias EC2. Funcionam como "placas de rede virtuais" que podem ser movidas entre instâncias, mantendo configurações, IPs e endereços MAC.

**Características das ENIs:**
- **Flexíveis**: Podem ser anexadas/desanexadas de instâncias
- **Persistentes**: Mantêm configurações independente da instância
- **MAC Address fixo**: Útil para licenciamento baseado em MAC
- **Multiple IPs**: Podem ter múltiplos IPs privados e elásticos
- **Security Groups**: Cada ENI pode ter security groups diferentes

**Casos de uso principais:**
- **Failover**: Mover interface entre instâncias para alta disponibilidade
- **Dual-homing**: Conectar instância a múltiplas subnets
- **Separação de tráfego**: Management vs production traffic
- **Licenciamento**: Manter MAC address para software licenciado
- **Load balancing**: Distribuir carga entre interfaces

**Analogias para facilitar o entendimento:**
- **ENI**: Como uma placa de rede USB que você pode trocar entre computadores
- **Failover**: Como trocar um cabo de rede de um servidor para outro
- **Dual-homing**: Como ter duas placas de rede no mesmo computador

### 2. Preparar Ambiente de Rede

1. **Identifique sua VPC e subnets**:
   - Acesse **VPC > Your VPCs**
   - Anote a VPC que será usada
   - Acesse **VPC > Subnets**
   - Identifique pelo menos 2 subnets públicas em AZs diferentes

2. **Crie Security Group para ENI**:
   - Acesse **EC2 > Security Groups > Create security group**
   - **Name**: `sg-eni-advanced`
   - **Description**: `Security group para ENI lab avançado`
   - **VPC**: Sua VPC
   - **Inbound rules**:
     - SSH (22) do seu IP
     - HTTP (80) from 0.0.0.0/0
     - HTTPS (443) from 0.0.0.0/0
     - ICMP from VPC CIDR (para ping entre instâncias)
   - **Outbound rules**: All traffic (padrão)

### 3. Criar ENI Independente

1. **Crie primeira ENI**:
   - Acesse **EC2 > Network Interfaces > Create network interface**
   - **Description**: `eni-web-primary`
   - **Subnet**: Selecione subnet pública na AZ-1a
   - **Security groups**: `sg-eni-advanced`
   - **Private IP**: (deixe automático ou especifique um IP específico)
   - **Tags**: 
     - Name: `eni-web-primary`
     - Purpose: `primary-interface`

2. **Crie segunda ENI para failover**:
   - **Description**: `eni-web-failover`
   - **Subnet**: Selecione subnet pública na AZ-1b (diferente da primeira)
   - **Security groups**: `sg-eni-advanced`
   - **Tags**: 
     - Name: `eni-web-failover`
     - Purpose: `failover-interface`

3. **Anote informações das ENIs**:
   - Private IP addresses de ambas
   - ENI IDs (eni-1234567890abcdef0)
   - Availability Zones

### 4. Lançar Instância EC2 Base

1. **Lance instância primária**:
   - **Name**: `ec2-eni-primary`
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t3.micro
   - **Subnet**: Mesma da primeira ENI (AZ-1a)
   - **Security group**: `sg-eni-advanced`
   - **User data**:
     ```bash
     #!/bin/bash
     yum update -y
     yum install -y httpd htop net-tools
     systemctl enable httpd
     systemctl start httpd
     
     # Página inicial identificando a interface
     cat > /var/www/html/index.html << 'EOF'
     <!DOCTYPE html>
     <html>
     <head>
         <title>ENI Lab - Servidor Primário</title>
         <style>
             body { font-family: Arial; margin: 40px; background: #e7f3ff; }
             .container { background: white; padding: 20px; border-radius: 10px; }
             .primary { color: #2e7d32; }
         </style>
     </head>
     <body>
         <div class="container">
             <h1 class="primary">🟢 Servidor Primário Ativo</h1>
             <p><strong>Interface:</strong> ENI Primária</p>
             <p><strong>Status:</strong> Operacional</p>
             <p><strong>Última atualização:</strong> <span id="time"></span></p>
         </div>
         <script>
             document.getElementById('time').innerHTML = new Date().toLocaleString();
             setInterval(function() {
                 document.getElementById('time').innerHTML = new Date().toLocaleString();
             }, 1000);
         </script>
     </body>
     </html>
     EOF
     ```

2. **Lance instância secundária**:
   - **Name**: `ec2-eni-secondary`
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t3.micro
   - **Subnet**: Mesma da segunda ENI (AZ-1b)
   - **Security group**: `sg-eni-advanced`
   - **User data**:
     ```bash
     #!/bin/bash
     yum update -y
     yum install -y httpd htop net-tools
     systemctl enable httpd
     systemctl start httpd
     
     # Página identificando como servidor secundário
     cat > /var/www/html/index.html << 'EOF'
     <!DOCTYPE html>
     <html>
     <head>
         <title>ENI Lab - Servidor Secundário</title>
         <style>
             body { font-family: Arial; margin: 40px; background: #fff3e0; }
             .container { background: white; padding: 20px; border-radius: 10px; }
             .secondary { color: #f57c00; }
         </style>
     </head>
     <body>
         <div class="container">
             <h1 class="secondary">🟡 Servidor Secundário (Standby)</h1>
             <p><strong>Interface:</strong> ENI Secundária</p>
             <p><strong>Status:</strong> Standby</p>
             <p><strong>Última atualização:</strong> <span id="time"></span></p>
         </div>
         <script>
             document.getElementById('time').innerHTML = new Date().toLocaleString();
             setInterval(function() {
                 document.getElementById('time').innerHTML = new Date().toLocaleString();
             }, 1000);
         </script>
     </body>
     </html>
     EOF
     ```

### 5. Anexar ENIs às Instâncias

1. **Anexe ENI primária à instância primária**:
   - Acesse **EC2 > Network Interfaces**
   - Selecione `eni-web-primary`
   - **Actions > Attach**
   - **Instance**: `ec2-eni-primary`
   - **Device index**: 1 (deixe eth0 como primária da instância)
   - **Attach**

2. **Anexe ENI secundária à instância secundária**:
   - Selecione `eni-web-failover`
   - **Actions > Attach**
   - **Instance**: `ec2-eni-secondary`
   - **Device index**: 1
   - **Attach**

### 6. Configurar Interfaces nas Instâncias

1. **Conecte-se à instância primária**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-primaria
   ```

2. **Verifique interfaces de rede**:
   ```bash
   # Liste todas as interfaces
   ip addr show
   
   # Verifique interfaces ativas
   ip link show
   
   # Veja informações de roteamento
   ip route show
   
   # Lista interfaces com ifconfig (se instalado)
   sudo yum install -y net-tools
   ifconfig
   ```

3. **Configure a segunda interface (se necessário)**:
   ```bash
   # Verifique se eth1 está ativa
   sudo ip link set eth1 up
   
   # Configure DHCP na interface se não estiver configurada
   sudo dhclient eth1
   
   # Verifique se recebeu IP
   ip addr show eth1
   ```

4. **Teste conectividade entre interfaces**:
   ```bash
   # Ping para a interface da outra instância
   ping -c 4 ip-privado-da-eni-secundaria
   ```

5. **Repita processo na instância secundária**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-secundaria
   ip addr show
   sudo ip link set eth1 up
   sudo dhclient eth1
   ```

### 7. Alocar e Associar IPs Elásticos

1. **Aloque IPs elásticos**:
   - Acesse **EC2 > Elastic IPs > Allocate Elastic IP address**
   - **Tags**: Name = `eip-eni-primary`
   - **Allocate**
   - Repita para criar `eip-eni-failover`

2. **Associe IP elástico à ENI primária**:
   - Selecione o IP elástico `eip-eni-primary`
   - **Actions > Associate Elastic IP address**
   - **Resource type**: Network interface
   - **Network interface**: `eni-web-primary`
   - **Private IP**: Selecione o IP privado da ENI
   - **Associate**

3. **Teste acesso via IP elástico**:
   - Acesse http://ip-elastico-primario
   - Deve mostrar a página do servidor primário

### 8. Simular Failover de ENI

1. **Desanexe ENI da instância primária**:
   - Acesse **EC2 > Network Interfaces**
   - Selecione `eni-web-primary`
   - **Actions > Detach**
   - Confirme o detach

2. **Anexe ENI à instância secundária**:
   - Com a mesma ENI selecionada
   - **Actions > Attach**
   - **Instance**: `ec2-eni-secondary`
   - **Device index**: 2 (para não conflitar com eth1 existente)
   - **Attach**

3. **Configure interface na instância secundária**:
   ```bash
   # Na instância secundária
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-secundaria
   
   # Verifique novas interfaces
   ip addr show
   
   # Ative a nova interface (provavelmente eth2)
   sudo ip link set eth2 up
   sudo dhclient eth2
   
   # Verifique se recebeu o IP da ENI
   ip addr show eth2
   ```

4. **Teste failover**:
   - Acesse http://ip-elastico-primario
   - Agora deve mostrar erro ou página da instância secundária
   - Isso demonstra que o IP elástico "seguiu" a ENI

### 9. Implementar High Availability com Script

1. **Crie script de verificação de saúde**:
   ```bash
   # Na instância que recebeu a ENI
   sudo tee /home/ec2-user/health-check.sh << 'EOF'
   #!/bin/bash
   
   # Script simples de health check e failover
   LOG_FILE="/var/log/eni-failover.log"
   
   log_message() {
       echo "$(date): $1" >> $LOG_FILE
   }
   
   check_primary_health() {
       # Substitua pelo IP da instância primária
       PRIMARY_IP="ip-privado-primario"
       
       if ping -c 2 $PRIMARY_IP > /dev/null 2>&1; then
           return 0  # Primário está saudável
       else
           return 1  # Primário não responde
       fi
   }
   
   # Exemplo de verificação
   if check_primary_health; then
       log_message "Primário está saudável"
   else
       log_message "Primário não responde - failover necessário"
   fi
   EOF
   
   chmod +x /home/ec2-user/health-check.sh
   ```

### 10. Explorar Funcionalidades Avançadas

1. **Multiple IPs na mesma ENI**:
   - Selecione uma ENI no console
   - **Actions > Manage IP addresses**
   - **Assign new IP**
   - Configure IP secundário

2. **IPv6 addresses** (se suportado na região):
   - Na mesma tela de gerenciamento
   - **Assign new IPv6 address**

3. **Enhanced networking** (SR-IOV):
   - Disponível em tipos de instância suportados
   - Melhora performance de rede
   - Habilitado automaticamente em instâncias compatíveis

### 11. Limpeza de Recursos

1. **Desassocie IPs elásticos**:
   - **EC2 > Elastic IPs**
   - Selecione IPs criados
   - **Actions > Disassociate Elastic IP address**
   - **Actions > Release Elastic IP address**

2. **Desanexe ENIs**:
   - **EC2 > Network Interfaces**
   - Selecione ENIs criadas
   - **Actions > Detach**

3. **Delete ENIs**:
   - Após desanexar, **Actions > Delete**

4. **Termine instâncias**:
   - **EC2 > Instances**
   - Selecione ambas as instâncias
   - **Instance State > Terminate Instance**

5. **Delete Security Group**:
   - **EC2 > Security Groups**
   - Delete `sg-eni-advanced`

## ✅ Conclusão

Você dominou o uso avançado de ENIs para arquiteturas de rede flexíveis:

**✅ Checklist de Conquistas:**
- [ ] Conceitos fundamentais de ENI compreendidos
- [ ] ENIs independentes criadas em múltiplas AZs
- [ ] Instâncias EC2 lançadas com configurações personalizadas
- [ ] ENIs anexadas e configuradas nas instâncias
- [ ] Interfaces de rede configuradas no sistema operacional
- [ ] IPs elásticos alocados e associados a ENIs
- [ ] Failover de ENI simulado entre instâncias
- [ ] Script de health check implementado
- [ ] Funcionalidades avançadas exploradas
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Network flexibility**: ENIs podem ser movidas entre instâncias
* **Failover capabilities**: Implementação de alta disponibilidade
* **MAC address persistence**: Importante para licenciamento
* **Multi-homing**: Conectar instância a múltiplas redes
* **Elastic IP mobility**: IPs elásticos seguem as ENIs
* **Advanced networking**: SR-IOV e enhanced networking
