# 💰 Lab: CloudWatch Billing Alarm - Controle de Custos AWS

## 🎯 Objetivo
Criar um **alarme de billing no CloudWatch** que monitora os custos da conta AWS e envia notificação quando ultrapassar $20, evitando surpresas na fatura.

## 📚 O que você vai aprender:
- Habilitar billing alerts na conta AWS
- Criar alarmes de CloudWatch para custos
- Configurar notificações via SNS (email)
- Monitorar gastos em tempo real
- Implementar controle proativo de custos

---

## 🧠 Conceitos Fundamentais

### CloudWatch Billing Metrics
- **EstimatedCharges**: Custo estimado atual do mês
- **Atualização**: A cada 4 horas
- **Região**: Disponível apenas em **us-east-1** (N. Virginia)
- **Granularidade**: Por serviço ou total da conta

### SNS (Simple Notification Service)
- **Tópicos**: Canais de comunicação
- **Subscribers**: Destinatários (email, SMS, etc.)
- **Delivery**: Entrega confiável de mensagens

---

## 🔧 Pré-requisitos

**Permissões necessárias:**
- ✅ CloudWatch: CreateAlarm, PutMetricAlarm
- ✅ SNS: CreateTopic, Subscribe, Publish
- ✅ Billing: ViewBilling, ViewAccount

**Importante:**
- ⚠️ **Região**: Todas as configurações devem ser feitas em **us-east-1**
- ⚠️ **Root Account**: Billing alerts só funcionam na conta root

---

## 🛠️ Etapa 1: Habilitar Billing Alerts

### 1.1 Acessar Billing Preferences
1. **Console AWS** → Canto superior direito → **Account name**
2. **Account** → **Billing preferences**
3. Ou acesse diretamente: https://console.aws.amazon.com/billing/home#/preferences

### 1.2 Habilitar Alertas
1. **Billing preferences** → **Alert preferences**
2. ✅ Marcar: **"Receive CloudWatch billing alerts"**
3. **Save preferences**

> 💡 **Importante**: Pode levar até 24h para métricas aparecerem no CloudWatch

### 1.3 Verificar Região
1. **Mudar região** para **US East (N. Virginia) us-east-1**
2. **CloudWatch** → **Metrics** → **Billing**
3. Verificar se métricas estão disponíveis

---

## 📧 Etapa 2: Criar Tópico SNS

### 2.1 Criar Tópico
1. **Navegar**: SNS → Topics → Create topic
2. **Configurações**:
   - **Type**: Standard
   - **Name**: `billing-alerts`
   - **Display name**: `AWS Billing Alerts`
3. **Create topic**

### 2.2 Criar Subscription (Email)
1. **Tópico criado** → **Subscriptions** → **Create subscription**
2. **Configurações**:
   - **Protocol**: Email
   - **Endpoint**: seu-email@exemplo.com
3. **Create subscription**

### 2.3 Confirmar Subscription
1. **Verificar email** (pode ir para spam)
2. **Clicar** em "Confirm subscription"
3. **Status** deve mudar para "Confirmed"

### 2.4 Testar Notificação
1. **Tópico** → **Publish message**
2. **Subject**: `Teste de Notificação`
3. **Message**: `Este é um teste do sistema de alertas de billing`
4. **Publish message**
5. **Verificar** se recebeu o email

---

## ⚠️ Etapa 3: Criar Alarme de Billing

### 3.1 Acessar CloudWatch Alarms
1. **Navegar**: CloudWatch → Alarms → Create alarm
2. **Select metric**

### 3.2 Selecionar Métrica
1. **Billing** → **Total Estimated Charge**
2. **Currency**: USD
3. **Metric name**: EstimatedCharges
4. **Select metric**

### 3.3 Configurar Condições
1. **Metric and conditions**:
   - **Statistic**: Maximum
   - **Period**: 6 hours
   - **Threshold type**: Static
   - **Whenever EstimatedCharges is**: Greater
   - **than**: `20`

2. **Additional configuration**:
   - **Datapoints to alarm**: 1 out of 1
   - **Missing data treatment**: Treat missing data as not breaching

### 3.4 Configurar Ações
1. **Configure actions**:
   - **Alarm state trigger**: In alarm
   - **Send a notification to**: billing-alerts
   - **Email endpoints**: (já configurado)

