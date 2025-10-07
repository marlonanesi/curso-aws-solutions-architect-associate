## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 5: Site Estático Seguro com S3 Privado + CloudFront OAC

## 🎯 Objetivo

Migrar um site estático para uma arquitetura segura com **Amazon S3 privado com BPA ativado**, **CloudFront com Origin Access Control (OAC)** para acesso seguro, **HTTPS via CDN** e arquivos hospedados sem exposição direta. **Nível: Avançado**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Este laboratório está dentro do Free Tier tradicional (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * S3: 5 GB de armazenamento, 20.000 requisições GET/mês no Free Tier
> * CloudFront: 50 GB de saída/mês e 2 milhões de requisições HTTP/HTTPS no Free Tier
> * Sempre **remova recursos** ao final do exercício

## 📘 Introdução

No laboratório anterior, publicamos um site estático usando bucket público e Static Website Hosting. Agora vamos evoluir para seguir as **melhores práticas de segurança** com bucket privado, BPA ativado e entrega exclusiva via CloudFront com OAC.

> 💡 **Esta é a abordagem ideal** para ambientes de produção, mesmo para sites públicos

## 🧰 Pré-requisitos

- Bucket com arquivos `index.html` e imagem já enviados (do Lab anterior)
- Permissões para configurar **CloudFront** e editar políticas de bucket **S3**
- O **Static Website Hosting** deve estar desativado

## Passo 1: Desativar Static Website Hosting

1. Acesse o bucket
2. Aba **Propriedades** > role até **Hospedagem de site estático**
3. Clique em **Editar** > selecione **Desativar** > **Salvar**

## Passo 2: Ativar o BPA (Block Public Access)

1. Aba **Permissões**
2. Clique em **Editar** em **Bloquear acesso público**
3. **Marque todas as opções** e **salve**

> 💡 **Agora o bucket está 100% privado** e seguro

## Passo 3: Remover Política Pública Anterior

1. Ainda na aba **Permissões**
2. **Apague a política** `PublicReadGetObject`, se existir
3. **Salve** as alterações

## Passo 4: Criar Distribuição CloudFront com OAC

1. Acesse o serviço **CloudFront**
2. Clique em **Create distribution**
3. **Origem**:
   - **Origem**: `s3-site-estatico-saa-<seunome>.s3.amazonaws.com`
   - **Tipo**: S3 (não use o website endpoint)
4. Em **Origin Access**, clique em `Create control setting`:
   - **Nome**: `oac-site-estatico`
   - **Origin type**: `S3`
   - **Signing behavior**: `Always`
   - **Signing protocol**: `SigV4`
5. **Selecione essa OAC**
6. Em **Viewer protocol policy**: `Redirect HTTP to HTTPS`
7. **Crie a distribuição**

## Passo 5: Aplicar Política Segura no Bucket

1. Acesse **Permissões** > **Política do bucket**
2. Cole a política substituindo `<seunome>`, `<seu-account-id>` e `<id-da-distribuicao>`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::s3-site-estatico-saa-<seunome>/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::<seu-account-id>:distribution/<id-da-distribuicao>"
        }
      }
    }
  ]
}
```

> 💡 **Esta política permite** apenas ao CloudFront acessar os objetos do bucket

## Passo 6: Definir o Arquivo de Índice na Distribuição

1. Acesse sua distribuição **CloudFront**
2. Aba **General** > clique em **Edit**
3. Em **Default root object**, adicione: `index.html`
4. **Salve** a configuração

## Passo 7: Testar o Site

1. Aguarde o status da distribuição ser **Deployed** (~15 minutos)
2. Acesse o **domínio CloudFront** (ex: `https://dxxxxx.cloudfront.net`)

> 💡 **O site deve carregar** com conteúdo HTML + imagem via HTTPS, sem acesso direto ao S3

## 🧠 Considerações e Dicas

- **OAC substitui o antigo OAI** e é o método recomendado para acessos privados via CloudFront
- Com **BPA ativado**, o S3 não responde a requisições diretas, protegendo seus objetos
- A **URL CloudFront pode ser personalizada** com domínio e certificado (via ACM)
- O **conteúdo pode ser atualizado** via S3 e invalidado no CloudFront conforme necessidade

## ✅ Conclusão

Ao final deste laboratório você:

- [x] Migrou de arquitetura pública para **privada e segura**
- [x] Desativou **Static Website Hosting** para maior segurança
- [x] Ativou **BPA (Block Public Access)** no bucket S3
- [x] Configurou **CloudFront com OAC** para acesso controlado
- [x] Implementou **política de bucket restritiva** para CloudFront
- [x] Testou a arquitetura **segura de produção**
- [x] Compreendeu as **melhores práticas** de hospedagem segura

> 🌟 **Agora você domina** a arquitetura recomendada pela AWS para sites estáticos em ambientes de produção com máxima segurança
