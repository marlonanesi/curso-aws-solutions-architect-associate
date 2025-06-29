@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ==========================================
:: CONFIGURACAO DE AUTENTICACAO MFA AWS
:: ==========================================
:: Este script automatiza o processo de obtenção de credenciais temporárias
:: da AWS usando Multi-Factor Authentication (MFA)

:: ARN do dispositivo MFA vinculado à sua conta AWS
:: Substitua <id da sua conta> pelo ID real da sua conta AWS
set "MFA_ARN=arn:aws:iam::<id da sua conta>:mfa/cli-user-mfa"  

:: Perfil AWS de origem (que possui as credenciais base configuradas)
set "SOURCE_PROFILE=base" 

:: Perfil AWS de destino (onde serão armazenadas as credenciais temporárias com MFA)
set "TARGET_PROFILE=default"

:: ==========================================
:: ENTRADA DO CODIGO MFA
:: ==========================================
:: Solicita ao usuário o código de 6 dígitos do aplicativo autenticador (Google Authenticator, Authy, etc.)
set /p TOKEN=Digite o codigo MFA: 

:: ==========================================
:: PREPARACAO DO SCRIPT POWERSHELL TEMPORARIO
:: ==========================================
:: Define o caminho para um script PowerShell temporário no diretório TEMP do sistema
set "TEMP_PS1=%TEMP%\_mfa_temp_script.ps1"

:: CRIA SCRIPT TEMPORARIO DO POWERSHELL
(
  echo $ErrorActionPreference = 'Stop'
  echo $MfaArn = "%MFA_ARN%"
  echo $SourceProfile = "%SOURCE_PROFILE%"
  echo $TargetProfile = "%TARGET_PROFILE%"
  echo $Token = "%TOKEN%"
  echo try {
  echo   Write-Host "`nSolicitando token temporario com perfil '$SourceProfile'..." -ForegroundColor Cyan
  echo   $cred = aws sts get-session-token --serial-number $MfaArn --token-code $Token --profile $SourceProfile --output json ^| ConvertFrom-Json
  echo   aws configure set aws_access_key_id $cred.Credentials.AccessKeyId --profile $TargetProfile
  echo   aws configure set aws_secret_access_key $cred.Credentials.SecretAccessKey --profile $TargetProfile
  echo   aws configure set aws_session_token $cred.Credentials.SessionToken --profile $TargetProfile
  echo   Write-Host "`nToken aplicado com sucesso no perfil '$TargetProfile'" -ForegroundColor Green
  echo } catch {
  echo   Write-Host "`nErro ao obter token:" -ForegroundColor Red
  echo   Write-Host $_.Exception.Message -ForegroundColor Yellow
  echo }
  echo Pause
) > "%TEMP_PS1%"

:: EXECUTA O SCRIPT POWERSHELL E MANTEM A JANELA ABERTA
powershell -NoExit -ExecutionPolicy Bypass -File "%TEMP_PS1%"

:: REMOVE SCRIPT TEMPORARIO (opcional)
:: del "%TEMP_PS1%"

endlocal
