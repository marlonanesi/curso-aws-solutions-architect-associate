
## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# Laboratório: Acesso Escalável ao Amazon DocumentDB via AWS SSM (Bastion Host Tunado)

## Visão Geral

Neste laboratório, você aprenderá a acessar o Amazon DocumentDB de forma **segura, escalável e auditável** usando o **AWS Systems Manager (SSM)**, eliminando a dependência de chaves SSH e portas abertas.

O plugin do SSM permite o uso de port forwarding via comandos CLI, tornando a conexão mais simples e rastreável, sem necessidade de abrir a porta 22 ou gerenciar chaves manualmente.

---

## Objetivos de Aprendizado

1. Instalar e configurar o plugin do AWS SSM
2. Utilizar port forwarding via SSM para conectar ao Amazon DocumentDB
3. Entender os benefícios de segurança e escalabilidade do SSM frente ao SSH tradicional

---

## Arquitetura

- **VPC** com subnets públicas e privadas (VPC-Condominio-Central)
- **DocumentDB** em subnets privadas
- **Instância EC2** (bastion host) com agente SSM habilitado
- **Conexão local** via plugin do SSM + port forwarding

---

## Parte 1: Requisitos da EC2 (Bastion Tunado e Escalável)

- A instância EC2 deve possuir a IAM Role com a policy `AmazonSSMManagedInstanceCore`
- A EC2 deve estar em subnet com acesso à internet (NAT Gateway ou IP público)
- Security Group com saída para a internet (porta 443 liberada)
- Agente SSM instalado e rodando

---

## Parte 2: Instalando o AWS CLI e o Plugin SSM (na sua máquina local)

### Windows

1. [Instale o AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html)
2. [Instale o SSM Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

```powershell
# Verifique se está tudo ok:
aws --version
session-manager-plugin --version
```

### Linux/macOS

```bash
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_amd64/session-manager-plugin.rpm" -o session-manager-plugin.rpm
sudo yum install -y ./session-manager-plugin.rpm
```

---

## Parte 3: Habilitando e Atualizando o SSM Agent na EC2

Acesse a instância via SSH (caso necessário) e execute:

```bash
# Habilite o agente SSM para iniciar automaticamente
sudo systemctl enable amazon-ssm-agent

# (Recomendado) Atualize o agente SSM para a versão mais recente
sudo yum install -y amazon-ssm-agent
sudo systemctl restart amazon-ssm-agent
```

> **Atenção:**  
> Para que o agente SSM funcione corretamente, é obrigatório liberar a **porta 443 (HTTPS)** para saída no Security Group da EC2.  
> Além disso, valide se as regras de saída também estão permitidas nas **NACLs** (Network ACLs) associadas à subnet da instância.
>
> Se você adicionou alguma regra de saída temporária no Security Group da EC2 apenas para testes, pode removê-la após garantir que a porta 443 está liberada e validada nas NACLs.

---

## Parte 4: Iniciando o Port Forwarding com SSM

Substitua o `instance-id` pelo ID da sua instância EC2 (bastion host) já registrada no SSM:

```bash
aws ssm start-session \
  --target i-0a316694d7ed7d2ba \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["docdb-condominio.cluster-ctk6u26y28ic.sa-east-1.docdb.amazonaws.com"],"portNumber":["27017"],"localPortNumber":["27017"]}' \
  --profile default
```

Ao executar, será criado um túnel local na porta 27017 que redireciona o tráfego para o DocumentDB dentro da VPC via a instância intermediária.

> **Importante:**  
> A instância EC2 deve estar na mesma VPC ou ter rota para acessar o DocumentDB.

---

## Parte 5: Conectando ao DocumentDB Localmente

Com o túnel ativo, utilize a seguinte string de conexão:

```bash
mongo "mongodb://userlab:docdb2025@localhost:27017/?tls=true&tlsAllowInvalidHostnames=true&directConnection=true"
```

Ou configure o MongoDB Compass:

- **Hostname:** localhost
- **Port:** 27017
- **SSL:** Sim, com certificado `global-bundle.pem`

---

## Parte 6: Benefícios do Acesso via SSM

- ✅ Elimina necessidade de abrir porta 22 (SSH)
- ✅ Evita gestão manual de chaves (uso via IAM + autenticação da AWS CLI)
- ✅ Escalável para vários ambientes
- ✅ Totalmente auditável (CloudTrail e logs de sessão)
- ✅ Mais seguro em ambientes multi-usuário e corporativos

---

## Recursos Avançados

- ⭐ É possível abrir múltiplos túneis simultaneamente com `start-session` em abas diferentes
- ⭐ Com `AWS-StartPortForwardingSession`, você pode conectar a diversos recursos (como Redis, PostgreSQL, APIs privadas)
- ⭐ Pode ser integrado a pipelines DevOps (com SSM automático via boto3 ou CLI)

---

## Limpeza dos Recursos

- Finalize a sessão SSM no terminal (Ctrl+C)
- Encerre a instância EC2 se for temporária
- Monitore pelo AWS Systems Manager > Session Manager > Histórico

---

## Conceitos Importantes para a Certificação SAA-C03

- **SSM Agent:** Agente instalado na instância que permite automação e acesso seguro
- **Session Manager:** Canal seguro e auditado para conexões
- **Document AWS-StartPortForwardingSessionToRemoteHost:** Permite redirecionamento de portas com SSM
- **Princípio do mínimo privilégio:** Acesso apenas ao que é necessário, quando necessário
- **IAM + SSM + CloudTrail:** Tripé de segurança, rastreabilidade e controle

---

## Recursos Adicionais

- [SSM Port Forwarding - Documentação Oficial](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-start-session.html#session-manager-start-session-port-forwarding)
- [CloudTrail para Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-auditing.html)
