## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
## 🧪 Lab 2: Repositório ECR com Política de Ciclo de Vida e Push de Imagem

# 🚨 Lab 3: Deploy no App Runner com Imagem do ECR (CUSTO!)

> ⚠️ **Atenção:** Este laboratório pode **gerar custos reais** na sua conta AWS. O App Runner é um serviço gerenciado com cobrança por uso, mesmo em ociosidade. Ao finalizar, **delete o serviço App Runner e o repositório ECR** para evitar cobranças indesejadas.

## 🎯 Objetivo

Neste laboratório, vamos:

1. Criar um serviço no **AWS App Runner** a partir de uma imagem armazenada no **Amazon ECR**;
2. Realizar o deploy da aplicação e validar seu funcionamento;
3. Entender os pontos de configuração básicos e boas práticas de limpeza.

---

## 🧠 Conceito-chave

* O **App Runner** permite executar aplicações em contêiner sem gerenciar servidores.
* Ele pode se integrar ao ECR para automatizar o deploy de imagens Docker.
* É ideal para APIs simples, interfaces web ou workers, mas deve-se **monitorar custos**.

---

## 🔧 Etapa 1: Criar o serviço no App Runner

1. Acesse o [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
2. Clique em **"Criar serviço"**
3. Selecione **"Repositório de contêiner"** e escolha **Amazon ECR**
4. Selecione o repositório `app-base` criado anteriormente
5. Escolha a imagem `latest`

Clique em **"Próximo"** e configure:

* Nome do serviço: `app-runner-base`
* Ambiente de execução: `Python 3 ou custom` (manter padrão se imagem já está pronta)
* Porta: `8000` (ajuste conforme exposto na sua imagem)

Finalize com **"Criar e implantar"**

---

## ⏱️ Aguarde o Deploy

O App Runner irá provisionar infraestrutura automaticamente. Esse processo pode levar alguns minutos.

Assim que estiver "Ativo", clique no link gerado para acessar sua aplicação.

---

## 🧼 Etapa Final: Limpeza para evitar cobranças

1. Acesse o serviço App Runner, clique em **"Excluir"**
2. Acesse o ECR, selecione o repositório `app-base`, clique em **"Excluir"**

> 🧽 **Importante:** Excluir os recursos criados impede cobranças futuras.

---

## ✅ Resultado esperado

Ao final do lab:

* Sua aplicação FastAPI/Docker foi publicada com sucesso no App Runner;
* Você compreendeu como funciona o deploy direto do ECR para o App Runner;
* Aprendeu a limpar os recursos para evitar custos.