## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 2.4: EFS e Instance Store - Armazenamento Compartilhado vs Temporário

## 🎯 Objetivo

Dominar o Amazon EFS (Elastic File System) como solução de armazenamento compartilhado entre instâncias EC2 e compreender as características do Instance Store para armazenamento temporário de alta performance. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> 5 GB de armazenamento EFS Standard incluídos no Free Tier (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * EFS é cobrado por GB armazenado e operações de I/O
> * Instance Store é incluído no preço da instância (sem custo adicional)
> * Transferência de dados entre AZs pode gerar custos
> * Sempre **delete sistemas EFS não utilizados** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender Conceitos Fundamentais de Armazenamento

**EFS (Elastic File System):**

O EFS é um sistema de arquivos NFS totalmente gerenciado que pode ser montado simultaneamente por múltiplas instâncias EC2. Funciona como um "HD compartilhado na nuvem" que cresce e diminui automaticamente conforme necessário.

**Características do EFS:**
- **Compartilhado**: Múltiplas instâncias podem acessar simultaneamente
- **Escalável**: Cresce automaticamente até petabytes
- **Durável**: Replicado automaticamente entre AZs
- **POSIX-compliant**: Funciona como sistema de arquivos Linux padrão
- **Performance modes**: General Purpose vs Max I/O

**Instance Store:**

Instance Store é armazenamento local temporário fisicamente anexado ao servidor host da instância EC2. Oferece performance extremamente alta, mas os dados são perdidos quando a instância é parada ou terminada.

**Características do Instance Store:**
- **Temporário**: Dados perdidos quando instância para/termina
- **Local**: Anexado fisicamente ao host
- **Alta performance**: IOPS muito altos, baixa latência
- **Sem custo adicional**: Incluído no preço da instância
- **Tipos específicos**: Apenas certas famílias de instância (ex: i3, d2, c5d)

**Comparação EFS vs EBS vs Instance Store:**

| Característica | EFS | EBS | Instance Store |
|----------------|-----|-----|----------------|
| **Compartilhamento** | Múltiplas instâncias | Uma instância | Uma instância |
| **Persistência** | Persistente | Persistente | Temporário |
| **Performance** | Moderada | Alta | Muito Alta |
| **Escalabilidade** | Automática | Manual | Fixo |
| **Uso típico** | Apps distribuídas | Boot volumes | Cache/Buffer |

### 2. Criar Sistema de Arquivos EFS

1. **Acesse o console EFS**:
   - Navegue até **Services > EFS > Create file system**

2. **Configure o sistema de arquivos**:
   - **Name**: `efs-lab-compartilhado`
   - **VPC**: Selecione sua VPC existente
   - **Performance mode**: General Purpose (padrão)
   - **Throughput mode**: Provisioned ou Bursting (escolha Bursting para Free Tier)
   - **Encryption**: Enable encryption at rest (recomendado)

3. **Configure network settings**:
   - **Mount targets**: Verifique se está criando em todas as AZs disponíveis
   - **Security groups**: Será configurado na próxima etapa

4. **Crie o sistema de arquivos**: Click **Create**

5. **Anote o File system ID**: Algo como `fs-1234567890abcdef0`

### 3. Configurar Security Groups para NFS

1. **Crie Security Group para EFS**:
   - **Name**: `sg-efs-lab`
   - **Description**: `Security group para EFS lab`
   - **VPC**: Sua VPC
   - **Inbound rules**:
     - Type: NFS
     - Protocol: TCP
     - Port: 2049
     - Source: Security group das instâncias EC2 (será criado no próximo passo)

2. **Crie Security Group para instâncias EC2**:
   - **Name**: `sg-ec2-efs-client`
   - **Description**: `Security group para instâncias que acessam EFS`
   - **VPC**: Sua VPC
   - **Inbound rules**:
     - Type: SSH
     - Protocol: TCP
     - Port: 22
     - Source: Seu IP
   - **Outbound rules**:
     - Type: NFS
     - Protocol: TCP
     - Port: 2049
     - Destination: Security group do EFS

3. **Atualize o EFS Security Group**:
   - Edite o `sg-efs-lab`
   - Source da regra NFS: `sg-ec2-efs-client`

### 4. Lançar Múltiplas Instâncias EC2

1. **Lance primeira instância**:
   - **Name**: `ec2-efs-client-1`
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t3.micro
   - **Subnet**: Subnet pública na AZ-1a
   - **Security group**: `sg-ec2-efs-client`
   - **User data**:
     ```bash
     #!/bin/bash
     yum update -y
     yum install -y amazon-efs-utils nfs-utils
     mkdir -p /mnt/efs
     ```

2. **Lance segunda instância**:
   - **Name**: `ec2-efs-client-2`
   - **AMI**: Amazon Linux 2023
   - **Instance type**: t3.micro
   - **Subnet**: Subnet pública na AZ-1b (diferente da primeira)
   - **Security group**: `sg-ec2-efs-client`
   - **User data**: Mesmo script da primeira instância

3. **Lance terceira instância** (opcional):
   - **Name**: `ec2-efs-client-3`
   - Configure similarmente em uma terceira AZ se disponível

### 5. Montar EFS nas Instâncias

1. **Conecte-se à primeira instância**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-1
   ```

2. **Verifique se o utilitário EFS está instalado**:
   ```bash
   # Instale se necessário
   sudo yum install -y amazon-efs-utils
   
   # Verifique a instalação
   which mount.efs
   ```

3. **Crie ponto de montagem**:
   ```bash
   sudo mkdir -p /mnt/efs
   ```

4. **Monte o EFS usando DNS name**:
   ```bash
   # Substitua fs-1234567890abcdef0 pelo seu File System ID
   sudo mount -t efs fs-1234567890abcdef0:/ /mnt/efs
   
   # Ou usando mount.efs (recomendado)
   sudo mount -t efs -o tls fs-1234567890abcdef0:/ /mnt/efs
   ```

5. **Verifique a montagem**:
   ```bash
   # Confirme que está montado
   df -h /mnt/efs
   
   # Verifique o tipo de sistema de arquivos
   mount | grep efs
   ```

6. **Configure montagem automática**:
   ```bash
   # Adicione ao /etc/fstab para montagem automática
   echo "fs-1234567890abcdef0.efs.sua-regiao.amazonaws.com:/ /mnt/efs efs defaults,_netdev" | sudo tee -a /etc/fstab
   
   # Teste montagem automática
   sudo umount /mnt/efs
   sudo mount -a
   df -h /mnt/efs
   ```

7. **Repita o processo nas outras instâncias**:
   - Conecte-se às instâncias 2 e 3
   - Execute os mesmos comandos de montagem

### 6. Testar Compartilhamento de Arquivos

1. **Na instância 1, crie estrutura de arquivos**:
   ```bash
   # Crie diretórios de teste
   sudo mkdir -p /mnt/efs/projetos
   sudo mkdir -p /mnt/efs/backups
   sudo mkdir -p /mnt/efs/logs
   
   # Crie arquivo de identificação da instância
   echo "Arquivo criado pela instância 1 em $(date)" | sudo tee /mnt/efs/instancia1.txt
   
   # Crie arquivo de projeto compartilhado
   sudo tee /mnt/efs/projetos/config-app.json << 'EOF'
   {
     "app_name": "Sistema Compartilhado",
     "version": "1.0",
     "database": {
       "host": "db.exemplo.com",
       "port": 5432
     },
     "created_by": "instancia-1",
     "created_at": "TIMESTAMP_PLACEHOLDER"
   }
   EOF
   
   # Substitua o placeholder
   sudo sed -i "s/TIMESTAMP_PLACEHOLDER/$(date -Iseconds)/" /mnt/efs/projetos/config-app.json
   ```

2. **Na instância 2, verifique e modifique arquivos**:
   ```bash
   # Conecte-se à instância 2
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-2
   
   # Verifique se vê os arquivos da instância 1
   ls -la /mnt/efs/
   cat /mnt/efs/instancia1.txt
   
   # Crie arquivo da instância 2
   echo "Arquivo criado pela instância 2 em $(date)" | sudo tee /mnt/efs/instancia2.txt
   
   # Modifique o arquivo compartilhado
   echo "Log da instância 2: $(date) - Configuração lida com sucesso" | sudo tee -a /mnt/efs/logs/sistema.log
   
   # Adicione entrada ao config compartilhado
   sudo sed -i 's/"created_by": "instancia-1"/"created_by": "instancia-1", "modified_by": "instancia-2"/' /mnt/efs/projetos/config-app.json
   ```

3. **Na instância 3 (se existir), teste escrita simultânea**:
   ```bash
   # Conecte-se à instância 3
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia-3
   
   # Verifique arquivos das outras instâncias
   ls -la /mnt/efs/
   cat /mnt/efs/instancia1.txt
   cat /mnt/efs/instancia2.txt
   
   # Crie arquivo de log em tempo real
   echo "Instância 3 iniciada: $(date)" | sudo tee -a /mnt/efs/logs/sistema.log
   
   # Simule monitoramento em tempo real
   sudo tail -f /mnt/efs/logs/sistema.log &
   ```

4. **Teste sincronização em tempo real**:
   ```bash
   # Em qualquer instância, adicione logs
   echo "Teste de sincronização: $(date)" | sudo tee -a /mnt/efs/logs/sistema.log
   
   # Veja aparecer instantaneamente nas outras instâncias
   # (se estiver executando tail -f)
   ```

### 7. Testar Performance e Limitações

1. **Teste performance básica**:
   ```bash
   # Teste velocidade de escrita
   time sudo dd if=/dev/zero of=/mnt/efs/teste-performance.bin bs=1M count=100
   
   # Teste velocidade de leitura
   time sudo dd if=/mnt/efs/teste-performance.bin of=/dev/null bs=1M
   
   # Compare com armazenamento local
   time sudo dd if=/dev/zero of=/tmp/teste-local.bin bs=1M count=100
   ```

2. **Teste comportamento com múltiplos acessos**:
   ```bash
   # Em múltiplas instâncias simultaneamente, execute:
   sudo dd if=/dev/zero of=/mnt/efs/teste-simultaneo-$(hostname).bin bs=1M count=50
   ```

### 8. Entender Instance Store (Teórico e Prático)

**Conceitos teóricos do Instance Store:**

1. **Quando usar Instance Store**:
   - Cache de aplicações
   - Buffers temporários
   - Dados de processamento intermediário
   - Sistemas de arquivos temporários para big data

2. **Limitações críticas**:
   - Dados perdidos em stop/terminate
   - Dados perdidos em falha de hardware
   - Não pode ser detached/attached
   - Tamanho fixo baseado no tipo de instância

3. **Tipos de instância com Instance Store**:
   - **i3/i4i**: Storage-optimized com NVMe SSD
   - **d2/d3**: Dense storage com HDD
   - **c5d/m5d/r5d**: Compute/memory-optimized com SSD local

**Demonstração prática (se possível):**

Se você quiser testar Instance Store real, lance uma instância i3.large (custa mais, mas demonstra o conceito):

```bash
# Em uma instância com Instance Store
lsblk
# Verá dispositivos nvme0n1, nvme1n1, etc.

# Formate e monte
sudo mkfs.ext4 /dev/nvme1n1
sudo mkdir /mnt/instance-store
sudo mount /dev/nvme1n1 /mnt/instance-store

# Teste performance
time sudo dd if=/dev/zero of=/mnt/instance-store/teste.bin bs=1M count=1000
# Performance será muito superior ao EFS
```

### 9. Configurar Montagem Automática do EFS

1. **Configure montagem no boot**:
   ```bash
   # Adicione ao fstab em todas as instâncias
   echo "fs-1234567890abcdef0.efs.sua-regiao.amazonaws.com:/ /mnt/efs efs defaults,_netdev,iam" | sudo tee -a /etc/fstab
   ```

2. **Teste reinicialização**:
   ```bash
   # Reinicie uma instância
   sudo reboot
   
   # Após reinicializar, verifique se EFS foi montado automaticamente
   df -h /mnt/efs
   ```

### 10. Limpeza de Recursos

1. **Desmonte EFS de todas as instâncias**:
   ```bash
   # Em cada instância
   sudo umount /mnt/efs
   
   # Remova do fstab
   sudo sed -i '/efs/d' /etc/fstab
   ```

2. **Termine todas as instâncias EC2**:
   - Selecione todas as instâncias criadas
   - **Instance State > Terminate Instance**

3. **Delete o sistema de arquivos EFS**:
   - Acesse **EFS > File systems**
   - Selecione `efs-lab-compartilhado`
   - **Actions > Delete**

4. **Delete Security Groups**:
   - Delete `sg-efs-lab`
   - Delete `sg-ec2-efs-client`

## ✅ Conclusão

Você dominou os conceitos e uso prático do EFS e Instance Store:

**✅ Checklist de Conquistas:**
- [ ] Conceitos fundamentais do EFS compreendidos
- [ ] Sistema de arquivos EFS criado e configurado
- [ ] Security Groups para NFS configurados corretamente
- [ ] Múltiplas instâncias EC2 lançadas em AZs diferentes
- [ ] EFS montado em múltiplas instâncias simultaneamente
- [ ] Compartilhamento de arquivos em tempo real testado
- [ ] Performance do EFS avaliada e comparada
- [ ] Conceitos do Instance Store compreendidos
- [ ] Montagem automática configurada
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Shared storage**: EFS permite acesso simultâneo entre instâncias
* **NFS protocol**: Sistema de arquivos de rede padrão Linux
* **Cross-AZ durability**: Replicação automática para alta disponibilidade
* **Performance modes**: General Purpose vs Max I/O para diferentes workloads
* **Temporary storage**: Instance Store para performance máxima temporária
* **Use case selection**: Quando usar EFS vs EBS vs Instance Store
