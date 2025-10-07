## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🐳 Introdução ao Docker

## Objetivo

Apresentar os principais conceitos do Docker e oferecer uma experiência prática utilizando um projeto real.

Você aprenderá:

* O que é Docker e para que serve
* Comandos básicos: `docker build`, `docker run`, `docker ps`, `docker exec`, `docker stop`, `docker rm`
* O que é um **container interativo**
* Como subir uma aplicações com backend FastAPI e frontend em NextJS. Ou qualquer coisa na verdade!

---

## 🧠 Conceitos Iniciais

### O que é Docker?

Docker é uma plataforma para empacotar, distribuir e executar aplicações em containers. Um **container** é uma "caixa isolada" que roda seu código e suas dependências em qualquer lugar.

### Diferença entre Imagem e Container:

* **Imagem**: é um blueprint (modelo) do container, geralmente definida em um `Dockerfile`
* **Container**: é uma instância em execução da imagem

### O que é um Container Interativo?

Um container interativo é aquele que você entra nele como se estivesse dentro de uma máquina virtual:

```bash
docker run -it python:3.11-slim /bin/bash
```

* `-i`: modo interativo
* `-t`: aloca um terminal
* `/bin/bash`: comando para abrir um shell

---

## 🛠️ Estrutura do Projeto que utilizaremos nessa aula, na de ECR (push) e Deploy no App Runner

```
pocs/
 └── container/
     ├── app_base/
     │   └── templates/
     ├── .dockerignore
     ├── config.py
     ├── Dockerfile
     ├── main.py
     ├── mock_data.json
     ├── notificacoes_local.py
     ├── notificacoes.db
     └── requirements.txt
```

---

## 📦 Construindo a imagem

No terminal, navegue até a pasta `container/app_base`:

```bash
cd container/app_base
docker build -t app .
```

> Isso cria uma imagem chamada `app` com base no `Dockerfile`.

### .dockerignore

Certifique-se de ter este conteúdo no `.dockerignore` para evitar arquivos desnecessários na imagem:

```
__pycache__
*.db
```

---

## 🚀 Executando o container

```bash
docker run -d --name app -p 8000:8000 app
```

* `-d`: modo "detached" (em segundo plano)
* `--name app`: nome do container
* `-p 8000:8000`: mapeia a porta 8000 local para a porta do container

Acesse no navegador: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Testando em modo interativo

Entre no container:

```bash
docker exec -it app /bin/bash
```

Explore o conteúdo, acesse logs, veja arquivos como o `notificacoes.db` sendo criado ou atualizado.

---

## 🛠️ Teste Avançado com Jenkins

Se quiser subir algo mais robusto, como um servidor Jenkins:

### Criar a imagem Jenkins

```bash
docker build -t jenkins-custom -f Dockerfile_Jenkins .
```

### Rodar o Jenkins

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 jenkins-custom
```

Acesse: [http://localhost:8080](http://localhost:8080)

---

## 🧹 Dicas de Limpeza

### Listar containers em execução:

```bash
docker ps
```

### Parar e remover container:

```bash
docker stop app
docker rm app
```

### Remover imagem:

```bash
docker rmi app
```

---
