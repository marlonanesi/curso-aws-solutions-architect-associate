## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 1.2: Dominando Spot Instances - Economia de até 90% em EC2

## 🎯 Objetivo

Explorar em profundidade as Spot Instances, uma das formas mais eficazes de reduzir custos na AWS, aprendendo a configurar, monitorar e implementar estratégias resilientes, tópico crucial para o exame SAA-C03. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Spot Instances oferecem economia significativa sobre instâncias Free Tier.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Spot Instances podem ser interrompidas com 2 minutos de aviso
> * Preços variam constantemente baseados na demanda
> * Não adequadas para aplicações críticas
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender Spot Instances

**Como funcionam as Spot Instances:**
- AWS tem capacidade ociosa disponível
- Você faz uma oferta pelo preço máximo que quer pagar
- Se sua oferta >= preço atual do Spot, sua instância roda
- Se o preço subir acima da sua oferta, a instância é interrompida

**Vantagens:**
- Economia de até 90% comparado ao On-Demand
- Mesma performance de instâncias On-Demand
- Integração com Auto Scaling Groups
- Ideal para workloads tolerantes a falhas

**Limitações:**
- Pode ser interrompida com 2 minutos de aviso
- Disponibilidade não garantida
- Não adequada para aplicações críticas
- Preços variam constantemente

**Casos de uso ideais:**
- Batch processing, Big Data (Hadoop, Spark)
- Machine Learning, Web Scraping
- Desenvolvimento e ambientes não-críticos

### 2. Verificar Preços Históricos

1. **Acesse Spot Pricing History**: EC2 > Spot Requests > Pricing History
2. **Configure a consulta**:
   - **Instance type**: t3.small
   - **Product**: Linux/UNIX
   - **Date range**: Last week

3. **Analise os padrões**:
   - Horários de pico vs baixa demanda
   - Diferenças entre zonas de disponibilidade
   - Tendências semanais

4. **Identifique oportunidades**:
   - Zonas com preços mais baixos
   - Horários com menor demanda
   - Tipos de instância com maior estabilidade

### 3. Criar Spot Instance

1. **Inicie o lançamento**: EC2 > Launch Instance
2. **Configure básico**:
   - **Nome**: `ec2-spot-demo`
   - **AMI**: Amazon Linux 2023
   - **Tipo de instância**: t3.small

3. **Configure Spot Request**:
   - Em "Advanced details", encontre "Purchasing option"
   - Marque "Request Spot instances"
   - **Maximum price**: Deixe como padrão (preço On-Demand atual)
   - **Request type**: One-time

4. **Configure aplicação resiliente** (User data):
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd aws-cli
   systemctl start httpd
   systemctl enable httpd
   
   # Cria página com informações da instância
   cat > /var/www/html/index.html << 'EOF'
   <html>
   <head><title>Spot Instance Demo</title></head>
   <body>
   <h1>🎯 Spot Instance Ativa!</h1>
   <p><strong>Instance ID:</strong> <span id="instance-id">Carregando...</span></p>
   <p><strong>Tipo:</strong> Spot Instance</p>
   <p><strong>Status:</strong> <span id="status">Rodando</span></p>
   
   <script>
   // Busca metadados da instância
   fetch('http://169.254.169.254/latest/meta-data/instance-id')
     .then(response => response.text())
     .then(data => document.getElementById('instance-id').textContent = data);
   
   // Verifica interrupção a cada 5 segundos
   setInterval(() => {
     fetch('http://169.254.169.254/latest/meta-data/spot/instance-action')
       .then(response => {
         if (response.status === 200) {
           document.getElementById('status').innerHTML = '<strong style="color:red">⚠️ INTERRUPÇÃO IMINENTE!</strong>';
         }
       })
       .catch(() => {
         document.getElementById('status').textContent = 'Rodando normalmente';
       });
   }, 5000);
   </script>
   </body>
   </html>
   EOF
   ```

5. **Configure rede e segurança**:
   - Security Group: Permitir HTTP (80) e SSH (22)
   - Subnet: Subnet pública
   - Auto-assign public IP: Enable

6. **Lance a instância**: Clique em "Launch Instance"

> 💡 O script monitora o endpoint de metadados que avisa sobre interrupções iminentes, permitindo cleanup graceful.

### 4. Monitorar Spot Instance

1. **Verifique o Spot Request**: EC2 > Spot Requests
2. **Observe os estados possíveis**:
   - `pending-evaluation`: Avaliando solicitação
   - `pending-fulfillment`: Aguardando capacidade
   - `fulfilled`: Instância rodando
   - `cancelled`: Cancelada (preço, capacidade, etc.)

3. **Teste a aplicação**:
   - Acesse via navegador: `http://ip-publico-da-instancia`
   - Observe as informações da instância
   - A página mostra se há interrupção iminente

### 5. Configurar Spot Fleet (Estratégia Avançada)

1. **Crie um Spot Fleet Request**: EC2 > Spot Requests > Request Spot Fleet
2. **Configure básico**:
   - **Fleet name**: `spot-fleet-demo`
   - **Target capacity**: 2 instances
   - **AMI**: Amazon Linux 2023

3. **Configure diversificação**:
   - **Instance types**: t3.micro, t3.small, t2.micro
   - **Subnets**: Múltiplas zonas de disponibilidade
   - **Allocation strategy**: Diversified
   - **Maximum price**: $0.05 per hour

> 💡 Spot Fleet automaticamente substitui instâncias interrompidas, mantendo a capacidade desejada através de diversificação.

### 6. Implementar Melhores Práticas

**Estratégias de Resiliência:**
- **Checkpointing**: Salve estado regularmente
- **Graceful shutdown**: Monitore interrupções via metadados
- **Diversificação**: Use múltiplos tipos e zonas
- **Backup automático**: Configure snapshots automáticos

**Monitoramento:**
- Configure CloudWatch alarms para interrupções
- Use EventBridge para automação
- Monitore tendências de preços

### 7. Limpeza de Recursos

1. **Termine Spot Instances**: EC2 > Instances > Terminate
2. **Cancele Spot Fleet**: EC2 > Spot Requests > Cancel
3. **Verifique recursos órfãos**:
   - Security Groups não utilizados
   - Volumes EBS desanexados

## ✅ Conclusão

Você dominou o uso de Spot Instances e estratégias de economia:

**✅ Checklist de Conquistas:**
- [ ] Conceito de Spot Instances compreendido
- [ ] Preços históricos analisados e padrões identificados
- [ ] Spot Instance criada com aplicação resiliente
- [ ] Monitoramento de interrupções implementado
- [ ] Spot Fleet configurado com diversificação
- [ ] Melhores práticas de resiliência aplicadas
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Spot Instances**: Economia de até 90% usando capacidade ociosa
* **Interrupções**: Aviso de 2 minutos via metadados
* **Diversificação**: Múltiplos tipos e zonas reduzem risco
* **Spot Fleet**: Gestão automática de capacidade
* **Resiliência**: Checkpointing e graceful shutdown
* **Casos de uso**: Batch processing, ML, desenvolvimento
