## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 4: Site Estático com Amazon S3 + CloudFront

## 🎯 Objetivo

Publicar um site estático na AWS com armazenamento e hospedagem no **Amazon S3**, entrega global com **Amazon CloudFront**, **HTTPS gratuito** via CDN e interface visual com HTML, imagem e animação. **Nível: Básico**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Este laboratório está dentro do Free Tier tradicional (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * S3: 5 GB de armazenamento, 20.000 requisições GET/mês no Free Tier
> * CloudFront: 50 GB/mês de saída, 2 milhões de requisições/mês no Free Tier
> * Excesso de transferência pode gerar custos
> * Sempre **remova recursos** ao final do exercício

## 🛠️ Pré-requisitos

- Conta AWS ativa
- Acesso ao **Console AWS** e **CloudShell** (opcional)
- Arquivos necessários:
  - `index.html` com estrutura do site
  - `aws-certified-solutions-architect-associate.png` (imagem decorativa)

> 💡 **Dica criativa**: Use ferramentas de GenAI como **Amazon Q Developer** ou ChatGPT para gerar um HTML moderno com prompt: *"Crie um index.html para um site pessoal com meu nome, uma imagem e texto animado de boas-vindas"*

## Passo 1: Criar Bucket no S3

1. Acesse o serviço **S3**
2. Clique em **Criar bucket**
3. **Nome**: `s3-site-estatico-saa-<seunome>`
4. **Região**: `São Paulo` (ou outra de sua escolha)
5. **Desmarque**: `Bloquear todo o acesso público`
6. **Confirme** a caixa de aviso
7. Clique em **Criar bucket**

## Passo 2: Ativar Hospedagem de Site Estático

1. Acesse o bucket criado
2. Aba **Propriedades** > role até **Static website hosting**
3. Clique em **Editar**
4. Marque **Ativar**
5. **Documento de índice**: `index.html`
6. **Salve** a configuração

## Passo 3: Fazer Upload dos Arquivos

1. Acesse a aba **Objetos**
2. Clique em **Fazer upload**
3. Envie os arquivos:
   - `index.html`
   - `aws-certified-solutions-architect-associate.png`
4. Após upload, selecione cada um e clique em **Ações** > **Tornar público**

## Passo 4: Aplicar Política Pública no Bucket

Para evitar erro **403 Access Denied**, aplique esta política:

1. Vá em **Permissões** > **Política do bucket**
2. Cole a política substituindo `<seunome>`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::s3-site-estatico-saa-<seunome>/*"
    }
  ]
}
```

## Passo 5: Testar Acesso Direto via S3 (Opcional)

1. Volte à aba **Propriedades** do bucket
2. Em **Static website hosting**, copie o **endpoint gerado**
3. Exemplo: `http://s3-site-estatico-saa-<seunome>.s3-website-sa-east-1.amazonaws.com`
4. **Acesse no navegador**

> 💡 **Deve exibir seu site** com HTML e imagem funcionando

## Passo 6: Criar Distribuição no CloudFront

1. Acesse o serviço **CloudFront**
2. Clique em **Create distribution**
3. Em **Origin domain**, clique em **Use website endpoint**
4. Insira o **endpoint do bucket S3** (modo website)
5. **Protocolo da origem**: `HTTP only` (esperado neste modo)
6. Em **Viewer protocol policy**, selecione: `Redirect HTTP to HTTPS`
7. Clique em **Create distribution**

## Passo 7: Testar via CloudFront (com HTTPS)

1. Aguarde o status da distribuição mudar para **Deployed** (~15 minutos)
2. Copie o **Domain name** gerado (ex: `d3j1p1fiuenbom.cloudfront.net`)
3. Acesse no navegador: `https://d3j1p1fiuenbom.cloudfront.net`

> 💡 **O site deve carregar com HTTPS** ativo e conteúdo entregue pela CDN

## 🧠 Observações e Aprendizados

- O **Static Website Hosting** exige objetos e bucket públicos (sem BPA)
- O **CloudFront entrega conteúdo com HTTPS** mesmo acessando origem HTTP
- **TTL pode ser ajustado** após a distribuição estar ativa
- Essa abordagem é válida para **protótipos, portfólios e landing pages**

## ✅ Conclusão

Ao final deste laboratório você:

- [x] Criou um bucket S3 com **hospedagem de site estático**
- [x] Configurou **acesso público** para arquivos web
- [x] Implementou **CloudFront** para entrega global
- [x] Ativou **HTTPS gratuito** via CDN
- [x] Testou a arquitetura completa de **site estático**
- [x] Compreendeu os conceitos de **Static Website Hosting**

> 🌟 **Você publicou um site completo** usando apenas S3 e CloudFront com entrega segura, rápida e de fácil manutenção
