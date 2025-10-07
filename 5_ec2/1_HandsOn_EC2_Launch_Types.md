# 🚀 Lab: Explorando os Tipos de Lançamento EC2, Spot Instances e Placement Groups

## Visão Geral

Neste laboratório hands-on, vamos explorar os diferentes tipos de lançamento de instâncias EC2, configurar Spot Instances para economia de custos e implementar Placement Groups para otimizar performance e disponibilidade. Este é um dos tópicos mais importantes para o exame SAA-C03, pois aborda estratégias de otimização de custos e performance.

**Tempo estimado**: 60-75 minutos  
**Nível de dificuldade**: Intermediário

## Objetivos de Aprendizado

Ao concluir este laboratório, você será capaz de:

1. Entender e configurar diferentes tipos de lançamento EC2 (On-Demand, Reserved, Spot)
2. Criar e gerenciar Spot Instances com estratégias de economia
3. Implementar Placement Groups para diferentes cenários de uso
4. Comparar custos e performance entre diferentes opções
5. Aplicar melhores práticas para otimização de custos e performance

## Pré-requisitos

- Uma conta AWS com permissões para criar instâncias EC2
- VPC com subnets públicas e privadas já configuradas
- Conhecimento básico do console EC2
- Calculadora AWS para comparação de custos

## Parte 1: Explorando Tipos de Lançamento EC2 💰

### 1.1 Criando uma Instância On-Demand (Padrão)

1. **Acesse o Console EC2**:
   - Navegue até EC2 > Instances > Launch Instance

2. **Configure a instância base**:
   - **Nome**: `ec2-ondemand-demo`
   - **AMI**: Amazon Linux 2023 (Free Tier eligible)
   - **Tipo de instância**: t3.micro
   - **Key pair**: Selecione ou crie um novo
   - **Network settings**: 
     - VPC: Sua VPC existente
     - Subnet: Uma subnet pública
     - Auto-assign public IP: Enable
   - **Security Group**: Crie um novo permitindo SSH (22) do seu IP

3. **Configurações avançadas**:
   - Mantenha todas as configurações padrão
   - **PONTO DIDÁTICO**: Explique que esta é uma instância On-Demand - paga por hora/segundo, sem compromisso, disponível imediatamente

4. **Lance a instância**: Clique em "Launch Instance"

> **PONTO DIDÁTICO**: On-Demand é o modelo padrão - você paga pelo que usa, quando usa. É como alugar um carro por hora - flexível, mas mais caro para uso contínuo.

### 1.2 Simulando Reserved Instances (Demonstração)

1. **Acesse Reserved Instances**:
   - No console EC2, navegue até "Reserved Instances" no menu lateral

2. **Explore as opções**:
   - Clique em "Purchase Reserved Instances"
   - **PONTO DIDÁTICO**: Mostre as diferentes opções:
     - **Standard**: Maior desconto, menos flexibilidade
     - **Convertible**: Menor desconto, mais flexibilidade para mudanças
     - **Scheduled**: Para cargas de trabalho previsíveis

3. **Compare preços**:
   - Selecione t3.micro, 1 ano, All Upfront
   - **PONTO DIDÁTICO**: Mostre a economia de até 75% comparado ao On-Demand
   - Cancele sem comprar (apenas demonstração)

> **PONTO DIDÁTICO**: Reserved Instances são como assinar um plano anual de celular - você se compromete com um período e ganha desconto significativo.

## Parte 2: Configurando Spot Instances 💸

### 2.1 Criando uma Spot Instance

1. **Inicie o lançamento**:
   - EC2 > Launch Instance
   - **Nome**: `ec2-spot-demo`
   - **AMI**: Amazon Linux 2023
   - **Tipo de instância**: t3.small (para demonstrar melhor)

2. **Configure Spot Request**:
   - Em "Advanced details", encontre "Purchasing option"
   - Marque "Request Spot instances"
   - **Maximum price**: Deixe como padrão (preço On-Demand atual)
   - **Request type**: One-time
   - **PONTO DIDÁTICO**: Explique que Spot pode ser até 90% mais barato que On-Demand