2. **Add notification** (opcional):
   - **OK state**: Notificar quando voltar ao normal
   - **Select SNS topic**: billing-alerts

### 3.5 Configurar Nome e Descrição
1. **Add name and description**:
   - **Alarm name**: `Billing-Alert-20USD`
   - **Alarm description**: `Alerta quando custos ultrapassam $20`

2. **Preview and create** → **Create alarm**

---

## 📊 Etapa 4: Verificar e Testar

### 4.1 Verificar Status do Alarme
1. **CloudWatch** → **Alarms**
2. **Status** deve ser:
   - **OK**: Custos abaixo de $20
   - **INSUFFICIENT_DATA**: Aguardando dados (normal inicialmente)

### 4.2 Visualizar Métricas
1. **CloudWatch** → **Metrics** → **Billing**
2. **Total Estimated Charge** → **USD**
3. **Graphed metrics** → Visualizar gráfico de custos

### 4.3 Criar Dashboard (Opcional)
1. **CloudWatch** → **Dashboards** → **Create dashboard**
2. **Dashboard name**: `AWS-Billing-Monitor`
3. **Add widget** → **Line** → **Metrics**
4. **Billing** → **Total Estimated Charge** → **USD**
5. **Create widget** → **Save dashboard**

---

## 🧪 Etapa 5: Simular Cenários

### 5.1 Teste com Limite Baixo
Para testar rapidamente, crie um alarme com limite baixo:

1. **Criar novo alarme** com threshold `1` USD
2. **Aguardar** algumas horas
3. **Verificar** se recebe notificação

### 5.2 Monitorar Custos por Serviço
1. **Billing** → **By Service** → **EC2-Instance**
2. **Criar alarme** específico para EC2: `5` USD
3. **Repetir** para outros serviços importantes

### 5.3 Alarmes Múltiplos
```
Alarme 1: Total > $10  (Aviso)
Alarme 2: Total > $20  (Crítico)
Alarme 3: EC2 > $5     (Específico)
```

---

## ✅ Resultados Esperados

**🎯 Controle de Custos:**
- Notificação automática quando custos > $20
- Visibilidade em tempo real dos gastos
- Prevenção de surpresas na fatura

**🎯 Monitoramento:**
- Dashboard com métricas de billing
- Histórico de custos por período
- Alertas proativos

**🎯 Automação:**
- Notificações via email
- Possibilidade de ações automáticas
- Controle granular por serviço

---

## 🚨 Troubleshooting

### Problema: Métricas não aparecem
**Solução:**
- Verificar se está em us-east-1
- Aguardar até 24h após habilitar billing alerts
- Confirmar que há custos na conta

### Problema: Alarme sempre INSUFFICIENT_DATA
**Solução:**
- Aguardar dados suficientes (6-12h)
- Verificar se há atividade gerando custos
- Ajustar período do alarme

### Problema: Não recebe emails
**Solução:**
- Verificar spam/lixo eletrônico
- Confirmar subscription no SNS
- Testar tópico SNS manualmente

---

## 💡 Boas Práticas

**Limites Escalonados:**
```
$5   - Aviso inicial
$10  - Alerta moderado  
$20  - Alerta crítico
$50  - Emergência (parar recursos)
```

**Segmentação:**
- Alarmes por serviço (EC2, S3, RDS)
- Alarmes por ambiente (dev, prod)
- Alarmes por projeto/departamento

**Automação:**
- Lambda para parar recursos
- SNS para múltiplos canais (email, Slack)
- CloudFormation para replicar setup

---

## 🧹 Limpeza de Recursos

**Para remover:**
1. **CloudWatch Alarms** → Delete alarm
2. **SNS Subscriptions** → Unsubscribe
3. **SNS Topics** → Delete topic
4. **CloudWatch Dashboards** → Delete dashboard

> 💰 **Custo**: Este lab tem custo mínimo (~$0.10/mês por alarme)

---

## 🎓 Conceitos Aprendidos

**CloudWatch:**
- Billing metrics e alertas
- Criação de alarmes personalizados
- Dashboards para visualização

**SNS:**
- Tópicos e subscriptions
- Notificações multi-canal
- Integração com CloudWatch

**Billing:**
- Monitoramento proativo de custos
- Controle de gastos por serviço
- Prevenção de surpresas financeiras

**Automação:**
- Alertas baseados em métricas
- Ações automáticas via Lambda
- Governança de custos

---