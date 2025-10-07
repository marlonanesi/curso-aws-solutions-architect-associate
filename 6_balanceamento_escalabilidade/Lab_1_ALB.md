## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 1: Application Load Balancer com EC2 e Round-Robin

## 🎯 Objetivo

Configurar um Application Load Balancer (ALB) distribuindo tráfego entre duas instâncias EC2, demonstrando o comportamento round-robin para equilibrar carga e garantir alta disponibilidade de aplicações web. **Nível: Básico**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> ALB: 750 horas/mês incluídas no Free Tier (12 meses). Instâncias EC2 t2.micro também incluídas.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * ALB é cobrado por hora de execução e por LCU (Load Balancer Capacity Units)
> * Instâncias em múltiplas AZs podem gerar custos de transferência de dados
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Compreender Conceitos de Load Balancing

**O que é Round-Robin?**

Round-Robin é um algoritmo simples de balanceamento de carga onde cada nova requisição é direcionada sequencialmente para a próxima instância disponível. É como distribuir cartas de um baralho - uma para cada jogador em ordem, voltando ao primeiro quando terminar a rodada.

**Conceitos importantes:**
- **Application Load Balancer (ALB)**: Load balancer de camada 7 (HTTP/HTTPS)
- **Target Group**: Agrupamento lógico de instâncias que recebem tráfego
- **Health Check**: Verificação automática se instâncias estão saudáveis
- **Cross-AZ**: Distribuição entre diferentes zonas de disponibilidade

### 2. Criar Duas Instâncias EC2 em AZs Diferentes

1. **Acesse o console EC2**: Navigate to **EC2 > Launch Instance**

2. **Configure primeira instância**:
   - **Name**: `web-server-1`
   - **AMI**: Amazon Linux 2023 (Free Tier eligible)
   - **Instance type**: t2.micro
   - **Subnet**: Subnet pública na `us-east-1a` (ou sua primeira AZ)
   - **Auto-assign public IP**: Enable
   - **Security Group**: Crie `sg-web-servers`
     - SSH (22) do seu IP
     - HTTP (80) from 0.0.0.0/0

3. **User Data para primeira instância**:
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd
   systemctl start httpd
   systemctl enable httpd
   
   # Criar página identificando servidor 1
   cat > /var/www/html/index.html << 'EOF'
   <!DOCTYPE html>
   <html>
   <head>
       <title>Web Server 1</title>
       <style>
           body { font-family: Arial; text-align: center; margin: 50px; }
           .server1 { color: blue; background: #e3f2fd; padding: 20px; border-radius: 10px; }
       </style>
   </head>
   <body>
       <div class="server1">
           <h1>🟦 SERVIDOR 1</h1>
           <h2>Hostname: $(hostname)</h2>
           <h3>IP Local: $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)</h3>
           <p>Timestamp: $(date)</p>
       </div>
   </body>
   </html>
   EOF
   
   # Substituir variáveis
   sed -i "s/\$(hostname)/$(hostname)/g" /var/www/html/index.html
   sed -i "s/\$(curl -s http:\/\/169.254.169.254\/latest\/meta-data\/local-ipv4)/$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)/g" /var/www/html/index.html
   sed -i "s/\$(date)/$(date)/g" /var/www/html/index.html
   ```

4. **Configure segunda instância**:
   - **Name**: `web-server-2`
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t2.micro
   - **Subnet**: Subnet pública na `us-east-1b` (AZ diferente da primeira)
   - **Security Group**: Use o mesmo `sg-web-servers`

5. **User Data para segunda instância**:
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd
   systemctl start httpd
   systemctl enable httpd
   
   # Criar página identificando servidor 2
   cat > /var/www/html/index.html << 'EOF'
   <!DOCTYPE html>
   <html>
   <head>
       <title>Web Server 2</title>
       <style>
           body { font-family: Arial; text-align: center; margin: 50px; }
           .server2 { color: orange; background: #fff3e0; padding: 20px; border-radius: 10px; }
       </style>
   </head>
   <body>
       <div class="server2">
           <h1>🟧 SERVIDOR 2</h1>
           <h2>Hostname: $(hostname)</h2>
           <h3>IP Local: $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)</h3>
           <p>Timestamp: $(date)</p>
       </div>
   </body>
   </html>
   EOF
   
   # Substituir variáveis
   sed -i "s/\$(hostname)/$(hostname)/g" /var/www/html/index.html
   sed -i "s/\$(curl -s http:\/\/169.254.169.254\/latest\/meta-data\/local-ipv4)/$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)/g" /var/www/html/index.html
   sed -i "s/\$(date)/$(date)/g" /var/www/html/index.html
   ```

6. **Teste as instâncias individualmente**:
   - Acesse `http://ip-publico-instancia-1`
   - Acesse `http://ip-publico-instancia-2`
   - Confirme que páginas diferentes aparecem

### 3. Criar Target Group para as Instâncias

1. **Acesse Target Groups**: Navigate to **EC2 > Target Groups > Create target group**

2. **Configure o Target Group**:
   - **Target type**: Instances
   - **Target group name**: `tg-web-servers`
   - **Protocol**: HTTP
   - **Port**: 80
   - **VPC**: Sua VPC
   - **Protocol version**: HTTP1

3. **Configure Health Check**:
   - **Health check protocol**: HTTP
   - **Health check path**: `/`
   - **Advanced health check settings**:
     - Port: Traffic port
     - Healthy threshold: 2
     - Unhealthy threshold: 2
     - Timeout: 5 seconds
     - Interval: 30 seconds
     - Success codes: 200

