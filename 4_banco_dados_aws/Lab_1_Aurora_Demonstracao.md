## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 1: Demonstração do Amazon Aurora - Recursos Avançados

## 🎯 Objetivo

Criar e explorar um cluster Amazon Aurora para visualizar seus recursos mais cobrados no exame SAA-C03, como endpoints diferenciados, failover automático, performance insights e opções como Aurora Serverless e Global Database. **Nível: Avançado**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> ⚠️ **Aurora NÃO está incluído no Free Tier** - gera cobranças por instância e armazenamento.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Instâncias db.t3.medium geram cobrança por hora
> * Armazenamento Aurora é cobrado por GB
> * Performance Insights pode gerar custos adicionais
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Criar Cluster Amazon Aurora MySQL

1. Acesse **RDS** > **Databases** > **Create database**
2. Escolha: `Standard create`
3. Engine: `Amazon Aurora`
4. Edition: `Aurora MySQL-Compatible Edition`, versão 3.x
5. Model: `Production`
6. Identificador do cluster: `aurora-demo-cluster`
7. Usuário: `admin` / Senha: `Aurora2025!`
8. Instância: `db.t3.medium`
9. Disponibilidade: `Create Aurora replica em AZ diferente`
10. Rede: use VPC e subnets já criadas
11. Public access: `No`
12. Autenticação: `Password`
13. Backup: `7 dias`, `Encryption: Yes`, `Performance Insights: Yes`
14. Crie o banco

### 2. Explorar Endpoints Aurora

1. Acesse detalhes do cluster criado
2. Veja os endpoints:
   * `Cluster endpoint` (escrita)
   * `Reader endpoint` (leitura balanceada)
3. Use como analogia:
   * Escrita: caixa central dos pedidos
   * Leitura: várias filiais com acesso à consulta dos pedidos

### 3. Adicionar Réplica de Leitura

1. No cluster, clique em **Add reader**
2. Nome: `aurora-demo-reader-2`
3. Instância: mesma configuração primária (db.t3.medium)
4. AZ: escolha uma diferente
5. Crie e aguarde
6. Explique que até 15 réplicas podem ser criadas, com latência < 20ms

### 4. Simular Failover

1. Selecione a instância writer
2. Clique **Actions > Failover**
3. Confirme
4. Observe o comportamento:
   * Endpoint do cluster é redirecionado automaticamente
   * A nova instância primária assume
   * Sem interrupção para aplicações

### 5. Explorar Recursos Avançados

* **Snapshots**: crie um snapshot manual
* **Restauração Point-in-Time**: visualize a opção
* **Clone**: `Actions > Create clone`, explique o conceito de copy-on-write
* **Aurora Serverless**: `Create database > Aurora Serverless v2`
* **Global Database**: visualize como adicionar região secundária
* **Integração**: Lambda, exportação para S3, IA com SageMaker

### 6. Monitoramento com Performance Insights

1. Acesse aba **Performance Insights** de uma instância
2. Mostre:
   * Carga de leitura/escrita
   * Tempo de resposta
   * Queries lentas
3. Outros insights:
   * `Aurora Replica Lag`, `Volume Bytes Used`, `Freeable Memory`

### 7. Limpeza Final (Evitar Custos)

1. Acesse **RDS > Databases**
2. Selecione o cluster `aurora-demo-cluster`
3. `Actions > Delete`
4. Desmarque `Create final snapshot`
5. Confirme com `delete me`

## ✅ Conclusão

Você explorou um cluster Amazon Aurora e seus recursos avançados:

**✅ Checklist de Conquistas:**
- [ ] Cluster Aurora criado com réplica em AZ diferente
- [ ] Endpoints de escrita e leitura identificados
- [ ] Réplica adicional criada e configurada
- [ ] Failover automático simulado e observado
- [ ] Recursos avançados (snapshots, clone, serverless) explorados
- [ ] Performance Insights analisado
- [ ] Cluster deletado para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Aurora**: Banco relacional gerenciado com arquitetura própria
* **Endpoints**: cluster (write), reader (read balanceado), instância (específico)
* **Failover automático**: < 30 segundos
* **Réplicas**: até 15, leitura com baixa latência
* **Restauração Point-in-Time**: clonagem rápida
* **Serverless**: escalabilidade automática
* **Global Database**: replicado entre regiões com latência < 1s
