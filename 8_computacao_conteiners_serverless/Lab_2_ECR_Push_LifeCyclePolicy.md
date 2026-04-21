                                                                                                   ## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
## 🧪 Lab 2: Repositório ECR com Política de Ciclo de Vida e Push de Imagem

## 🎯 Objetivo

Neste laboratório, vamos:

1. Criar um repositório Docker no **Amazon ECR** (Elastic Container Registry) via console;
2. Configurar uma **política de ciclo de vida** para eliminar imagens antigas automaticamente;
3. Fazer o **push de uma imagem Docker local** para o ECR e visualizar o resultado na console.

---

## 🧠 Conceito-chave

* **Amazon ECR** é um repositório privado gerenciado para armazenar imagens de contêiner Docker.
* **Políticas de ciclo de vida (Lifecycle Policies)** ajudam a controlar o número de imagens salvas, reduzindo custos.

---

## 🔧 Etapa 1: Criar o repositório no ECR via console

1. Acesse o [Amazon ECR Console](https://console.aws.amazon.com/ecr/repositories)
2. Clique em **"Criar repositório"**
3. Configure:

   * Nome: `app-base`
   * Visibilidade: **Privado**
   * Mantenha o restante padrão
4. Clique em **"Criar repositório"**

---

## 🧹 Etapa 2: Adicionar política de ciclo de vida

1. Com o repositório `app-base` aberto, clique na aba **"Ciclo de vida"**
2. Clique em **"Criar regra"**
3. Configure:

   * Nome da regra: `limpar-antigas`
   * Ação: **Excluir**
   * Filtro: **Todas as tags**
   * "Retenha no máximo": **5 imagens**
4. Clique em **"Salvar"**

Essa regra garante que somente as 5 imagens mais recentes sejam mantidas automaticamente.

---

## 📦 Etapa 3: Realizar o push da imagem Docker para o ECR

1. Acesse o repositório recém-criado e clique em **"Ver comandos de push"** (canto superior direito)
2. Aparecerá uma sequência de comandos para:

   * Autenticar no ECR via Docker
   * Taguear a imagem local
   * Fazer push

> ✅ **Dica:** você já aprendeu no início do curso a autenticar seu terminal usando o comando `aws sts get-caller-identity` ou algum alias de login. Se isso estiver funcionando, já pode seguir os comandos normalmente para push.

3. No terminal, navegue até a pasta com seu projeto Docker anterior (como o `app` com FastAPI)

Execute os comandos (adaptando o `<account_id>` e `<region>`):

```bash
aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.sa-east-1.amazonaws.com

docker tag app:latest <account_id>.dkr.ecr.sa-east-1.amazonaws.com/app-base:latest

docker push <account_id>.dkr.ecr.sa-east-1.amazonaws.com/app-base:latest
```

---

## ✅ Valide na Console

1. Volte ao repositório na console da AWS
2. Atualize a página para visualizar a nova imagem publicada
3. Valide também se o App Runner (caso esteja usando) reconhece essa nova imagem

---