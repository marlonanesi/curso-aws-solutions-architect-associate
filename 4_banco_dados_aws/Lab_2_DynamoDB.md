## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 2: Amazon DynamoDB - NoSQL Gerenciado e Escalável

## 🎯 Objetivo

Criar uma tabela DynamoDB com chave primária composta, inserir dados no formato chave-valor/documento, realizar consultas com filtros, criar um índice secundário global (GSI) e simular uma arquitetura orientada a eventos com Streams. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> DynamoDB está incluso no Free Tier com até 25 unidades de leitura e escrita por mês.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Modo sob demanda evita cobranças por provisionamento não utilizado
> * Streams e integrações podem gerar custos adicionais
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Criar a Tabela DynamoDB

1. Acesse o serviço **Amazon DynamoDB**
2. Clique em **Tabelas** > **Criar tabela**
3. Parâmetros:
   * Nome: `Pedidos`
   * Chave de partição: `cliente_id` (String)
   * Chave de ordenação: `data_pedido` (String)
   * Modo de capacidade: **Sob demanda (on-demand)**
4. Clique em **Criar tabela**

### 2. Inserir Itens Manualmente

1. Na aba **Itens** da tabela, clique em **Criar item**
2. Ative a opção **Visualizar JSON do DynamoDB**
3. Insira os seguintes itens, um por vez:

```json
{
  "cliente_id": { "S": "c001" },
  "data_pedido": { "S": "2024-06-01" },
  "valor_total": { "N": "250.00" },
  "status": { "S": "enviado" }
}
```

```json
{
  "cliente_id": { "S": "c001" },
  "data_pedido": { "S": "2024-06-15" },
  "valor_total": { "N": "150.00" },
  "status": { "S": "entregue" }
}
```

```json
{
  "cliente_id": { "S": "c002" },
  "data_pedido": { "S": "2024-06-10" },
  "valor_total": { "N": "90.00" },
  "status": { "S": "cancelado" }
}
```

### 3. Consultar por Chave Primária

1. Acesse a aba **Explorar itens**
2. Selecione a tabela **Pedidos**
3. Configure a consulta:
   * Chave de partíção: `cliente_id` = `c001`
4. Execute e observe os pedidos ordenados por `data_pedido`

### 4. Criar Índice Secundário Global (GSI)

1. Acesse a aba **Índices** > **Criar índice**
2. Parâmetros:
   * Chave de partíção: `status` (String)
   * Chave de ordenação: `data_pedido` (String)
   * Nome: `status-data-index`
   * Projeção: **Todos os atributos**
3. Clique em **Criar índice** e aguarde a propagação (1 a 2 minutos)

### 5. Consultar Utilizando o GSI

1. Acesse novamente **Explorar itens**
2. Altere para o índice `status-data-index`
3. Configure a consulta:
   * Chave de partíção: `status` = `entregue`
   * (Opcional) Chave de ordenação: `data_pedido` = `2024-06-15`
4. Execute e visualize os resultados

### 6. Ativar DynamoDB Streams (Arquitetura Reativa)

1. Acesse a aba **Exports and streams** > clique em **Editar**
2. Marque **Enable stream**
3. Tipo: **New and old images**
4. Clique em **Salvar alterações**

> 💡 Este recurso será utilizado em laboratórios futuros com Lambda e EventBridge

### 7. Finalização (Evitar Custos)

1. Delete a tabela DynamoDB `Pedidos`
2. Remova eventuais integrações com Lambda ou Streams

## ✅ Conclusão

Você explorou o Amazon DynamoDB e seus recursos essenciais:

**✅ Checklist de Conquistas:**
- [ ] Tabela DynamoDB criada com chave primária composta
- [ ] Dados inseridos no formato chave-valor/documento
- [ ] Consultas realizadas por chave primária
- [ ] Índice secundário global (GSI) criado e testado
- [ ] DynamoDB Streams ativado para arquitetura reativa
- [ ] Recursos removidos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **DynamoDB**: Banco NoSQL gerenciado e altamente escalável
* **Chave composta**: Partição + ordenação para consultas eficientes
* **GSI**: Índice secundário para consultas por atributos não-chave
* **Streams**: Captura mudanças para arquiteturas orientadas a eventos
* **Casos de uso**: Pedidos por cliente, relatórios por status, logs e eventos