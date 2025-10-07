## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 2.2: Snapshots EBS - Backup e Recuperação de Dados

## 🎯 Objetivo

Dominar os Snapshots EBS como solução fundamental de backup e recuperação, criando snapshots manuais, simulando perda de dados e executando restaurações point-in-time para garantir continuidade dos negócios. **Nível: Básico**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> 1 GB de snapshots EBS incluído no Free Tier (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Snapshots são cobrados por GB armazenado no S3
> * Snapshots incrementais acumulam custos ao longo do tempo
> * Volumes criados a partir de snapshots são cobrados normalmente
> * Sempre **delete snapshots não utilizados** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender Conceitos Fundamentais de Snapshots

**O que são Snapshots EBS?**

Snapshots são "fotografias" point-in-time dos seus volumes EBS, armazenadas de forma durável no Amazon S3. Funcionam como backup incremental - apenas as mudanças desde o último snapshot são armazenadas.

**Características principais:**
- **Incrementais**: Apenas blocos modificados são salvos
- **Duráveis**: Armazenados no S3 (99.999999999% durabilidade)
- **Regionais**: Podem ser copiados entre regiões
- **Flexíveis**: Podem criar novos volumes ou AMIs
- **Automatizáveis**: Integração com DLM (Data Lifecycle Manager)

**Analogias para facilitar o entendimento:**
- **Snapshot**: Como tirar uma foto do estado atual do seu HD
- **Incremental**: Como salvar apenas as páginas alteradas de um documento
- **Restauração**: Como voltar o computador para um ponto de restauração

### 2. Preparar Ambiente com Dados de Teste

**Pré-requisito**: Tenha uma instância EC2 com volume EBS adicional montado (do lab anterior).

1. **Conecte-se à instância via SSH**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   ```

2. **Crie estrutura de dados de teste**:
   ```bash
   # Crie diretórios de trabalho
   sudo mkdir -p /mnt/dados/documentos
   sudo mkdir -p /mnt/dados/backup
   sudo mkdir -p /mnt/dados/projetos
   ```

3. **Crie arquivos de dados simulados**:
   ```bash
   # Documento crítico
   echo "Relatório financeiro Q1 2025 - CONFIDENCIAL" | sudo tee /mnt/dados/documentos/relatorio-q1.txt
   
   # Configurações de aplicação
   echo "database_host=prod-db.company.com" | sudo tee /mnt/dados/projetos/config.txt
   echo "api_key=sk-1234567890abcdef" | sudo tee -a /mnt/dados/projetos/config.txt
   
   # Log de operações
   echo "$(date): Sistema iniciado com sucesso" | sudo tee /mnt/dados/backup/sistema.log
   echo "$(date): Backup automatico executado" | sudo tee -a /mnt/dados/backup/sistema.log
   ```

4. **Verifique os dados criados**:
   ```bash
   # Liste toda a estrutura
   sudo find /mnt/dados -type f -exec ls -la {} \;
   
   # Verifique conteúdo dos arquivos principais
   cat /mnt/dados/documentos/relatorio-q1.txt
   cat /mnt/dados/projetos/config.txt
   ```

### 3. Criar Snapshot Inicial

1. **Identifique o volume no console**:
   - Acesse **EC2 > Elastic Block Store > Volumes**
   - Localize o volume anexado à sua instância (8-12 GiB)
   - Anote o Volume ID

2. **Crie o snapshot via console**:
   - Selecione o volume de dados
   - Clique em **Actions > Create Snapshot**
   - **Description**: `Backup inicial - dados críticos Q1 2025`
   - **Tags**: 
     - Key: `Name`, Value: `snapshot-dados-iniciais`
     - Key: `Environment`, Value: `lab`
     - Key: `Purpose`, Value: `backup-criticos`
   - Clique em **Create Snapshot**

3. **Monitore o progresso**:
   - Acesse **EC2 > Elastic Block Store > Snapshots**
   - Verifique o status: `pending` → `completed`
   - Anote o Snapshot ID para referência

> 💡 O primeiro snapshot é uma cópia completa do volume. Snapshots subsequentes serão incrementais, copiando apenas blocos modificados.

### 4. Simular Atividade e Modificações

1. **Adicione novos dados**:
   ```bash
   # Simule trabalho adicional
   echo "$(date): Nova entrada de dados" | sudo tee -a /mnt/dados/backup/sistema.log
   echo "Relatório Q2 2025 - EM DESENVOLVIMENTO" | sudo tee /mnt/dados/documentos/relatorio-q2.txt
   
   # Modifique configuração
   echo "new_feature_flag=enabled" | sudo tee -a /mnt/dados/projetos/config.txt
   ```

2. **Crie arquivo grande para simular crescimento**:
   ```bash
   # Simule download ou geração de dados
   sudo dd if=/dev/zero of=/mnt/dados/backup/dados_grandes.bin bs=1M count=50
   ```

3. **Verifique o estado atual**:
   ```bash
   # Veja o uso de espaço
   df -h /mnt/dados
   
   # Liste todos os arquivos
   sudo find /mnt/dados -type f -exec ls -lh {} \;
   ```

### 5. Simular Perda Catastrófica de Dados

1. **"Acidente" - perda de dados críticos**:
   ```bash
   # Simule exclusão acidental de arquivos críticos
   sudo rm -f /mnt/dados/documentos/relatorio-q1.txt
   sudo rm -f /mnt/dados/projetos/config.txt
   
   # Simule corrupção de logs
   echo "SISTEMA CORROMPIDO" | sudo tee /mnt/dados/backup/sistema.log
   ```

2. **Confirme a perda**:
   ```bash
   # Tente acessar arquivos perdidos
   cat /mnt/dados/documentos/relatorio-q1.txt  # Erro esperado
   cat /mnt/dados/projetos/config.txt          # Erro esperado
   
   # Veja o estado dos logs corrompidos
   cat /mnt/dados/backup/sistema.log
   ```

3. **Avalie o impacto**:
   ```bash
   # Veja o que sobrou
   sudo find /mnt/dados -type f -exec ls -la {} \;
   ```

> 💡 Esta simulação representa cenários reais: exclusão acidental, corrupção de dados, ataques de ransomware, ou falhas de hardware.

### 6. Restaurar a partir do Snapshot

1. **Crie volume a partir do snapshot**:
   - Acesse **EC2 > Elastic Block Store > Snapshots**
   - Selecione o snapshot `snapshot-dados-iniciais`
   - Clique em **Actions > Create Volume from Snapshot**
   - **Volume Type**: gp3
   - **Size**: Mantenha o tamanho original
   - **Availability Zone**: Mesma da instância
   - **Tags**: Name = `volume-restaurado-dados`
   - Clique em **Create Volume**

2. **Anexe o volume restaurado à instância**:
   - Acesse **EC2 > Elastic Block Store > Volumes**
   - Selecione o volume recém-criado
   - Clique em **Actions > Attach Volume**
   - **Instance**: Selecione sua instância
   - **Device name**: `/dev/sdh`
   - Clique em **Attach Volume**

3. **Monte o volume restaurado**:
   ```bash
   # Crie ponto de montagem
   sudo mkdir /mnt/restaurado
   
   # Monte o volume restaurado
   sudo mount /dev/xvdh /mnt/restaurado
   
   # Verifique se foi montado
   df -h /mnt/restaurado
   ```

4. **Verifique os dados restaurados**:
   ```bash
   # Confirme que os dados originais estão intactos
   cat /mnt/restaurado/documentos/relatorio-q1.txt
   cat /mnt/restaurado/projetos/config.txt
   cat /mnt/restaurado/backup/sistema.log
   
   # Compare com dados corrompidos
   echo "=== DADOS ORIGINAIS (RESTAURADOS) ==="
   sudo find /mnt/restaurado -type f -exec ls -la {} \;
   
   echo "=== DADOS ATUAIS (CORROMPIDOS) ==="
   sudo find /mnt/dados -type f -exec ls -la {} \;
   ```

### 7. Recuperar Dados Críticos

1. **Copie dados essenciais de volta**:
   ```bash
   # Restaure arquivos críticos
   sudo cp /mnt/restaurado/documentos/relatorio-q1.txt /mnt/dados/documentos/
   sudo cp /mnt/restaurado/projetos/config.txt /mnt/dados/projetos/
   
   # Restaure logs limpos
   sudo cp /mnt/restaurado/backup/sistema.log /mnt/dados/backup/sistema-limpo.log
   ```

2. **Verifique a recuperação**:
   ```bash
   # Confirme que os arquivos estão de volta
   cat /mnt/dados/documentos/relatorio-q1.txt
   cat /mnt/dados/projetos/config.txt
   
   # Compare logs
   echo "=== LOG CORROMPIDO ==="
   cat /mnt/dados/backup/sistema.log
   echo "=== LOG RESTAURADO ==="
   cat /mnt/dados/backup/sistema-limpo.log
   ```

### 8. Explorar Funcionalidades Avançadas

1. **Crie snapshot incremental**:
   - No console, selecione o volume original
   - Actions > Create Snapshot
   - **Description**: `Backup pós-recuperação - incremental`
   - **Tags**: Name = `snapshot-pos-recuperacao`
   - Create Snapshot

2. **Compare tamanhos dos snapshots**:
   - Acesse **EC2 > Snapshots**
   - Compare o **Storage Tier** e **Size** dos snapshots
   - Note que o segundo snapshot é menor (incremental)

3. **Teste cópia entre regiões (opcional)**:
   - Selecione um snapshot
   - Actions > Copy Snapshot
   - **Destination region**: Escolha região diferente
   - **Description**: `Backup cross-region para DR`

### 9. Limpeza de Recursos

1. **Desmonte volumes**:
   ```bash
   sudo umount /mnt/restaurado
   ```

2. **Remova recursos no console**:
   - **Volumes**: Detach e delete o volume restaurado
   - **Snapshots**: Delete todos os snapshots criados no lab
   - **Volumes cross-region**: Delete se criou cópias

3. **Limpe arquivos de teste**:
   ```bash
   # Remova arquivos grandes criados
   sudo rm -f /mnt/dados/backup/dados_grandes.bin
   
   # Opcional: limpe todos os dados de teste
   sudo rm -rf /mnt/dados/documentos/*
   sudo rm -rf /mnt/dados/projetos/*
   sudo rm -rf /mnt/dados/backup/*
   ```

## ✅ Conclusão

Você dominou o uso de Snapshots EBS para backup e recuperação de dados:

**✅ Checklist de Conquistas:**
- [ ] Conceitos de snapshots EBS compreendidos
- [ ] Dados de teste criados em volume EBS
- [ ] Snapshot inicial criado via console
- [ ] Perda catastrófica de dados simulada
- [ ] Volume restaurado a partir de snapshot
- [ ] Dados críticos recuperados com sucesso
- [ ] Snapshots incrementais testados
- [ ] Funcionalidades cross-region exploradas
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Snapshots incrementais**: Apenas blocos modificados são salvos
* **Durabilidade S3**: 99.999999999% de durabilidade dos backups
* **Point-in-time recovery**: Restauração para momento específico
* **Cross-region copying**: Backup para disaster recovery
* **Storage tiers**: Otimização de custos de armazenamento
* **DLM integration**: Automação de políticas de backup
