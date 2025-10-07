## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 2.1: Volumes EBS - Fundamentos de Armazenamento EC2

## 🎯 Objetivo

Explorar os volumes EBS (Elastic Block Store) e dominar os fundamentos do armazenamento persistente no EC2, aprendendo a criar, anexar, formatar e gerenciar volumes EBS com diferentes tipos e estratégias de performance. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> 30 GB de armazenamento EBS (gp2 ou gp3) incluídos no Free Tier (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Volumes EBS são cobrados por GB provisionado, mesmo não usado
> * Volumes órfãos (não anexados) continuam sendo cobrados
> * Snapshots são cobrados por GB armazenado
> * Sempre **remova volumes não utilizados** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender os Conceitos Fundamentais do EBS

**O que é EBS?**

EBS (Elastic Block Store) é como um "HD externo virtual" que você pode conectar às suas instâncias EC2. Diferente do armazenamento local (Instance Store), os dados no EBS persistem mesmo quando a instância é desligada.

**Características principais:**
- **Persistente**: Dados mantidos independente da instância
- **Anexável**: Pode ser conectado/desconectado de instâncias
- **Escalável**: Pode aumentar tamanho e performance
- **Durável**: Replicado automaticamente na AZ
- **Criptografável**: Suporte nativo à criptografia

**Tipos de Volume EBS:**

| Tipo | Nome | Caso de Uso | Performance |
|------|------|-------------|-------------|
| **gp3** | General Purpose SSD v3 | Uso geral, balanceado | 3.000-16.000 IOPS |
| **gp2** | General Purpose SSD v2 | Uso geral (legado) | 100-16.000 IOPS |
| **io1** | Provisioned IOPS SSD v1 | Bancos de dados críticos | Até 64.000 IOPS |
| **io2** | Provisioned IOPS SSD v2 | Apps críticas, maior durabilidade | Até 64.000 IOPS |
| **st1** | Throughput Optimized HDD | Big data, data warehouses | 40-500 MB/s |
| **sc1** | Cold HDD | Arquivos, acesso infrequente | 12-250 MB/s |

> 💡 **gp3** é a escolha padrão para a maioria dos casos - oferece melhor custo-benefício que gp2 e permite ajustar IOPS e throughput independentemente.

### 2. Criar Instância com Volume EBS Personalizado

1. **Acesse o Console EC2**: Navegue até EC2 > Instances > Launch Instance

2. **Configure a instância básica**:
   - **Nome**: `ec2-ebs-demo`
   - **AMI**: Amazon Linux 2023 (Free Tier eligible)
   - **Tipo**: t3.micro
   - **Key pair**: Selecione ou crie um novo
   - **Network settings**: 
     - VPC: Sua VPC existente
     - Subnet: Uma subnet pública
     - Auto-assign public IP: Enable
   - **Security Group**: Crie um novo permitindo SSH (22) do seu IP

3. **Configure armazenamento personalizado**:
   - Na seção "Configure storage"
   - **Volume 1 (Root)**:
     - Size: 10 GiB
     - Volume type: gp3
   - **Adicionar volume**:
     - Size: 8 GiB
     - Volume type: gp3
     - Device name: /dev/sdf

4. **Lance a instância**: Clique em "Launch Instance"

### 3. Verificar Volumes no Console

1. **Acesse EBS Volumes**: EC2 > Elastic Block Store > Volumes

2. **Analise as informações dos volumes criados**:
   - **Volume ID**: Identificador único
   - **Size**: Tamanho em GiB
   - **Volume type**: Tipo do volume (gp3)
   - **State**: Estado (in-use, available)
   - **Attached instances**: Instância anexada

> 💡 Volumes EBS existem independentemente das instâncias. Você pode ver todos os volumes, anexados ou não.

### 4. Trabalhar com Volumes na Instância

1. **Conecte-se via SSH**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   ```

2. **Verifique volumes disponíveis**:
   ```bash
   # Lista dispositivos de bloco
   lsblk
   
   # Informações detalhadas sobre dispositivos
   sudo fdisk -l
   
   # Uso de espaço atual
   df -h
   ```

3. **Formate o volume adicional**:
   ```bash
   # Verifique se o volume tem sistema de arquivos
   sudo file -s /dev/xvdf
   
   # Formate o volume com ext4
   sudo mkfs -t ext4 /dev/xvdf
   
   # Verifique a formatação
   sudo file -s /dev/xvdf
   ```

4. **Monte o volume**:
   ```bash
   # Crie um ponto de montagem
   sudo mkdir /mnt/dados
   
   # Monte o volume
   sudo mount /dev/xvdf /mnt/dados
   
   # Verifique se foi montado
   df -h
   lsblk
   ```

5. **Teste o volume**:
   ```bash
   # Crie um arquivo de teste
   sudo touch /mnt/dados/teste.txt
   echo "Volume EBS funcionando!" | sudo tee /mnt/dados/teste.txt
   
   # Verifique o conteúdo
   cat /mnt/dados/teste.txt
   
   # Verifique espaço disponível
   df -h /mnt/dados
   ```

### 5. Configurar Montagem Automática

1. **Obtenha o UUID do volume**:
   ```bash
   sudo blkid /dev/xvdf
   # Anote o UUID retornado
   ```

2. **Configure montagem automática**:
   ```bash
   # Faça backup do fstab
   sudo cp /etc/fstab /etc/fstab.backup
   
   # Adicione entrada para montagem automática
   echo "UUID=seu-uuid-aqui /mnt/dados ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
   ```

3. **Teste a configuração**:
   ```bash
   # Desmonte o volume
   sudo umount /mnt/dados
   
   # Teste montagem automática
   sudo mount -a
   
   # Verifique se foi montado
   df -h /mnt/dados
   ```

### 6. Gerenciar Volumes EBS

1. **Crie um novo volume via console**:
   - EC2 > Volumes > Create volume
   - **Volume type**: gp3
   - **Size**: 5 GiB
   - **Availability Zone**: Mesma da instância
   - **Tags**: Name = `volume-extra-demo`

2. **Anexe o volume à instância**:
   - Selecione o volume recém-criado
   - Actions > Attach volume
   - **Instance**: Selecione `ec2-ebs-demo`
   - **Device name**: /dev/sdg

3. **Configure o novo volume na instância**:
   ```bash
   # Verifique se apareceu
   lsblk
   
   # Formate e monte
   sudo mkfs -t ext4 /dev/xvdg
   sudo mkdir /mnt/extra
   sudo mount /dev/xvdg /mnt/extra
   
   # Teste
   echo "Volume extra funcionando!" | sudo tee /mnt/extra/teste.txt
   ```

### 7. Modificar Volumes EBS

1. **Aumente o tamanho do volume via console**:
   - EC2 > Volumes
   - Selecione o volume de dados (8 GiB)
   - Actions > Modify volume
   - **Size**: 12 GiB
   - Modify

2. **Estenda o sistema de arquivos na instância**:
   ```bash
   # Verifique o novo tamanho
   lsblk
   
   # Estenda o sistema de arquivos
   sudo resize2fs /dev/xvdf
   
   # Verifique o resultado
   df -h /mnt/dados
   ```

> 💡 Modificar volume EBS é feito online (sem parar a instância). Você pode aumentar tamanho, IOPS e throughput. Não é possível diminuir o tamanho.

### 8. Monitorar Performance

1. **Teste performance básica**:
   ```bash
   # Teste de escrita
   sudo dd if=/dev/zero of=/mnt/dados/testfile bs=1M count=100
   
   # Teste de leitura
   sudo dd if=/mnt/dados/testfile of=/dev/null bs=1M
   
   # Limpe o arquivo de teste
   sudo rm /mnt/dados/testfile
   ```

2. **Monitore IOPS via CloudWatch**:
   - CloudWatch > Metrics > EC2 > EBS
   - Métricas importantes:
     - VolumeReadOps/VolumeWriteOps
     - VolumeTotalReadTime/VolumeTotalWriteTime
     - VolumeQueueLength

### 9. Limpeza de Recursos

1. **Desmonte volumes**:
   ```bash
   sudo umount /mnt/dados
   sudo umount /mnt/extra
   ```

2. **Termine a instância**:
   - EC2 > Instances
   - Selecione `ec2-ebs-demo`
   - Instance State > Terminate

3. **Delete volumes órfãos**:
   - EC2 > Volumes
   - Delete volumes que não estão mais anexados

## ✅ Conclusão

Você dominou os fundamentos dos volumes EBS e suas estratégias de gerenciamento:

**✅ Checklist de Conquistas:**
- [ ] Conceitos fundamentais do EBS compreendidos
- [ ] Instância EC2 criada com volumes EBS personalizados
- [ ] Volume adicional formatado e montado
- [ ] Montagem automática configurada com /etc/fstab
- [ ] Novo volume criado e anexado dinamicamente
- [ ] Volume modificado (aumento de tamanho) online
- [ ] Performance testada e métricas monitoradas
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **EBS vs Instance Store**: Persistência vs performance temporal
* **Tipos de volumes**: gp3, gp2, io1/io2, st1, sc1 e seus casos de uso
* **Operações de volume**: Criar, anexar, formatar, montar, modificar
* **Montagem automática**: Configuração do /etc/fstab
* **Performance**: IOPS, throughput e monitoramento
* **Melhores práticas**: Separação de dados, backup e segurança
