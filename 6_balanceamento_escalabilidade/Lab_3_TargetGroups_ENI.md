## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 3: Target Group com ENIs e Load Balancer

## 🎯 Objetivo

Criar um **Target Group do tipo IP** e registrar **ENIs (Elastic Network Interfaces)** associadas a instâncias EC2, permitindo que o Load Balancer se conecte diretamente a interfaces específicas para maior controle e flexibilidade. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> ENIs: gratuitas quando associadas a instâncias. ALB: 750 horas/mês incluídas no Free Tier (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * ENIs detached geram custo de $0.005/hora (~$3.60/mês)
> * IPs Elásticos não utilizados custam $0.005/hora
> * Sempre **detach e delete ENIs** e **release Elastic IPs** ao final do exercício

## ⭐ Passos a Executar

### 1. Compreender Conceitos de ENI e Target Groups IP

**O que são ENIs (Elastic Network Interfaces)?**

ENIs são interfaces de rede virtuais que podem ser:
- Criadas independentemente das instâncias
- Anexadas e desanexadas dinamicamente
- Movidas entre instâncias para failover
- Configuradas com múltiplos IPs privados

**Target Group tipo IP vs Instance:**
- **Instance**: Registra instâncias EC2 diretamente
- **IP**: Registra endereços IP específicos (ENIs, containers, on-premises)

**Vantagens do Target Group IP:**
- ✅ Maior flexibilidade de roteamento
- ✅ Suporte a múltiplas interfaces por instância
- ✅ Integração com containers e serviços híbridos
- ✅ Failover manual simplificado

### 2. Preparar o Ambiente Base

**Pré-requisitos**: 2 instâncias EC2 com aplicação web rodando

1. **Verifique instâncias existentes**:
   ```bash
   # Liste instâncias ativas
   aws ec2 describe-instances \
     --filters "Name=instance-state-name,Values=running" \
     --query 'Reservations[].Instances[].[InstanceId,PrivateIpAddress,SubnetId]' \
     --output table
   ```

2. **Se necessário, crie instâncias EC2**:
   - **Nome**: `web-server-eni-1` e `web-server-eni-2`
   - **AMI**: Amazon Linux 2023
   - **Instance Type**: t2.micro
   - **Subnets**: Diferentes AZs na mesma VPC
   - **Security Group**: Permita HTTP (80) e SSH (22)

3. **Configure aplicação web simples** (se não tiver):
   ```bash
   # SSH para cada instância
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   
   # Instale e configure Apache
   sudo yum update -y
   sudo yum install -y httpd
   
   # Crie página identificadora
   echo "<h1>SERVIDOR ENI 1 - $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)</h1>" | sudo tee /var/www/html/index.html
   
   sudo systemctl start httpd
   sudo systemctl enable httpd
   ```

### 3. Criar ENIs (Elastic Network Interfaces)

1. **Identifique subnets das instâncias**:
   - **EC2 > Instances**
   - Note `Subnet ID` de cada instância
   - Note `Security Group` de cada instância

2. **Crie primeira ENI**:
   - **EC2 > Network Interfaces > Create network interface**
   - **Description**: `eni-server-1`
   - **Subnet**: Mesma subnet da primeira instância
   - **Private IPv4 address**: Auto-assign ou específico
   - **Security groups**: Mesmo SG das instâncias
   - **Create network interface**

3. **Crie segunda ENI**:
   - **Description**: `eni-server-2`
   - **Subnet**: Mesma subnet da segunda instância
   - Repita configurações similares

4. **Anote IPs privados das ENIs**:
   - Na lista de Network Interfaces
   - Copie **Primary private IPv4 IP** de cada ENI
   - Exemplo: `10.0.1.150` e `10.0.2.151`

### 4. Anexar ENIs às Instâncias

1. **Anexe primeira ENI**:
   - Selecione `eni-server-1`
   - **Actions > Attach**
   - **Instance**: Escolha `web-server-eni-1`
   - **Device index**: 1 (eth0 já é usado pela interface primária)
   - **Attach**

2. **Anexe segunda ENI**:
   - Selecione `eni-server-2`
   - **Actions > Attach**
   - **Instance**: Escolha `web-server-eni-2`
   - **Device index**: 1
   - **Attach**

3. **Verifique anexação nas instâncias**:
   ```bash
   # SSH para instância
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   
   # Liste interfaces de rede
   ip addr show
   
   # Você deve ver eth0 (primária) e eth1 (ENI anexada)
   ```

### 5. Configurar Network Interfaces nas Instâncias

1. **Configure interface secundária** (em cada instância):
   ```bash
   # SSH para primeira instância
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-1
   
   # Obtenha IP da ENI anexada
   ENI_IP=$(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/$(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/)/local-ipv4s | tail -1)
   
   # Configure interface secundária
   sudo ip addr add $ENI_IP/24 dev eth1
   sudo ip link set eth1 up
   
   # Verifique configuração
   ip addr show eth1
   ```

2. **Teste conectividade da ENI**:
   ```bash
   # Teste ping interno entre ENIs
   ping -c 3 ip-da-segunda-eni
   ```

### 6. Criar Target Group do Tipo IP

1. **Crie Target Group**:
   - **EC2 > Target Groups > Create target group**
   - **Choose a target type**: IP addresses
   - **Target group name**: `tg-eni-demo`
   - **Protocol**: HTTP
   - **Port**: 80
   - **VPC**: Mesma VPC das instâncias
   - **Protocol version**: HTTP1

2. **Configure Health Check**:
   - **Health check protocol**: HTTP
   - **Health check path**: `/`
   - **Port**: Traffic port
   - **Healthy threshold**: 2
   - **Unhealthy threshold**: 2
   - **Timeout**: 5 seconds
   - **Interval**: 30 seconds
   - **Success codes**: 200

3. **Registre IPs das ENIs**:
   - **Register targets**
   - **Network**: Same VPC
   - **IPv4 address**: Digite IP da primeira ENI
   - **Port**: 80
   - **Add to list**
   - Repita para segunda ENI
   - **Create target group**

### 7. Criar ou Configurar Application Load Balancer

1. **Se não tiver ALB, crie um novo**:
   - **EC2 > Load Balancers > Create load balancer**
   - **Application Load Balancer > Create**
   - **Name**: `alb-eni-demo`
   - **Scheme**: Internet-facing
   - **IP address type**: IPv4
   - **VPC**: Mesma das instâncias
   - **Mappings**: Selecione ao menos 2 AZs
   - **Security groups**: Permita HTTP (80) de anywhere

2. **Configure Listener**:
   - **Protocol**: HTTP
   - **Port**: 80
   - **Default actions**: Forward to `tg-eni-demo`
   - **Create load balancer**

3. **Se já tiver ALB, modifique listener**:
   - **Listeners > Edit**
   - Altere **Forward to** para `tg-eni-demo`

### 8. Testar Funcionamento

1. **Aguarde Target Group ficar healthy**:
   - **Target Groups > tg-eni-demo > Targets**
   - Status deve mudar para `healthy` (~2-3 minutos)

2. **Teste acesso via ALB**:
   - Copie **DNS name** do ALB
   - Acesse no navegador: `http://dns-name-do-alb`
   - **Resultado esperado**: Vê páginas dos servidores alternando

3. **Teste via linha de comando**:
   ```bash
   # Teste múltiplas requisições
   ALB_DNS="dns-name-do-alb"
   
   echo "=== Testando load balancing via ENIs ==="
   for i in {1..6}; do
     echo "Requisição $i:"
     curl -s http://$ALB_DNS | grep -E "(SERVIDOR ENI 1|SERVIDOR ENI 2|IP:)"
     echo "---"
     sleep 1
   done
   ```

### 9. Verificar Comportamento de Failover

1. **Simule falha em uma instância**:
   ```bash
   # SSH para primeira instância
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-1
   
   # Pare o serviço web
   sudo systemctl stop httpd
   ```

2. **Monitore Target Group**:
   - **Target Groups > tg-eni-demo > Targets**
   - Observe target ficando `unhealthy`
   - ALB para de enviar tráfego para esse target

3. **Teste failover**:
   ```bash
   # Continue testando - agora só vai para instância saudável
   for i in {1..4}; do
     curl -s http://$ALB_DNS | grep -E "(SERVIDOR ENI 1|SERVIDOR ENI 2)"
     sleep 2
   done
   ```

4. **Restaure serviço**:
   ```bash
   sudo systemctl start httpd
   ```

### 10. Demonstrar Flexibilidade de ENIs

1. **Mova ENI entre instâncias** (opcional avançado):
   ```bash
   # Pare aplicação na instância atual
   sudo systemctl stop httpd
   ```

2. **Detach e reattach ENI**:
   - **EC2 > Network Interfaces**
   - Selecione ENI > **Actions > Detach**
   - Aguarde detachment
   - **Actions > Attach** para outra instância

3. **Reconfigure nova instância**:
   ```bash
   # Configure ENI na nova instância
   sudo ip addr add ip-da-eni/24 dev eth1
   sudo ip link set eth1 up
   ```

### 11. Monitorar Métricas Específicas

1. **Verifique métricas no CloudWatch**:
   - **CloudWatch > Metrics > AWS/ApplicationELB**
   - Métricas por Target Group: `tg-eni-demo`
   - **HealthyHostCount** por IP
   - **RequestCount** por IP

2. **Compare com Target Group tipo Instance**:
   - Crie TG tipo Instance para comparação
   - Observe diferenças nas métricas disponíveis

### 12. Limpeza Responsável de Recursos

1. **Delete Load Balancer**:
   - **EC2 > Load Balancers**
   - Selecione `alb-eni-demo`
   - **Actions > Delete**

2. **Delete Target Group**:
   - **EC2 > Target Groups**
   - Selecione `tg-eni-demo`
   - **Actions > Delete**

3. **Detach e delete ENIs**:
   - **EC2 > Network Interfaces**
   - Selecione cada ENI criada
   - **Actions > Detach** (aguarde conclusão)
   - **Actions > Delete network interface**

4. **Termine instâncias EC2**:
   - **EC2 > Instances**
   - Selecione instâncias criadas
   - **Instance State > Terminate Instance**

5. **Cleanup Security Groups** (se criados especificamente):
   - **EC2 > Security Groups**
   - Delete SGs não utilizados

6. **Verifique limpeza**:
   ```bash
   # Verifique se não há recursos órfãos
   aws ec2 describe-network-interfaces --filters "Name=status,Values=available"
   aws elbv2 describe-load-balancers --query 'LoadBalancers[?State.Code==`active`]'
   ```

## ✅ Conclusão

Você dominou o uso de ENIs com Load Balancers para arquiteturas flexíveis:

**✅ Checklist de Conquistas:**
- [ ] Conceitos de ENI e Target Groups IP compreendidos
- [ ] ENIs criadas e anexadas a instâncias EC2
- [ ] Interfaces secundárias configuradas no sistema operacional
- [ ] Target Group tipo IP criado e configurado
- [ ] IPs das ENIs registrados como targets
- [ ] Application Load Balancer conectado ao Target Group
- [ ] Load balancing via ENIs testado e verificado
- [ ] Comportamento de failover demonstrado
- [ ] Flexibilidade de movimentação de ENIs explorada
- [ ] Métricas específicas por IP monitoradas
- [ ] Limpeza responsável de recursos executada

**🎓 Conceitos Reforçados:**
* **ENI (Elastic Network Interface)**: Interfaces de rede flexíveis e móveis
* **Target Group IP**: Registro direto de endereços IP como targets
* **Network failover**: Movimentação de interfaces entre instâncias
* **Multi-homed instances**: Instâncias com múltiplas interfaces de rede
* **IP-based load balancing**: Balanceamento baseado em endereços específicos
* **Hybrid architectures**: Integração com recursos on-premises via IP
