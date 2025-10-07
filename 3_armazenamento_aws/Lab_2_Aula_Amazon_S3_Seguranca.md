## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 2: Segurança, Logs, Criptografia e Replicação Cross-Region no Amazon S3

## 🎯 Objetivo

# 🔧 Lab 2: Segurança, Logs, Criptografia e Replicação Cross-Region no Amazon S3

## 🎯 Objetivo

Configurar um ambiente seguro e resiliente no **Amazon S3** com usuário **IAM** dedicado, buckets em múltiplas regiões, políticas restritivas, **logs de acesso**, criptografia **SSE-KMS**, versionamento e **replicação Cross-Region (CRR)**. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> ⚠️ **Este laboratório pode gerar custos** principalmente em tráfego entre regiões e KMS.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Tráfego entre regiões (replicação CRR) gera cobrança
> * Uso de KMS com SSE-KMS tem custos por operação
> * Armazenamento de múltiplas versões consume mais espaço
> * Sempre **remova recursos** ao final do exercício

## Passo 1: Criar Usuário IAM para o Laboratório

1. Acesse **IAM** no console AWS
2. Vá em **Usuários** > **Adicionar usuários**
3. **Nome**: `usuario-s3-hands-on`
4. **Tipo de acesso**: `Acesso programático`
5. **Permissões**: `Anexar políticas diretamente` → selecione `AmazonS3FullAccess`
6. Finalize e **anote as chaves de acesso**

> � **Boas práticas de segurança**: evitar uso da conta root e isolar permissões por usuário

## Passo 2: Criar Buckets S3

### Bucket de Origem
- **Nome**: `s3-origem-seguranca-sp-<seunome>`
- **Região**: `sa-east-1` (São Paulo)
- **Acesso público**: bloqueado

### Bucket de Destino
- **Nome**: `s3-destino-replica-us-east-1-<seunome>`
- **Região**: `us-east-1` (Norte da Virgínia)
- **Acesso público**: bloqueado

### Bucket para Logs
- **Nome**: `s3-logs-<seunome>`
- **Região**: à sua escolha
- **Acesso público**: bloqueado

> � **Separar os buckets** melhora a organização e facilita auditoria e segurança

## Passo 3: Aplicar Política de Bucket na Origem

1. Vá em **Permissões** > **Política do bucket** do bucket de origem
2. Cole a política abaixo, substituindo `<seu-account-id>` e `<seunome>`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<seu-account-id>:user/usuario-s3-hands-on"
      },
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::s3-origem-seguranca-sp-<seunome>",
        "arn:aws:s3:::s3-origem-seguranca-sp-<seunome>/*"
      ]
    }
  ]
}
```

> � **Restringe o acesso** ao usuário do laboratório, simulando ambiente de produção seguro

## Passo 4: Ativar Server Access Logging

1. Acesse **Propriedades** do bucket de origem
2. Vá até **Server access logging**
3. **Ative o logging** e escolha o bucket `s3-logs-<seunome>` como destino

> � **Habilita auditoria detalhada** de acessos e ações no bucket

## Passo 5: Ativar Criptografia SSE-KMS

1. Acesse **Propriedades** do bucket de origem
2. Vá até **Criptografia do lado do servidor**
3. Selecione **SSE-KMS**
4. **Crie uma nova chave KMS** (recomendado) ou use uma existente

> � **Garante controle detalhado** e auditoria sobre o acesso aos dados

## Passo 6: Habilitar Versionamento nos Buckets

1. Vá em **Propriedades** do bucket de origem → habilite o **versionamento**
2. Faça o mesmo para o **bucket de destino**

> � **Essencial para replicação** e proteção contra exclusões acidentais

## Passo 7: Configurar Replicação Cross-Region (CRR)

1. No bucket de origem, vá em **Gerenciamento** > **Regras de replicação**
2. Clique em **Criar regra de replicação**
3. Configure:
   - **Nome da regra**: escolha um nome descritivo
   - **Abrangência**: todos os objetos
   - **Bucket de destino**: `s3-destino-replica-us-east-1-<seunome>`
   - **Permitir replicar objetos criptografados** com SSE-KMS
   - **Criar nova função IAM**
4. **Salve** a configuração

> 💡 **Aumenta resiliência**, continuidade do negócio e recuperação de desastres

## Passo 8: Testar o Ambiente

### Teste 1: Upload de Objeto
1. Envie um arquivo simples para o bucket de origem
2. Verifique se está **criptografado com SSE-KMS**

### Teste 2: Versionamento
1. Reenvie o **mesmo arquivo**
2. Ative **Mostrar versões** e verifique múltiplas versões

### Teste 3: Logs
1. Acesse o **bucket de logs** e confira os registros de acesso

### Teste 4: Replicação
1. Verifique o **bucket de destino** após alguns minutos
2. Confirme que a **replicação ocorreu** com sucesso

* Reenvie o mesmo arquivo
* Ative “Mostrar versões” e verifique múltiplas versões

### Teste 3: Logs

* Acesse o bucket de logs e confira os registros de acesso

### Teste 4: Replicação

* Verifique o bucket de destino após alguns minutos
* Confirme que a replicação ocorreu com sucesso

---

## ✅ Conclusão

Ao final deste laboratório você:

- [x] Criou usuário **IAM** dedicado com permissões específicas
- [x] Configurou buckets S3 em múltiplas regiões (São Paulo e Norte da Virgínia)
- [x] Aplicou políticas de bucket restritivas para segurança
- [x] Ativou **Server Access Logging** para auditoria
- [x] Implementou criptografia **SSE-KMS** para proteção de dados
- [x] Habilitou versionamento para controle de mudanças
- [x] Configurou **replicação Cross-Region** para resiliência
- [x] Testou todos os componentes da arquitetura segura

> 🌟 **Esta arquitetura é base** para soluções seguras e escaláveis com o Amazon S3 em ambientes de produção
