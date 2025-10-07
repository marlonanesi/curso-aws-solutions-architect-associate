## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 1.3: Placement Groups - Otimizando Performance e Disponibilidade

## 🎯 Objetivo

Explorar os Placement Groups do EC2, uma funcionalidade avançada para otimizar performance de rede e disponibilidade de aplicações, aprendendo quando e como usar cada tipo para diferentes cenários no exame SAA-C03. **Nível: Avançado**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Placement Groups não geram custo adicional, apenas as instâncias EC2 utilizadas.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Instâncias em Cluster Placement Groups devem usar tipos compatíveis
> * Spread Placement Groups têm limite de 7 instâncias por AZ
> * Recomendado usar instâncias do mesmo tipo e tamanho
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender Placement Groups

**Conceito Fundamental:**
Placement Groups controlam como as instâncias EC2 são fisicamente posicionadas no hardware da AWS.

**Tipos de Placement Groups:**

1. **Cluster Placement Group**:
   - **Objetivo**: Máxima performance de rede
   - **Localização**: Mesma zona de disponibilidade, hardware próximo
   - **Benefício**: Baixa latência (10 Gbps entre instâncias)
   - **Caso de uso**: HPC, machine learning distribuído

2. **Spread Placement Group**:
   - **Objetivo**: Máxima disponibilidade
   - **Localização**: Hardware separado, múltiplas AZs
   - **Benefício**: Isolamento de falhas
   - **Caso de uso**: Aplicações críticas, bancos de dados

3. **Partition Placement Group**:
   - **Objetivo**: Balanceamento entre performance e disponibilidade
   - **Localização**: Grupos isolados dentro da mesma AZ
   - **Benefício**: Controle granular sobre distribuição
   - **Caso de uso**: Big Data (Hadoop, Cassandra, Kafka)

### 2. Criar Cluster Placement Group

1. **Acesse Placement Groups**: EC2 > Network & Security > Placement Groups
2. **Crie novo grupo**:
   - **Name**: `cluster-hpc-demo`
   - **Strategy**: Cluster
   - **Tags**: Environment = Lab

3. **Características do Cluster**:
   - Mesma AZ obrigatoriamente
   - Baixa latência entre instâncias
   - Largura de banda de 10 Gbps
   - Ideal para aplicações que precisam de comunicação intensiva

### 3. Criar Spread Placement Group

1. **Crie novo grupo**:
   - **Name**: `spread-ha-demo`
   - **Strategy**: Spread
   - **Tags**: Environment = Lab

2. **Características do Spread**:
   - Máximo 7 instâncias por AZ
   - Hardware diferente para cada instância
   - Reduz risco de falhas correlacionadas
   - Pode usar múltiplas AZs

### 4. Criar Partition Placement Group

1. **Crie novo grupo**:
   - **Name**: `partition-distributed-demo`
   - **Strategy**: Partition
   - **Number of partitions**: 3
   - **Tags**: Environment = Lab

2. **Características do Partition**:
   - Até 7 partições por AZ
   - Cada partição tem racks separados
   - Controle sobre distribuição de instâncias
   - Ideal para sistemas distribuídos

### 5. Testar Cluster Placement Group

1. **Lance instâncias no Cluster**:
   - **AMI**: Amazon Linux 2023
   - **Instance type**: c5n.large (otimizado para rede)
   - **Quantidade**: 2 instâncias
   - **Placement group**: cluster-hpc-demo
   - **Advanced details** > **Placement group name**: cluster-hpc-demo

2. **Configure para teste de performance**:
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y iperf3 htop
   systemctl start iperf3
   systemctl enable iperf3
   
   # Inicia servidor iperf3 na primeira instância
   nohup iperf3 -s -p 5001 &
   ```

3. **Execute teste de largura de banda**:
   ```bash
   # Na segunda instância, teste conectividade com a primeira
   iperf3 -c [IP-PRIMEIRA-INSTANCIA] -p 5001 -t 30
   ```

### 6. Testar Spread Placement Group

1. **Lance instâncias no Spread**:
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t3.micro
   - **Quantidade**: 3 instâncias
   - **Placement group**: spread-ha-demo
   - **Multi-AZ**: Distribua em diferentes AZs

2. **Verifique distribuição**:
   - EC2 > Instances
   - Confirme que instâncias estão em AZs diferentes
   - Observe que cada uma está em hardware separado

### 7. Testar Partition Placement Group

1. **Lance instâncias no Partition**:
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t3.micro
   - **Quantidade**: 6 instâncias
   - **Placement group**: partition-distributed-demo

2. **Distribua entre partições**:
   - 2 instâncias na Partition 1
   - 2 instâncias na Partition 2
   - 2 instâncias na Partition 3

3. **Verifique informações de partição**:
   ```bash
   # Execute em cada instância para ver a partição
   curl http://169.254.169.254/latest/meta-data/placement/partition-number
   ```

### 8. Análise Comparativa

**Teste de Latência:**
- Cluster: < 1ms entre instâncias
- Spread: 1-3ms (dependendo da AZ)
- Partition: 1-2ms dentro da mesma partição

**Disponibilidade:**
- Cluster: Risco de falha correlacionada (mesmo rack)
- Spread: Máxima proteção contra falhas
- Partition: Proteção moderada (grupos isolados)

**Performance:**
- Cluster: Máxima (10 Gbps)
- Spread: Padrão EC2
- Partition: Alta dentro da partição

### 9. Casos de Uso Práticos

**Cluster Placement Group:**
- Simulações científicas (HPC)
- Machine Learning distribuído
- Aplicações de trading de alta frequência
- Rendering de vídeo

**Spread Placement Group:**
- Bancos de dados críticos
- Servidores DNS
- Aplicações de monitoramento
- Sistemas de backup

**Partition Placement Group:**
- Hadoop clusters
- Apache Kafka
- Cassandra/NoSQL distribuído
- Sistemas de processamento distribuído

### 10. Limpeza de Recursos

1. **Termine todas as instâncias**: EC2 > Instances > Terminate
2. **Delete Placement Groups**:
   - EC2 > Placement Groups
   - Selecione cada grupo criado
   - Actions > Delete

3. **Verifique recursos órfãos**:
   - Security Groups não utilizados
   - Volumes EBS desanexados

## ✅ Conclusão

Você dominou o uso de Placement Groups para otimização de performance e disponibilidade:

**✅ Checklist de Conquistas:**
- [ ] Conceitos de Placement Groups compreendidos
- [ ] Cluster Placement Group criado e testado
- [ ] Spread Placement Group configurado
- [ ] Partition Placement Group implementado
- [ ] Testes de performance executados
- [ ] Análise comparativa realizada
- [ ] Casos de uso práticos identificados
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Cluster**: Máxima performance de rede, mesma AZ
* **Spread**: Máxima disponibilidade, hardware separado
* **Partition**: Balanceamento performance/disponibilidade
* **Casos de uso**: HPC, bancos críticos, sistemas distribuídos
* **Limitações**: 7 instâncias por AZ (Spread), tipos compatíveis (Cluster)
* **Performance**: Cluster (10 Gbps), Spread (padrão), Partition (alta interna)
