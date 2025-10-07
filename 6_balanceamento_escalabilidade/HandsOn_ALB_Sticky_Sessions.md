# ⚖️ Lab: Application Load Balancer com Sticky Sessions

## Visão Geral

Neste laboratório prático, vamos configurar um Application Load Balancer (ALB) com duas instâncias EC2 para demonstrar distribuição de carga, sticky sessions e cross-zone load balancing. Você verá na prática como o ALB distribui requisições e como controlar esse comportamento.

---

## Objetivos

* Configurar ALB com múltiplas instâncias EC2
* Demonstrar distribuição de carga padrão
* Configurar e testar sticky sessions
* Entender cross-zone load balancing

---

## Etapa 1: Criando Instâncias Web

1. **Lance a primeira instância:**
   * **Nome**: `web-server-1`
   * **AMI**: Amazon Linux 2023
   * **Tipo**: t3.micro
   * **Subnet**: Escolha uma subnet pública (AZ-1a)
   * **Security Group**: Permitir HTTP (80) e SSH (22)
   * **User Data**:
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd
   systemctl start httpd
   systemctl enable httpd
   
   # Página personalizada mostrando qual servidor está respondendo
   cat > /var/www/html/index.html << 'EOF'
   <!DOCTYPE html>
   <html>
   <head>
       <title>Servidor Web 1</title>
       <style>
           body { font-family: Arial; text-align: center; margin: 50px; }
           .server1 { background: #e3f2fd; border: 3px solid #2196f3; }
           .info { background: #f5f5f5; padding: 20px; margin: 20px; }
       </style>
   </head>
   <body class="server1">
       <h1>🖥️ SERVIDOR WEB 1</h1>
       <div class="info">
           <p><strong>Hostname:</strong> <span id="hostname"></span></p>
           <p><strong>IP Privado:</strong> <span id="ip"></span></p>
           <p><strong>Timestamp:</strong> <span id="time"></span></p>
           <p><strong>Requests atendidos:</strong> <span id="counter">1</span></p>
       </div>
       
       <script>
           // Busca informações da instância
           fetch('http://169.254.169.254/latest/meta-data/hostname')
               .then(r => r.text()).then(data => document.getElementById('hostname').textContent = data);
           fetch('http://169.254.169.254/latest/meta-data/local-ipv4')
               .then(r => r.text()).then(data => document.getElementById('ip').textContent = data);
           
           // Atualiza timestamp e contador
           let counter = 1;
           setInterval(() => {
               document.getElementById('time').textContent = new Date().toLocaleString();
               document.getElementById('counter').textContent = ++counter;
           }, 1000);
       </script>
   </body>
   </html>
   EOF
   ```

2. **Lance a segunda instância:**
   * **Nome**: `web-server-2`
   * **Subnet**: Escolha subnet em AZ diferente (AZ-1b)
   * **User Data** (mude para Servidor 2):
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd
   systemctl start httpd
   systemctl enable httpd
   
   cat > /var/www/html/index.html << 'EOF'
   <!DOCTYPE html>
   <html>
   <head>
       <title>Servidor Web 2</title>
       <style>
           body { font-family: Arial; text-align: center; margin: 50px; }
           .server2 { background: #fff3e0; border: 3px solid #ff9800; }
           .info { background: #f5f5f5; padding: 20px; margin: 20px; }
       </style>
   </head>
   <body class="server2">
       <h1>🖥️ SERVIDOR WEB 2</h1>
       <div class="info">
           <p><strong>Hostname:</strong> <span id="hostname"></span></p>
           <p><strong>IP Privado:</strong> <span id="ip"></span></p>
           <p><strong>Timestamp:</strong> <span id="time"></span></p>
           <p><strong>Requests atendidos:</strong> <span id="counter">1</span></p>
       </div>
       
       <script>
           fetch('http://169.254.169.254/latest/meta-data/hostname')
               .then(r => r.text()).then(data => document.getElementById('hostname').textContent = data);
           fetch('http://169.254.169.254/latest/meta-data/local-ipv4')
               .then(r => r.text()).then(data => document.getElementById('ip').textContent = data);
           
           let counter = 1;
           setInterval(() => {
               document.getElementById('time').textContent = new Date().toLocaleString();
               document.getElementById('counter').textContent = ++counter;
           }, 1000);
       </script>
   </body>
   </html>
   EOF
   ```

> **Ponto Didático**: Cada servidor tem visual diferente (azul vs laranja) para facilitar identificação durante os testes.

---

## Etapa 2: Criando Target Group

1. **EC2 > Target Groups > Create target group**
2. **Configurações básicas:**
   * **Target type**: Instances
   * **Target group name**: `tg-web-servers`
   * **Protocol**: HTTP
   * **Port**: 80
   * **VPC**: Selecione sua VPC

3. **Health checks:**
   * **Health check path**: `/`
   * **Health check interval**: 30 seconds
   * **Healthy threshold**: 2
   * **Unhealthy threshold**: 2

4. **Registrar targets:**
   * Selecione ambas as instâncias (`web-server-1` e `web-server-2`)
   * **Port**: 80
   * **Include as pending below**

5. **Create target group**

> **Ponto Didático**: Target Groups definem quais instâncias recebem tráfego e como verificar se estão saudáveis.

---

## Etapa 3: Criando Application Load Balancer

1. **EC2 > Load Balancers > Create load balancer**
2. **Escolha Application Load Balancer**
3. **Configurações básicas:**
   * **Load balancer name**: `alb-web-demo`
   * **Scheme**: Internet-facing
   * **IP address type**: IPv4

4. **Network mapping:**
   * **VPC**: Sua VPC
   * **Mappings**: Selecione as duas AZs onde estão suas instâncias
   * **Subnets**: Selecione subnets públicas

5. **Security groups:**
   * Crie novo ou use existente permitindo HTTP (80)

6. **Listeners and routing:**
   * **Protocol**: HTTP
   * **Port**: 80
   * **Default action**: Forward to `tg-web-servers`

7. **Create load balancer**

> **Ponto Didático**: ALB opera na camada 7 (aplicação) e pode rotear baseado em conteúdo HTTP.

---

## Etapa 4: Testando Distribuição de Carga

1. **Aguarde o ALB ficar "Active"** (alguns minutos)

2. **Teste via navegador:**
   * Acesse o DNS name do ALB
   * Recarregue a página várias vezes (F5)
   * **Observe**: Alternância entre Servidor 1 (azul) e Servidor 2 (laranja)

3. **Teste via curl:**
   ```bash
   # Execute várias vezes
   curl http://seu-alb-dns-name.elb.amazonaws.com
   
   # Ou em loop para ver distribuição
   for i in {1..10}; do
     curl -s http://seu-alb-dns-name.elb.amazonaws.com | grep "SERVIDOR WEB"
     sleep 1
   done
   ```

> **Ponto Didático**: Por padrão, o ALB distribui requisições de forma round-robin entre targets saudáveis.

---

## Etapa 5: Configurando Sticky Sessions

1. **EC2 > Target Groups > Selecione `tg-web-servers`**
2. **Aba "Attributes" > Edit**
3. **Stickiness:**
   * **Stickiness**: Enable
   * **Stickiness type**: Load balancer generated cookie
   * **Stickiness duration**: 300 seconds (5 minutos)
4. **Save changes**

---

## Etapa 6: Testando Sticky Sessions

1. **Teste no navegador:**
   * Acesse o ALB novamente
   * Recarregue várias vezes
   * **Observe**: Agora sempre vai para o mesmo servidor!

2. **Teste com curl (simulando cookie):**
   ```bash
   # Primeira requisição (sem cookie)
   curl -c cookies.txt http://seu-alb-dns-name.elb.amazonaws.com
   
   # Requisições seguintes (com cookie)
   for i in {1..5}; do
     curl -b cookies.txt -s http://seu-alb-dns-name.elb.amazonaws.com | grep "SERVIDOR WEB"
   done
   ```

3. **Para testar sem sticky:**
   * Abra navegador em modo privado/incógnito
   * Ou delete cookies do site
   * Observe que volta a alternar entre servidores

> **Ponto Didático**: Sticky sessions mantêm o usuário no mesmo servidor usando cookies. Útil para aplicações que mantêm estado na sessão.

---

## Etapa 7: Verificando Cross-Zone Load Balancing

1. **EC2 > Load Balancers > Selecione seu ALB**
2. **Aba "Attributes" > Edit**
3. **Cross-zone load balancing**: Enabled (padrão no ALB)

> **Ponto Didático**: Cross-zone permite que o ALB distribua tráfego uniformemente entre todas as instâncias, independente da AZ. No ALB é sempre habilitado.

---

## Etapa 8: Monitoramento

1. **CloudWatch Metrics:**
   * EC2 > Load Balancers > Monitoring
   * Observe métricas como:
     * Request Count
     * Target Response Time
     * Healthy Host Count

2. **Target Group Health:**
   * EC2 > Target Groups > Health checks
   * Verifique status "healthy" das instâncias

---

## Conceitos Importantes

### **Application Load Balancer (ALB)**:
- Opera na camada 7 (HTTP/HTTPS)
- Suporta roteamento baseado em path, host, headers
- Cross-zone load balancing sempre habilitado
- Suporte nativo a WebSockets e HTTP/2

### **Sticky Sessions**:
- Mantém usuário no mesmo servidor
- Baseado em cookies do load balancer
- Útil para aplicações stateful
- Pode causar distribuição desigual

### **Target Groups**:
- Agrupam targets (instâncias, IPs, Lambda)
- Definem health checks
- Podem ter múltiplos por ALB
- Suportam diferentes protocolos

### **Cross-Zone Load Balancing**:
- Distribui tráfego uniformemente entre AZs
- Sempre habilitado no ALB
- Melhora disponibilidade e distribuição

---

## Limpeza

* **Delete** o Load Balancer
* **Delete** o Target Group
* **Terminate** as instâncias EC2
* **Delete** Security Groups não utilizados

---

## Próximos Passos

* Explore roteamento baseado em path
* Configure HTTPS com certificados SSL
* Implemente Auto Scaling Groups
* Teste com Network Load Balancer (NLB)

---

## Recursos Adicionais

* [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
* [Target Groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)
* [Sticky Sessions](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/sticky-sessions.html)