3. **Configure o resto**:
   - Mesmas configurações de rede da instância anterior
   - **User data** (opcional):
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd
   systemctl start httpd
   systemctl enable httpd
   echo "<h1>Spot Instance Demo - $(hostname)</h1>" > /var/www/html/index.html
   ```

4. **Lance a instância**: Clique em "Launch Instance"

> **PONTO DIDÁTICO**: Spot Instances usam capacidade ociosa da AWS. É como pegar um voo em standby - muito mais barato, mas pode ser cancelado se alguém pagar o preço cheio.

### 2.2 Monitorando Spot Instances

1. **Verifique o status**:
   - Vá para EC2 > Spot Requests
   - Observe o status da sua solicitação
   - **PONTO DIDÁTICO**: Explique os diferentes status (pending, active, cancelled)

2. **Verifique preços históricos**:
   - EC2 > Spot Requests > Pricing History
   - Selecione t3.small e sua região
   - **PONTO DIDÁTICO**: Mostre como os preços variam ao longo do tempo

## Parte 3: Implementando Placement Groups 🏗️

### 3.1 Criando um Cluster Placement Group

1. **Crie o Placement Group**:
   - EC2 > Placement Groups > Create placement group
   - **Nome**: `cluster-pg-demo`
   - **Strategy**: Cluster
   - **PONTO DIDÁTICO**: Cluster agrupa instâncias em uma única AZ para baixa latência

2. **Lance instâncias no Placement Group**:
   - Launch Instance
   - **Nome**: `ec2-cluster-1`
   - **AMI**: Amazon Linux 2023
   - **Tipo**: c5n.large (otimizado para rede)
   - **Advanced details** > **Placement group**: Selecione `cluster-pg-demo`
   - Configure rede e segurança normalmente
   - Lance a instância

3. **Lance uma segunda instância**:
   - Repita o processo
   - **Nome**: `ec2-cluster-2`
   - Mesmo placement group: `cluster-pg-demo`

> **PONTO DIDÁTICO**: Cluster Placement Groups são ideais para aplicações HPC (High Performance Computing) que precisam de comunicação rápida entre instâncias, como processamento científico ou big data.

### 3.2 Criando um Spread Placement Group

1. **Crie o Placement Group**:
   - Create placement group
   - **Nome**: `spread-pg-demo`
   - **Strategy**: Spread
   - **PONTO DIDÁTICO**: Spread distribui instâncias em hardware diferente para máxima disponibilidade

2. **Lance instâncias no Spread Group**:
   - Launch Instance
   - **Nome**: `ec2-spread-1`
   - **AMI**: Amazon Linux 2023
   - **Tipo**: t3.micro
   - **Placement group**: `spread-pg-demo`
   - Lance a instância

3. **Lance mais instâncias**:
   - Repita para `ec2-spread-2` e `ec2-spread-3`
   - **PONTO DIDÁTICO**: Máximo de 7 instâncias por AZ em Spread Groups

> **PONTO DIDÁTICO**: Spread Placement Groups são ideais para aplicações críticas que precisam de máxima disponibilidade, como bancos de dados distribuídos ou aplicações que não podem ter pontos únicos de falha.

### 3.3 Criando um Partition Placement Group

1. **Crie o Placement Group**:
   - Create placement group
   - **Nome**: `partition-pg-demo`
   - **Strategy**: Partition
   - **Number of partitions**: 3
   - **PONTO DIDÁTICO**: Partition combina benefícios de Cluster e Spread

2. **Lance instâncias em diferentes partições**:
   - Launch Instance
   - **Nome**: `ec2-partition-1`
   - **Placement group**: `partition-pg-demo`
   - **Partition**: 1
   - Lance mais instâncias em partições diferentes

> **PONTO DIDÁTICO**: Partition Placement Groups são ideais para aplicações distribuídas como Hadoop, Cassandra, Kafka - onde você quer grupos de instâncias próximas, mas os grupos separados entre si.

## Parte 4: Testando Performance e Disponibilidade 📊

### 4.1 Teste de Latência (Cluster vs Normal)

1. **Conecte-se às instâncias do cluster**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-instancia-cluster-1
   ```

