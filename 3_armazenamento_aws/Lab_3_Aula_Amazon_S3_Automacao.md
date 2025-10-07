## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# � Lab 3: Lifecycle, Notificações e Pre-signed URLs no Amazon S3

## 🎯 Objetivo

Expandir o bucket S3 com funcionalidades avançadas: **políticas de ciclo de vida (Lifecycle)**, **notificações de upload via SNS**, **geração de Pre-signed URLs** com tempo limitado e execução prática via **AWS CloudShell**. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> ⚠️ **Transições de classe de armazenamento** geram custos por solicitação e não estão no Free Tier.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Transições de classe geram custos por solicitação
> * Teste com arquivos pequenos para minimizar custos
> * Regras de expiração (deleção) não geram custo adicional
> * Sempre **remova recursos** ao final do exercício

## 🧰 Pré-requisitos

- Bucket `s3-origem-seguranca-sp-<seunome>` já criado
- Permissões para **S3**, **SNS**, **IAM** e **CloudShell**
- Bucket e SNS devem estar na **mesma região** (`sa-east-1`)

## Passo 1: Criar Regras de Lifecycle Separadas por Fase

### Regra 1 – `lifecycle-30d`
1. Vá até o bucket > aba **Gerenciamento** > **Lifecycle rules**
2. Clique em **Criar regra**
3. **Nome**: `lifecycle-30d`
4. **Aplicar a**: todos os objetos
5. Ative **transição de versões atuais**:
   - Após **30 dias** → `S3 Standard-IA`
6. **Salve** a regra

### Regra 2 – `lifecycle-60d`
1. **Criar nova regra**
2. **Nome**: `lifecycle-60d`
3. **Aplicar a**: todos os objetos
4. **Transição de versões atuais**:
   - Após **60 dias** → `S3 Glacier Flexible Retrieval`
5. **Salvar**

### Regra 3 – `lifecycle-90d`
1. **Criar nova regra**
2. **Nome**: `lifecycle-90d`
3. **Aplicar a**: todos os objetos
4. **Expiração de versões atuais**:
   - Após **90 dias** → excluir objeto
5. **Salvar**

> � **Essas regras simulam** um ciclo de vida comum de dados arquivados e controlam o custo de armazenamento ao longo do tempo

## Passo 2: Criar Tópico SNS para Notificações

1. Acesse o serviço **Amazon SNS**
2. Clique em **Criar tópico**
3. **Tipo**: `Padrão`
4. **Nome**: `sns-notificacoes-s3-lab`
5. **Criar tópico**

### (Opcional) Criar Assinatura por E-mail
1. Clique em **Criar assinatura**
2. **Protocolo**: `E-mail`
3. **Endpoint**: insira seu e-mail
4. **Confirme** clicando no link enviado

## Passo 3: Permitir que o S3 Publique no SNS

1. No tópico SNS criado, vá até **Permissões** > **Política de acesso**
2. **Edite** e cole a seguinte política (ajuste `<sua-conta>` e `<seunome>`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3Publish",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "SNS:Publish",
      "Resource": "arn:aws:sns:sa-east-1:<sua-conta>:sns-notificacoes-s3-lab",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:::s3-origem-seguranca-sp-<seunome>"
        }
      }
    }
  ]
}
```

> 🔐 Esta política limita a publicação no tópico apenas ao bucket específico

---

## Passo 4: Configurar Evento no Bucket para Publicar no SNS

1. Volte ao bucket `s3-origem-seguranca-sp-<seunome>`
2. Vá em **Propriedades > Eventos**
3. Clique em **Criar evento**
4. Nome: `evento-upload-sns`
5. Tipo de evento: **PUT (upload de objeto)**
6. Destino: **SNS topic** → selecione `sns-notificacoes-s3-lab`
7. Salve

> 📣 A cada upload, o bucket publicará uma notificação no tópico SNS

---

## Passo 5: Gerar Pre-signed URLs via CloudShell

1. Abra o **CloudShell** (ícone de terminal no topo do console)
2. Certifique-se de estar na mesma região do bucket (ex: `sa-east-1`)
3. Use o comando abaixo para gerar uma URL válida por 1 hora:

```bash
aws s3 presign s3://s3-origem-seguranca-sp-<seunome>/nome-do-arquivo.txt --expires-in 3600
```

4. **Copie e acesse** a URL em um navegador (válida até expirar)

> � **Útil para compartilhamento temporário** e seguro sem tornar público o bucket

## ✅ Conclusão

Ao final deste laboratório você:

- [x] Criou **regras de ciclo de vida** para controle automático de custos
- [x] Configurou **notificações reativas** com SNS para monitoramento
- [x] Implementou **políticas de acesso** para integração S3-SNS
- [x] Gerou **Pre-signed URLs** para compartilhamento seguro e temporário
- [x] Utilizou **AWS CloudShell** para automação via CLI

> 🌟 **Esses recursos tornam o S3** mais automatizado, auditável e flexível para diferentes cenários empresariais

---
