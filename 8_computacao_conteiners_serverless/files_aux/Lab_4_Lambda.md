# 🧪 Lab 4: Função Lambda Básica na AWS

## 🌟 Objetivo

Criar uma função **AWS Lambda** simples e interativa, executando código sem provisionar servidores. Vamos explorar a interface da console, realizar testes e ver resultados práticos na hora.

---

## 🔍 Conceito-chave

* **AWS Lambda** é um serviço de computação serverless que executa código em resposta a eventos.
* O código é executado em um contêiner efêmero, gerenciado automaticamente pela AWS.

---

## 🔧 Etapa 1: Criar a função Lambda

1. Acesse o [console da AWS Lambda](https://console.aws.amazon.com/lambda/)
2. Clique em **"Criar função"**
3. Selecione **"Autor do zero"**

   * Nome da função: `hello-mundo`
   * Tempo de execução: `Python 3.11`
   * Permissões: selecione **"Criar nova função com permissões básicas do Lambda"**
4. Clique em **"Criar função"**

---

## ✏️ Etapa 2: Editar o código da função direto na console

1. Na aba **"Código-fonte"**, substitua o código padrão por:

```python
def lambda_handler(event, context):
    nome = event.get("nome", "Visitante")
    return {
        'statusCode': 200,
        'body': f'Olá, {nome}! Bem-vindo à AWS Lambda!'
    }
```

2. Clique em **"Deploy"**

---

## ⚙️ Etapa 3: Testar a função na própria console

1. Clique em **"Testar"**
2. Configure um novo evento de teste:

   * Nome do evento: `teste-nome`
   * JSON:

```json
{
  "nome": "seu-nome"
}
```

3. Clique em **"Salvar"** e depois em **"Testar"**
4. Resultado esperado:

```json
{
  "statusCode": 200,
  "body": "Olá, seu-nome! Bem-vindo à AWS Lambda!"
}
```

---

## ⚠️ Importante

Este lab não gera custos significativos dentro do **Free Tier**, mas lembre-se de apagar a função se não for mais utilizar:

1. Acesse o console Lambda
2. Selecione a função `hello-mundo`
3. Clique em **"Ações > Excluir"**
