## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 4: Acesso ao Amazon DocumentDB via Bastion Host

## 🎯 Objetivo

Provisionar uma instância EC2 gratuita para atuar como bastion host, configurar Security Groups com foco em reuso e segurança, e testar o acesso seguro ao cluster Amazon DocumentDB já provisionado. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> EC2 t2.micro está no Free Tier com 750 horas/mês. DocumentDB oferece 750 horas/mês com `db.t3.medium`.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Se tiver múltiplas instâncias DocumentDB, o tempo será contado em dobro
> * Mantenha EC2 e cluster ativos apenas quando necessário
> * Sempre **remova recursos** ao final do exercício

## ⭐ Passos a Executar

### 1. Criar a instância EC2 (Bastion Host)

1. Acesse o serviço **EC2** > **Launch Instance**
2. Configure os parâmetros:
   * **Nome da instância**: `bastion-host-documentdb`
   * **AMI**: Amazon Linux 2 ou Amazon Linux 2023
   * **Tipo de instância**: `t2.micro` (Free Tier) ou `t3` conforme a disponibilidade do Free Tier
   * **Par de chaves**: Selecione uma existente ou crie nova

3. Em **Network settings**:
   * VPC: mesma VPC do DocumentDB
   * Subnet: uma **subnet pública**
   * **Atribuir IP Publico**: **Ativado**
   * **Auto-assign public IP**: **Enable**

4. Em **Security Group (SG)**:
   * Crie um novo SG chamado `sg-ec2-acesso-privado`
   * Regras de entrada:
     * **Porta 22 (SSH)**: Seu IP
   * Regras de saída:
     * **Tudo liberado** por padrão (pode restringir depois)

> 🎯 Este SG será reutilizado para outras EC2 que acessam recursos privados na VPC.
> 💡 Como boa prática, use **SG como origem de outro SG**. No futuro, o SG do DocumentDB pode permitir acesso **apenas** deste `sg-ec2-acesso-privado`

5. Clique em **Launch Instance** e aguarde o status "Running"

### 2. Acessar a EC2 e Testar o DocumentDB

1. Acesse via terminal:

```bash
ssh -i "sua-chave.pem" ec2-user@<IP_PUBLICO_DA_EC2>
```

2. Dentro da EC2, instale o cliente MongoDB:

```bash
sudo yum update -y
sudo amazon-linux-extras enable epel -y
sudo yum install -y mongodb-org-shell
```

> Se o comando acima falhar, tente: `sudo yum install -y mongodb`

3. Baixe o certificado SSL:

```bash
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

4. Teste a conexão com o DocumentDB:

```bash
mongo --tls \
  --host docdb-condominio.cluster-xxxx.sa-east-1.docdb.amazonaws.com:27017 \
  --tlsCAFile global-bundle.pem \
  -u userlab -p docdb2025
```

> Substitua o endpoint com o seu real. Essa etapa comprova que a EC2 pública consegue atingir o cluster privado.

### 3. (Opcional) Túnel SSH para Acesso Local

> Esta etapa permite que você utilize ferramentas locais como MongoDB Compass para se conectar ao banco via EC2.

1. Crie o túnel da sua máquina local para o DocumentDB via bastion:

```bash
ssh -i "sua-chave.pem" -N -L 27017:<ENDPOINT_DO_CLUSTER>:27017 ec2-user@<IP_PUBLICO_DA_EC2>
```

💡 *Dica:* Para manter o túnel vivo:

```bash
ssh -i "sua-chave.pem" -t ec2-user@<IP_PUBLICO_DA_EC2> "ping 127.0.0.1 > /dev/null & bash"
```

2. Baixe o certificado SSL na sua máquina:

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem" -OutFile "C:\\Users\\<seu_usuario>\\global-bundle.pem"
```

**Linux/macOS:**
```bash
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

3. Abra o MongoDB Compass e configure:

**URI de conexão:**
```text
mongodb://userlab:docdb2025@localhost:27017/?tls=true&tlsAllowInvalidHostnames=true&directConnection=true&tlsCAFile=C:\\Users\\<seu_usuario>\\global-bundle.pem
```

Em "Advanced Options":
* Marque **TLS/SSL**
* Marque **Allow invalid hostnames**
* Selecione o arquivo do certificado

Clique em **Connect**

### 4. Limpeza de Recursos

1. **Pare ou exclua a instância EC2** se não for reutilizar
2. O DocumentDB pode permanecer ativo se for usado em outros labs. Caso contrário:
   * Acesse DocumentDB > Actions > Delete cluster
   * Desmarque snapshot final (ou mantenha, se desejar backup)

## ✅ Conclusão

Você configurou um bastion host seguro para acessar banco em subnet privada:

**✅ Checklist de Conquistas:**
- [ ] Instância EC2 criada como bastion host
- [ ] Security Group configurado com acesso SSH restrito
- [ ] Cliente MongoDB instalado na EC2
- [ ] Certificado SSL baixado e configurado
- [ ] Conexão ao DocumentDB testada com sucesso
- [ ] (Opcional) Túnel SSH configurado para acesso local
- [ ] Recursos removidos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Bastion Host**: EC2 em subnet pública para acesso a recursos privados
* **Security Groups**: Controle de acesso por origem e destino
* **Certificados SSL**: Conexões seguras com DocumentDB
* **Túnel SSH**: Acesso local a recursos remotos via proxy
* **Isolamento de rede**: Bancos em subnets privadas para segurança
