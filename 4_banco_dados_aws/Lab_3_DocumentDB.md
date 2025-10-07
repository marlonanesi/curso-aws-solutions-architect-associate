## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 3: Amazon DocumentDB - Provisionamento Inicial

## 🎯 Objetivo

Criar um cluster Amazon DocumentDB com uma instância única, configurar autenticação por usuário e senha, associar o cluster a subnets privadas e configurar Security Groups para acesso controlado. **Nível: Básico**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> DocumentDB oferece 750 horas por mês de uso gratuito com instância `db.t3.medium`.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Se criar 1 instância primária + 1 de leitura, o tempo será contado em dobro
> * Após limite do Free Tier, haverá cobrança por hora adicional
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Criar o Cluster DocumentDB

1. Acesse o serviço **Amazon DocumentDB** > **Databases** > **Create**
2. Configure os parâmetros principais:
   * **Identificador do cluster**: `docdb-condominio`
   * **Engine version**: Selecione a mais recente disponível
   * **DB instance class**: `db.t3.medium`
   * **Número de instâncias**: `1` (importante para se manter no Free Tier)
   * **Authentication**:
     * **Username**: `userlab`
     * **Password**: `docdb2025` (evite usar essa senha em ambientes reais)

3. Em **Connectivity**:
   * **VPC**: Selecione a mesma VPC dos seus recursos privados
   * **Subnet Group**: Selecione subnets **privadas** em múltiplas AZs
   * **Public Access**: **Desabilitado**

4. Em **VPC Security Group**:
   * Crie um novo SG ou selecione um existente com porta `27017` liberada (MongoDB)
   * ☝️ **Este SG será ajustado posteriormente para permitir acesso via EC2 (bastion host)**
   * 👉 Como boa prática, a **origem** de um SG (DocumentDB) pode ser **outro SG** — no caso, **o SG da EC2 que atuará como bastion host**
   * Por enquanto, você pode deixar a origem como `My IP` ou abrir para a VPC temporariamente (com cautela)

5. Mantenha os outros parâmetros padrão e clique em **Create cluster**
6. Aguarde até o status mudar para **Available**

> � **Observações importantes:**
> * Você poderá conectar ao cluster futuramente via EC2 ou SSM, utilizando o bastion host criado nos primeiros laboratórios
> * Este cluster será utilizado em exercícios posteriores (consultas, Streams, integração com Lambda, failover, etc)
> * Durante os períodos de inatividade, você pode parar a instância manualmente ou deletar e recriar depois

### 2. Limpeza (Evitar Custos)

1. Acesse **Databases** > Selecione o cluster > **Actions** > **Delete**
2. Desmarque a opção de snapshot final (a menos que deseje backup)
3. Confirme digitando `delete me` e clique em **Delete**

## ✅ Conclusão

Você provisionou um cluster Amazon DocumentDB pronto para uso:

**✅ Checklist de Conquistas:**
- [ ] Cluster DocumentDB criado com instância `db.t3.medium`
- [ ] Autenticação configurada com usuário e senha
- [ ] Cluster associado a subnets privadas
- [ ] Security Group configurado para porta 27017
- [ ] Cluster disponível para conexões futuras
- [ ] Recursos removidos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **DocumentDB**: Banco NoSQL compatível com MongoDB
* **Subnets privadas**: Melhor prática de segurança para bancos de dados
* **Security Groups**: Controle de acesso por porta e origem
* **Free Tier**: Limites de 750 horas mensais para `db.t3.medium`
* **Bastion host**: Acesso seguro a recursos privados
