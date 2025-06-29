#!/bin/bash
# Necessário ter o jq instalado (para parsear o JSON)
# Instale com: sudo apt install jq

# === CONFIGURAÇÕES DO USUÁRIO ===
MFA_ARN="arn:aws:iam::123456789012:mfa/cli-user"   # ← Substitua pelo seu ARN real
PROFILE_NAME="default"                             # Ou use "mfa" se quiser usar um perfil separado

# === ENTRADA DO USUÁRIO ===
read -p "Digite o código MFA: " TOKEN

# === SOLICITA TOKEN TEMPORÁRIO ===
CRED=$(aws sts get-session-token \
  --serial-number "$MFA_ARN" \
  --token-code "$TOKEN" \
  --output json)

# === EXTRAI DADOS ===
AWS_ACCESS_KEY_ID=$(echo "$CRED" | jq -r '.Credentials.AccessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo "$CRED" | jq -r '.Credentials.SecretAccessKey')
AWS_SESSION_TOKEN=$(echo "$CRED" | jq -r '.Credentials.SessionToken')

# === APLICA NO PERFIL ===
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID" --profile "$PROFILE_NAME"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY" --profile "$PROFILE_NAME"
aws configure set aws_session_token "$AWS_SESSION_TOKEN" --profile "$PROFILE_NAME"

echo "Token aplicado no perfil [$PROFILE_NAME] com sucesso!"