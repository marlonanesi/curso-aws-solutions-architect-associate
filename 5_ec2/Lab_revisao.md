## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#

# 🔧 Lab Revisão: EC2 - Limpeza e Gestão de Recursos

## � Objetivo

Revisar e limpar todos os recursos AWS criados durante os laboratórios de EC2, garantindo a não geração de custos desnecessários e aplicando boas práticas de gestão de recursos na nuvem. **Nível: Básico**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> A limpeza evita extrapolar os limites do Free Tier tradicional (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Recursos como EBS, Snapshots e EIPs geram custos mesmo quando não utilizados
> * AMIs mantêm snapshots associados que continuam sendo cobrados
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Verificar e Encerrar Instâncias EC2

**Caminho**: EC2 → Instâncias  
**Filtro**: Running  
**Ação**: Encerrar ou excluir instâncias dos labs (ex: `spot-hands-on`, `placement-group-demo`)  
**Custo**: EC2 cobra por hora quando está `running`

> ⚠️ Mesmo `stopped`, o volume EBS segue gerando custo

### 2. Limpar Volumes EBS Órfãos

**Caminho**: EC2 → Volumes  
**Filtro**: `available`  
**Ação**: Deletar volumes órfãos de labs de Resize, Snapshot, AMI  
**Custo**: Cobrança por GB/mês, mesmo se não estiver anexado

### 3. Remover Snapshots Desnecessários

**Caminho**: EC2 → Snapshots  
**Ação**: Deletar snapshots manuais ou criados via AMI  
**Custo**: Cobrança por GB armazenado

### 4. Deletar AMIs (Amazon Machine Images)

**Caminho**: EC2 → AMIs  
**Ação**: Deletar AMIs criadas nos labs  
**Custo**: Cada AMI está associada a um snapshot → gera custo contínuo

### 5. Limpar Security Groups (SGs)

**Caminho**: VPC → Security Groups  
**Ação**: Deletar SGs não associados (ex: `sg-hands-on`, `sg-docdb`)  
**Custo**: ❌ Sem custo direto, mas importante para manter ambiente limpo

### 6. Remover Placement Groups

**Caminho**: EC2 → Placement Groups  
**Ação**: Deletar os grupos `cluster-hpc-demo`, `spread-ha-demo`, `partition-distributed-demo`  
**Custo**: ❌ Sem custo, mas boa prática deletar

### 7. Liberar Elastic IPs (EIP)

**Caminho**: EC2 → Endereços IP Elásticos  
**Ação**: Liberar qualquer IP desassociado  
**Custo**: IP não associado a instância é cobrado por hora

### 8. Limpar Network Interfaces (ENIs)

**Caminho**: EC2 → Network Interfaces  
**Ação**: Deletar ENIs soltas ou de instâncias já removidas  
**Custo**: ❌ Sem custo direto, mas podem impedir limpeza de SGs

### 9. Remover EFS (File System)

**Caminho**: EFS → File Systems  
**Ação**: Deletar sistemas de arquivos criados no lab  
**Custo**: Cobrança por GB + throughput provisionado

### 10. Deletar DocumentDB

**Caminho**: RDS → DocumentDB → Clusters  
**Ação**: Deletar cluster criado  
**Custo**: Instância + armazenamento são cobrados por hora

## ✅ Conclusão

Você realizou uma limpeza completa dos recursos AWS criados nos laboratórios:

**✅ Checklist de Conquistas:**
- [ ] Instâncias EC2 encerradas ou removidas
- [ ] Volumes EBS órfãos deletados
- [ ] Snapshots desnecessários removidos
- [ ] AMIs criadas nos labs deletadas
- [ ] Security Groups não utilizados limpos
- [ ] Placement Groups removidos
- [ ] Elastic IPs desassociados liberados
- [ ] Network Interfaces órfãs deletadas
- [ ] Sistemas EFS removidos
- [ ] Clusters DocumentDB deletados

**🎓 Conceitos Reforçados:**
* **Gestão de custos**: Responsabilidade na nuvem para evitar cobranças desnecessárias
* **Recursos órfãos**: Identificação e remoção de recursos desvinculados
* **Boas práticas**: Manutenção regular e limpeza de ambiente
* **Monitoramento**: Verificação periódica de recursos ativos
* **Responsabilidade**: Diferencial no mercado para arquitetos e engenheiros AWS