2. **Instale ferramentas de teste**:
   ```bash
   sudo yum update -y
   sudo yum install -y iperf3
   ```

3. **Execute teste de latência**:
   ```bash
   # Na primeira instância (servidor)
   iperf3 -s
   
   # Na segunda instância (cliente)
   iperf3 -c IP_PRIMEIRA_INSTANCIA -t 10
   ```

4. **Compare com instâncias normais**:
   - Repita o teste entre instâncias que não estão em placement group
   - **PONTO DIDÁTICO**: Mostre a diferença de latência e throughput

### 4.2 Simulação de Falha (Spread vs Normal)

1. **Verifique distribuição das instâncias Spread**:
   - EC2 > Instances
   - Observe as diferentes zonas de disponibilidade
   - **PONTO DIDÁTICO**: Instâncias Spread estão em hardware diferente

2. **Simule cenário de falha**:
   - Explique como uma falha de hardware afetaria instâncias normais vs Spread
   - **PONTO DIDÁTICO**: Spread oferece melhor isolamento de falhas

## Parte 5: Análise de Custos e Casos de Uso 💡

### 5.1 Comparação de Custos

1. **Acesse a calculadora AWS**:
   - Abra https://calculator.aws/
   - Compare custos para t3.medium por 1 ano:
     - On-Demand: $X/mês
     - Reserved (1 ano): $Y/mês (economia de ~40%)
     - Spot (média): $Z/mês (economia de ~70%)

2. **Cenários de uso**:
   - **PONTO DIDÁTICO**: Explique quando usar cada tipo:
     - On-Demand: Cargas imprevisíveis, desenvolvimento, testes
     - Reserved: Cargas estáveis, produção, aplicações críticas
     - Spot: Processamento batch, análise de dados, cargas tolerantes a falhas

### 5.2 Casos de Uso dos Placement Groups

| Tipo | Caso de Uso | Exemplo |
|------|-------------|---------|
| Cluster | Baixa latência, alto throughput | HPC, machine learning distribuído |
| Spread | Máxima disponibilidade | Bancos de dados críticos, aplicações HA |
| Partition | Aplicações distribuídas | Hadoop, Cassandra, Kafka |

## Parte 6: Limpeza de Recursos 🧹

### 6.1 Terminando Instâncias

1. **Termine todas as instâncias criadas**:
   - EC2 > Instances
   - Selecione todas as instâncias do laboratório
   - Instance State > Terminate Instance

2. **Cancele Spot Requests ativos**:
   - EC2 > Spot Requests
   - Selecione requests ativos
   - Actions > Cancel spot request

3. **Delete Placement Groups**:
   - EC2 > Placement Groups
   - Selecione os grupos criados
   - Actions > Delete placement group

## Conceitos Importantes para o Exame SAA-C03

### Tipos de Instância:
- **On-Demand**: Flexível, sem compromisso, mais caro
- **Reserved**: Desconto por compromisso de 1-3 anos
- **Spot**: Até 90% de desconto, pode ser interrompido
- **Dedicated Hosts**: Hardware dedicado para compliance

### Placement Groups:
- **Cluster**: Baixa latência, mesma AZ, até 10 Gbps
- **Spread**: Máxima disponibilidade, hardware separado, máx 7 por AZ
- **Partition**: Grupos isolados, até 7 partições por AZ

### Estratégias de Otimização:
- **Custo**: Spot para batch, Reserved para produção estável
- **Performance**: Cluster para HPC, tipos otimizados (C5, R5, etc.)
- **Disponibilidade**: Spread, múltiplas AZs, Auto Scaling

## Próximos Passos

- Explore instâncias otimizadas (C5, R5, M5, etc.)
- Implemente Auto Scaling Groups
- Configure Load Balancers
- Estude padrões de arquitetura para diferentes workloads

## Recursos Adicionais

- [Guia de tipos de instância EC2](https://aws.amazon.com/ec2/instance-types/)
- [Documentação Spot Instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)
- [Placement Groups Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html)
- [Calculadora de preços AWS](https://calculator.aws/)