# 🧪 Lab 1: Usando Route 53 com Alias para o ALB

## 🎯 Objetivo

Criar uma **zona de hospedagem no Route 53** e apontar um **registro Alias A** para o **Application Load Balancer (ALB)** criado anteriormente. Com isso, a aplicação fica acessível por um **nome de domínio** gerenciado e resolvido pelo DNS da AWS.

---

## 🧠 Conceito-chave

- O **Route 53** permite gerenciar domínios públicos e privados com alta disponibilidade.
- Um **Alias Record** é como um CNAME, mas **pode ser usado na raiz do domínio** e é **gratuito** ao apontar para serviços AWS.
- Ideal para mapear `meusite.com` diretamente para o DNS do ALB, sem custos adicionais e com integração nativa.

---

## 🔧 Pré-requisitos

- Um **ALB existente** (do lab anterior), com DNS como:  
  `alb-asg-demo-xxxxxxxx.elb.sa-east-1.amazonaws.com`
- Um domínio comprado e gerenciado pela AWS (ou transferido para o Route 53)  
  Exemplo: `exemplo.meudominio.com`
- Permissão para criar zonas hospedadas e registros DNS

---

## 🛠️ Etapas

### 1. Criar a Zona de Hospedagem no Route 53

1. Console → **Route 53 → Zonas hospedadas → Criar zona hospedada**
2. Nome do domínio: `exemplo.com` (ou o domínio real)
3. Tipo: **Pública**
4. Clique em **Criar zona hospedada**

> 💡 *Se o domínio foi comprado fora da AWS, atualize os DNS servers na sua registradora com os valores da zona.*

---

### 2. Criar o Registro Alias A

1. Dentro da zona hospedada criada → Clique em **Criar registro**
2. Nome do subdomínio: `www` (ou deixe em branco para raiz)
3. Tipo: **A – IPv4**
4. Alias: **Sim**
5. Destino: selecione o **Application Load Balancer** (aparece listado)
6. Clique em **Criar registro**

---

### 3. Testar o domínio

- Acesse no navegador:  
  `http://www.exemplo.com`  
  ou  
  `http://exemplo.com`  
  conforme o que configurou

> ⚠️ Pode levar alguns minutos por causa do TTL e propagação DNS (dependendo do domínio).

---

## ✅ Resultado Esperado

- Ao acessar o domínio, a aplicação do ALB (com ASG por trás) será carregada
- Nenhum custo extra será gerado pelo Alias
- O domínio pode ser alterado futuramente sem reconfigurar o ALB

---

## 🧠 O que você aprendeu

- Como criar e gerenciar zonas no Route 53
- Como usar **Alias Records** para apontar para serviços AWS
- Como transformar uma aplicação escalável em um ambiente **oficial de produção via DNS**

---

## 🎤 Encerramento sugerido

> "Hoje integramos nossa aplicação escalável com um nome de domínio próprio, usando os recursos nativos da AWS. Com apenas alguns cliques, tornamos acessível ao mundo uma arquitetura elástica, com domínio profissional e DNS gerenciado. Essa é a ponte final entre infraestrutura e produto real."