4. **Register targets**:
   - **Available instances**: Selecione ambas as instâncias `web-server-1` e `web-server-2`
   - **Port**: 80
   - **Include as pending below**: Click para adicionar
   - **Create target group**

5. **Verifique o health status**:
   - Aguarde alguns minutos
   - Status deve mudar de `initial` → `healthy`

### 4. Criar Security Group para ALB

1. **Crie Security Group para ALB**:
   - **Name**: `sg-alb-web`
   - **Description**: Security group for Application Load Balancer
   - **VPC**: Sua VPC

2. **Configure regras de entrada**:
   - **Type**: HTTP
   - **Protocol**: TCP
   - **Port range**: 80
   - **Source**: 0.0.0.0/0 (anywhere)

3. **Configure regras de saída**:
   - **Type**: HTTP
   - **Protocol**: TCP
   - **Port range**: 80
   - **Destination**: Security Group das instâncias (`sg-web-servers`)

### 5. Criar Application Load Balancer

1. **Acesse Load Balancers**: Navigate to **EC2 > Load Balancers > Create Load Balancer**

2. **Selecione tipo**: Choose **Application Load Balancer**

3. **Configure básico**:
   - **Load balancer name**: `alb-web-demo`
   - **Scheme**: Internet-facing
   - **IP address type**: IPv4

4. **Configure network mapping**:
   - **VPC**: Sua VPC
   - **Mappings**: Selecione pelo menos 2 AZs disponíveis
     - AZ 1: us-east-1a (subnet pública)
     - AZ 2: us-east-1b (subnet pública)

5. **Configure security groups**:
   - **Security groups**: Selecione `sg-alb-web`
   - Remova o security group default se estiver selecionado

6. **Configure listeners and routing**:
   - **Protocol**: HTTP
   - **Port**: 80
   - **Default action**: Forward to target group
   - **Target group**: `tg-web-servers`

7. **Create load balancer**

### 6. Testar Balanceamento Round-Robin

1. **Obtenha o DNS name do ALB**:
   - Acesse **EC2 > Load Balancers**
   - Selecione `alb-web-demo`
   - Copie o **DNS name** (algo como `alb-web-demo-123456789.us-east-1.elb.amazonaws.com`)

2. **Teste via navegador**:
   - Acesse `http://dns-name-do-alb`
   - Recarregue a página várias vezes (F5)
   - Observe a alternância entre Servidor 1 (azul) e Servidor 2 (laranja)

3. **Teste via linha de comando**:
   ```bash
   # Execute várias vezes para ver alternância
   curl http://dns-name-do-alb
   curl http://dns-name-do-alb
   curl http://dns-name-do-alb
   curl http://dns-name-do-alb
   ```

4. **Monitore no console**:
   - **Target Groups > tg-web-servers > Targets**
   - Verifique que ambas instâncias estão `healthy`
   - **Load Balancers > alb-web-demo > Monitoring**
   - Observe as métricas de requisições

### 7. Testar Comportamento de Falha

1. **Simule falha do Servidor 1**:
   - Conecte-se via SSH à `web-server-1`
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-servidor-1
   sudo systemctl stop httpd
   ```

2. **Observe o comportamento**:
   - Acesse o ALB pelo navegador
   - Todas as requisições devem ir para Servidor 2
   - No Target Group, observe status de `web-server-1` mudando para `unhealthy`

3. **Restaure o serviço**:
   ```bash
   sudo systemctl start httpd
   ```

4. **Confirme recuperação**:
   - Aguarde alguns minutos
   - Status deve voltar para `healthy`
   - Round-robin deve voltar a funcionar

### 8. Analisar Métricas e Logs

1. **CloudWatch Metrics**:
   - Acesse **CloudWatch > Metrics > AWS/ApplicationELB**
   - Observe métricas como:
     - RequestCount
     - TargetResponseTime
     - HTTPCode_Target_2XX_Count

2. **Access Logs** (opcional):
   - Configure access logs no S3 para análise detalhada
   - **Load Balancers > alb-web-demo > Attributes > Access logs**

### 9. Limpeza de Recursos

1. **Delete o Load Balancer**:
   - **EC2 > Load Balancers**
   - Selecione `alb-web-demo`
   - **Actions > Delete**

2. **Delete o Target Group**:
   - **EC2 > Target Groups**
   - Selecione `tg-web-servers`
   - **Actions > Delete**

3. **Termine as instâncias**:
   - **EC2 > Instances**
   - Selecione ambas as instâncias
   - **Instance State > Terminate Instance**

4. **Delete Security Groups**:
   - **EC2 > Security Groups**
   - Delete `sg-alb-web` e `sg-web-servers`

## ✅ Conclusão

Você configurou com sucesso um Application Load Balancer com distribuição round-robin:

**✅ Checklist de Conquistas:**
- [ ] Duas instâncias EC2 criadas em AZs diferentes
- [ ] Páginas web distintivas configuradas em cada servidor
- [ ] Target Group criado e configurado com health checks
- [ ] Security Groups configurados adequadamente
- [ ] Application Load Balancer configurado e funcionando
- [ ] Comportamento round-robin observado e testado
- [ ] Tolerância a falhas demonstrada
- [ ] Métricas de monitoramento analisadas
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Load balancing**: Distribuição de tráfego entre múltiplas instâncias
* **Round-robin algorithm**: Distribuição sequencial e equilibrada
* **High availability**: Tolerância a falhas com múltiplas AZs
* **Health checks**: Monitoramento automático da saúde das instâncias
* **Target Groups**: Agrupamento lógico de recursos para balanceamento
* **Security Groups**: Controle de tráfego entre ALB e instâncias
