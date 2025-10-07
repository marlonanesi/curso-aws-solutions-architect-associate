## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🛡️ Lab: Criando um Usuário IAM com MFA e Acesso via AWS CLI com STS

## 🎯 Objetivo

Este laboratório irá guiá-lo na criação de um **usuário IAM com autenticação MFA**, configuração de **acesso programático seguro** via **STS (AWS Security Token Service)** e uso da **AWS CLI** para autenticação temporária.

---

## 💰 Custos e Cuidados

> ℹ️ Este laboratório **não gera custos diretos fora do Free Tier**, pois envolve apenas a criação de um usuário IAM e uso da AWS CLI com credenciais temporárias. No entanto, **o uso prolongado de chaves ativas ou permissões excessivas pode representar riscos de segurança**.

> ⚠️ **Orientação Importante**: Após concluir os testes, **remova o usuário IAM criado ou desative suas credenciais** para evitar riscos de acesso indevido. Mesmo que não haja cobrança, manter credenciais ativas desnecessariamente pode violar boas práticas de segurança.

---

## 🧱 Pré-requisitos

* Conta AWS com permissão para criar usuários IAM
* Acesso à console AWS como usuário com privilégios administrativos
* Um smartphone com aplicativo de autenticação MFA (ex: Google Authenticator, Authy)

---

## 🪪 Etapa 1: Criar um usuário IAM para acesso via terminal

1. Acesse o [IAM na AWS Console](https://console.aws.amazon.com/iam/)
2. Clique em **Users** (Usuários) → **Add users**
3. Defina:

   * Nome: `usuario-terminal`
   * Tipo de acesso: marque **Access key - Programmatic access**
4. Clique em **Next: Permissions**
5. Escolha uma política mínima, por exemplo:

   * `ReadOnlyAccess` *(ou crie uma policy customizada com acesso restrito)*

   > ⚠️ Cuidado ao usar acesso de Administrador. Use com prudência.
6. Clique em **Next** até finalizar e anote o **Access Key ID** e o **Secret Access Key**

---

## 🔐 Etapa 2: Habilitar MFA para o usuário

1. Vá em **IAM > Users > usuario-terminal**
2. Clique em **Security credentials**
3. Em **Assigned MFA device**, clique em **Manage**
4. Escolha **Virtual MFA device**
5. Escaneie o QR Code com o app autenticador
6. Digite os dois códigos gerados
7. Finalize

---

## 💻 Etapa 3: Instalar a AWS CLI

### Windows

```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

### macOS

```bash
brew install awscli
```

### Linux (Debian/Ubuntu)

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Verifique a instalação:

```bash
aws --version
```

---

## ⚙️ Etapa 4: Configurar o perfil base do usuário

```bash
aws configure --profile usuario-mfa
```

Preencha:

* AWS Access Key ID: (da criação do usuário)
* AWS Secret Access Key: (da criação do usuário)
* Region: `us-east-1` *(ou sua região preferida)*
* Output format: `json`

---

## 🔄 Etapa 5: Autenticação Temporária com MFA (usando STS)

Obtenha os **códigos MFA temporários** e execute:

```bash
aws sts get-session-token \
  --serial-number arn:aws:iam::123456789012:mfa/usuario-terminal \
  --token-code 123456 \
  --profile usuario-mfa
```

Anote os valores retornados:

* `AccessKeyId`
* `SecretAccessKey`
* `SessionToken`

Configure um perfil temporário:

```bash
aws configure --profile usuario-temporario
```

Insira as credenciais temporárias obtidas acima.

Você agora pode usar este perfil para interagir com a AWS de forma segura:

```bash
aws s3 ls --profile usuario-temporario
```

---

## 🧼 Etapa Final: Revogue sessões quando necessário

Para segurança, revogue sessões inválidas ou não utilizadas regularmente, e nunca compartilhe suas chaves.

---

## ✅ Conclusão

Você configurou um acesso seguro com MFA usando o STS e AWS CLI. Esse processo é importante para operações seguras locais, respeitando as boas práticas de segurança da AWS.

---
