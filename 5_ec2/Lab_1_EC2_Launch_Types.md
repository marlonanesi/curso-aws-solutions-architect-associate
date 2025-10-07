## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 1: Tipos de Lançamento EC2 - On-Demand vs Reserved vs Spot � Lab 1: Tipos de Lançamento EC2 - On-Demand vs Reserved vs Spot

## 🎯 Objetivo

Explorar os diferentes tipos de lançamento de instâncias EC2 e suas estratégias de otimização de custos, entendendo as diferenças entre On-Demand, Reserved e Spot Instances para aplicar no exame SAA-C03. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> EC2 t2.micro/t3.micro está no Free Tier com 750 horas/mês (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Instâncias cobram por hora quando estão `running`
> * Reserved Instances exigem compromisso de 1-3 anos
> * Spot Instances podem ser interrompidas a qualquer momento
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender os Tipos de Lançamento

**Conceitos Fundamentais:**

1. **On-Demand**: Pague pelo que usar, quando usar
2. **Reserved Instances**: Compromisso de 1-3 anos com desconto
3. **Spot Instances**: Use capacidade ociosa com até 90% de desconto
4. **Dedicated Hosts**: Hardware dedicado para compliance

**Analogias para facilitar o entendimento:**
- **On-Demand**: Como alugar um carro por hora - flexível, mas mais caro
- **Reserved**: Como assinar um plano de celular - compromisso com desconto
- **Spot**: Como pegar um voo em standby - muito barato, mas pode ser cancelado
- **Dedicated**: Como alugar uma casa inteira - controle total, preço premium

### 2. Criar Instância On-Demand

1. **Acesse o Console EC2**: Navegue até EC2 > Instances > Launch Instance
2. **Configure a instância**:
   - **Nome**: `ec2-ondemand-demo`
   - **AMI**: Amazon Linux 2023 (Free Tier eligible)
   - **Tipo de instância**: t3.micro
   - **Key pair**: Selecione ou crie um novo
   - **Network settings**: 
     - VPC: Sua VPC existente
     - Subnet: Uma subnet pública
     - Auto-assign public IP: Enable
   - **Security Group**: Crie um novo permitindo SSH (22) do seu IP

3. **Configurações avançadas** (opcional):
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd htop
   systemctl start httpd
   systemctl enable httpd
   echo "<h1>Instância On-Demand</h1><p>Criada em: $(date)</p>" > /var/www/html/index.html
   ```

4. **Lance a instância**: Clique em "Launch Instance"

> 💡 On-Demand é o modelo padrão - você paga pelo que usa, quando usa. Ideal para cargas de trabalho imprevisíveis, desenvolvimento e testes.

### 3. Verificar Custos On-Demand

1. **Acesse a calculadora AWS**: https://calculator.aws/
2. **Configure o cálculo**:
   - Service: Amazon EC2
   - Region: Sua região atual
   - Instance type: t3.micro
   - Usage: 24 hours/day, 30 days/month

3. **Anote o valor**: Aproximadamente $8-10/mês para t3.micro

### 4. Explorar Reserved Instances

1. **Acesse Reserved Instances**: No console EC2, navegue até "Reserved Instances" no menu lateral

**Tipos de Reserved Instances:**
- **Standard**: Até 75% de desconto, baixa flexibilidade
- **Convertible**: Até 54% de desconto, alta flexibilidade
- **Scheduled**: Para horários específicos

2. **Simule uma compra**:
   - Instance type: t3.micro
   - Platform: Linux/UNIX
   - Term: 1 year
   - Payment option: All Upfront

3. **Compare preços**:
   - On-Demand: ~$8.50/mês
   - Reserved (1 ano): ~$5.00/mês (economia de ~40%)
   - Reserved (3 anos): ~$3.50/mês (economia de ~60%)

4. **Cancele sem comprar**: Apenas demonstração

### 5. Analisar Estratégias de Otimização

**Matriz de Decisão por Tipo de Workload:**

| Tipo de Workload | Recomendação | Justificativa |
|------------------|--------------|---------------|
| **Desenvolvimento/Teste** | On-Demand | Uso intermitente, flexibilidade |
| **Produção Estável** | Reserved | Uso contínuo, economia significativa |
| **Batch Processing** | Spot | Tolerante a interrupções, máxima economia |
| **Aplicações Críticas** | On-Demand + Reserved | Combinação para flexibilidade e economia |

**Estratégias Híbridas:**
- **Baseline + Burst**: Reserved para carga base + On-Demand para picos
- **Exemplo**: 2x t3.medium Reserved + Auto Scaling On-Demand + Spot para batch

### 6. Usar Ferramentas de Monitoramento

1. **AWS Cost Explorer**: Analise padrões de uso e identifique otimizações
2. **AWS Trusted Advisor**: Recomendações automáticas de Reserved Instances
3. **AWS Compute Optimizer**: Recomendações de rightsizing

### 7. Limpeza de Recursos

1. **Termine a instância criada**:
   - EC2 > Instances
   - Selecione `ec2-ondemand-demo`
   - Instance State > Terminate Instance

2. **Verifique recursos órfãos**:
   - Security Groups não utilizados
   - Volumes EBS desanexados

## ✅ Conclusão

Você explorou os diferentes tipos de lançamento EC2 e estratégias de otimização:

**✅ Checklist de Conquistas:**
- [ ] Tipos de lançamento EC2 compreendidos (On-Demand, Reserved, Spot, Dedicated)
- [ ] Instância On-Demand criada e configurada
- [ ] Custos calculados usando calculadora AWS
- [ ] Reserved Instances exploradas e simuladas
- [ ] Estratégias de otimização analisadas
- [ ] Ferramentas de monitoramento identificadas
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **On-Demand**: Flexível, sem compromisso, mais caro
* **Reserved**: Desconto por compromisso de 1-3 anos
* **Spot**: Até 90% de desconto, pode ser interrompido
* **Estratégias híbridas**: Combinação de tipos para otimização
* **Rightsizing**: Escolher o tamanho correto de instância
* **Ferramentas**: Cost Explorer, Trusted Advisor, Compute Optimizer

