## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 2: Sticky Sessions e Monitoramento de Load Balancer

## 🎯 Objetivo

Configurar sticky sessions no Target Group para manter afinidade de sessão, compreender o comportamento de cookies do ALB, analisar métricas de monitoramento no CloudWatch e implementar práticas de limpeza de recursos. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Este lab usa recursos do Lab 1. ALB: 750 horas/mês incluídas no Free Tier (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Sticky sessions podem concentrar carga em uma instância específica
> * CloudWatch métricas são gratuitas para ALB, mas dashboards customizados podem gerar custos
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Compreender Conceitos de Sticky Sessions

**O que são Sticky Sessions?**

Sticky Sessions (afinidade de sessão) garantem que todas as requisições de um usuário específico sejam direcionadas sempre para a mesma instância. É útil quando a aplicação mantém estado local (sessões, cache, dados temporários).

**Tipos de stickiness:**
- **Load balancer generated cookie**: ALB gera cookie automaticamente
- **Application generated cookie**: Aplicação controla o cookie
- **Duration-based**: Cookie expira após tempo determinado

**Quando usar:**
- ✅ Aplicações stateful que mantêm dados de sessão localmente
- ✅ Shopping carts em aplicações de e-commerce
- ✅ Sessões de login complexas
- ❌ Aplicações stateless (melhor usar shared storage)

### 2. Configurar Sticky Sessions no Target Group

**Pré-requisito**: Complete o Lab 1 (ALB com 2 instâncias funcionando)

1. **Acesse Target Groups**: Navigate to **EC2 > Target Groups**

2. **Selecione o Target Group**: Click em `tg-web-servers`

3. **Configure Stickiness**:
   - Click na aba **Attributes**
   - Click **Edit**
   - **Stickiness**: Enable
   - **Stickiness type**: Load balancer generated cookie
   - **Stickiness duration**: 300 seconds (5 minutos)
   - **Save changes**

4. **Verifique configuração**:
   - Na aba Attributes, confirme que `Stickiness` está habilitado
   - Note o nome do cookie: `AWSALB`

### 3. Testar Comportamento com Sticky Sessions

1. **Teste via navegador web**:
   - Acesse o DNS do ALB no navegador
   - Recarregue a página várias vezes (F5)
   - **Resultado esperado**: Sempre o mesmo servidor (azul OU laranja)
   - Abra ferramentas de desenvolvedor (F12) > Application > Cookies
   - Observe o cookie `AWSALB` criado pelo load balancer

2. **Teste com novo navegador/sessão**:
   - Abra modo incógnito/privado
   - Acesse o mesmo URL
   - **Resultado esperado**: Pode ir para servidor diferente
   - Mas dentro da mesma sessão incógnito, sempre mesmo servidor

3. **Teste via linha de comando**:
   ```bash
   # Primeira requisição - salva cookies
   curl -c cookies.txt http://dns-name-do-alb
   
   # Requisições subsequentes usando o cookie
   echo "=== Testando sticky sessions ==="
   for i in {1..5}; do
     echo "Requisição $i:"
     curl -b cookies.txt -s http://dns-name-do-alb | grep -E "(SERVIDOR 1|SERVIDOR 2)"
     echo "---"
   done
   ```

4. **Teste sem cookies (comportamento normal)**:
   ```bash
   # Requisições sem cookies - deve alternar
   echo "=== Testando sem cookies (round-robin) ==="
   for i in {1..5}; do
     echo "Requisição $i:"
     curl -s http://dns-name-do-alb | grep -E "(SERVIDOR 1|SERVIDOR 2)"
     echo "---"
   done
   ```

### 4. Analisar Impacto das Sticky Sessions

1. **Monitore distribuição de carga**:
   - Acesse **EC2 > Target Groups > tg-web-servers**
   - Click na aba **Targets**
   - Observe que com sticky sessions, carga pode ficar desbalanceada

2. **Simule múltiplos usuários**:
   ```bash
   # Simular diferentes sessões de usuários
   for session in {1..3}; do
     echo "=== Sessão de usuário $session ==="
     curl -c "session_${session}.txt" http://dns-name-do-alb | grep -E "(SERVIDOR 1|SERVIDOR 2)"
     
     # Múltiplas requisições da mesma sessão
     for req in {1..3}; do
       curl -b "session_${session}.txt" -s http://dns-name-do-alb | grep -E "(SERVIDOR 1|SERVIDOR 2)"
     done
     echo "---"
   done
   ```

### 5. Monitorar Métricas no CloudWatch

1. **Acesse métricas do ALB**:
   - Navigate to **CloudWatch > Metrics > All metrics**
   - **AWS/ApplicationELB**
   - Select metrics por LoadBalancer
   - Escolha `alb-web-demo`

2. **Métricas importantes para observar**:
   - **RequestCount**: Total de requisições
   - **TargetResponseTime**: Tempo de resposta das instâncias
   - **HTTPCode_Target_2XX_Count**: Respostas de sucesso
   - **HealthyHostCount**: Número de instâncias saudáveis
   - **UnHealthyHostCount**: Número de instâncias com problemas

3. **Crie dashboard personalizado**:
   - **CloudWatch > Dashboards > Create dashboard**
   - **Dashboard name**: `ALB-Monitoring`
   - Add widgets para as métricas principais
   - **Widget type**: Line graph
   - **Metrics**: Selecione as métricas do ALB
   - **Save dashboard**

4. **Configure alarmes** (opcional):
   ```bash
   # Exemplo de alarme para resposta lenta
   aws cloudwatch put-metric-alarm \
     --alarm-name "ALB-High-Response-Time" \
     --alarm-description "ALB response time is high" \
     --metric-name TargetResponseTime \
     --namespace AWS/ApplicationELB \
     --statistic Average \
     --period 300 \
     --threshold 1.0 \
     --comparison-operator GreaterThanThreshold \
     --evaluation-periods 2
   ```

### 6. Testar Comportamento de Falha com Sticky Sessions

1. **Pare uma instância que está recebendo tráfego sticky**:
   - Identifique qual servidor está respondendo para sua sessão
   - Se for Servidor 1, conecte-se via SSH:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-servidor-1
   sudo systemctl stop httpd
   ```

2. **Observe o comportamento**:
   - Recarregue página no navegador com cookie ativo
   - **Resultado esperado**: ALB detecta falha e redireciona para instância saudável
   - Novo cookie pode ser criado para nova instância

3. **Monitore no Target Group**:
   - **EC2 > Target Groups > tg-web-servers > Targets**
   - Observe status mudando para `unhealthy`
   - Tempo para detectar falha: ~1-2 minutos

4. **Restaure o serviço**:
   ```bash
   sudo systemctl start httpd
   ```

### 7. Comparar Performance com e sem Sticky Sessions

1. **Desabilite sticky sessions temporariamente**:
   - **Target Groups > tg-web-servers > Attributes > Edit**
   - **Stickiness**: Disable
   - **Save changes**

2. **Execute teste de carga simples**:
   ```bash
   # Teste sem sticky sessions
   echo "=== Teste SEM sticky sessions ==="
   time for i in {1..20}; do
     curl -s http://dns-name-do-alb > /dev/null
   done
   ```

3. **Reabilite sticky sessions**:
   - **Stickiness**: Enable
   - **Stickiness duration**: 300 seconds

4. **Repita teste de carga**:
   ```bash
   # Teste COM sticky sessions
   echo "=== Teste COM sticky sessions ==="
   curl -c test_cookies.txt http://dns-name-do-alb > /dev/null
   time for i in {1..20}; do
     curl -b test_cookies.txt -s http://dns-name-do-alb > /dev/null
   done
   ```

### 8. Analisar Logs de Acesso (Configuração Opcional)

1. **Configure access logs no S3**:
   - **EC2 > Load Balancers > alb-web-demo**
   - **Attributes > Edit > Access logs**
   - **Enable**: Yes
   - **S3 location**: Especifique bucket S3
   - **Save changes**

2. **Analise logs para padrões de sticky sessions**:
   - Logs mostrarão qual target recebeu cada requisição
   - Procure por padrões de IP → mesma instância

### 9. Implementar Limpeza Responsável de Recursos

1. **Desabilite sticky sessions antes de deletar**:
   - **Target Groups > tg-web-servers > Attributes**
   - **Stickiness**: Disable
   - **Save changes**

2. **Delete Load Balancer**:
   - **EC2 > Load Balancers**
   - Selecione `alb-web-demo`
   - **Actions > Delete**
   - Confirme digitando "confirm"

3. **Delete Target Group**:
   - **EC2 > Target Groups**
   - Selecione `tg-web-servers`
   - **Actions > Delete**

4. **Termine instâncias EC2**:
   - **EC2 > Instances**
   - Selecione `web-server-1` e `web-server-2`
   - **Instance State > Terminate Instance**

5. **Cleanup adicional**:
   - Delete security groups criados (`sg-alb-web`, `sg-web-servers`)
   - Delete dashboard CloudWatch se criado
   - Delete alarmes CloudWatch se criados
   - Limpe arquivos de cookies locais

6. **Verifique limpeza completa**:
   ```bash
   # Limpe arquivos de teste locais
   rm -f cookies.txt session_*.txt test_cookies.txt
   ```

## ✅ Conclusão

Você dominou o uso de sticky sessions e monitoramento de load balancers:

**✅ Checklist de Conquistas:**
- [ ] Conceitos de sticky sessions compreendidos
- [ ] Sticky sessions configuradas no Target Group
- [ ] Comportamento de afinidade de sessão testado
- [ ] Diferença entre requisições com e sem cookies demonstrada
- [ ] Múltiplos cenários de teste executados
- [ ] Métricas CloudWatch analisadas
- [ ] Dashboard de monitoramento criado
- [ ] Comportamento de falha com sticky sessions testado
- [ ] Performance comparada com e sem sticky sessions
- [ ] Limpeza responsável de recursos executada

**🎓 Conceitos Reforçados:**
* **Session affinity**: Manter usuários na mesma instância
* **Load balancer cookies**: Como ALB gerencia sticky sessions
* **Stateful vs stateless**: Quando usar cada abordagem
* **CloudWatch monitoring**: Métricas essenciais para load balancers
* **Fault tolerance**: Como sticky sessions afetam recuperação de falhas
* **Resource cleanup**: Práticas responsáveis de gerenciamento de custos
