## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 2.3: AMIs Personalizadas - Criando Templates de Instância EC2

## 🎯 Objetivo

Dominar a criação e uso de AMIs (Amazon Machine Images) personalizadas para padronizar deployments, acelerar provisionamento de instâncias e garantir consistência de configurações em ambientes de produção. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Instâncias t2.micro/t3.micro incluídas no Free Tier (750 horas/mês por 12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * AMIs geram snapshots EBS que são cobrados por armazenamento
> * Instâncias criadas a partir de AMIs são cobradas normalmente
> * AMIs compartilhadas podem gerar transferência de dados
> * Sempre **delete AMIs e snapshots não utilizados** ao final do exercício

## ⭐ Passos a Executar

### 1. Entender Conceitos Fundamentais de AMIs

**O que são AMIs?**

AMIs (Amazon Machine Images) são templates pré-configurados que contêm o sistema operacional, aplicações, configurações e dados necessários para lançar instâncias EC2 idênticas. Funcionam como "moldes" para criação rápida e consistente de servidores.

**Componentes de uma AMI:**
- **Root volume template**: Sistema operacional e configurações
- **Launch permissions**: Quem pode usar a AMI
- **Block device mapping**: Configuração de volumes anexados
- **Metadata**: Informações sobre arquitetura, virtualização, etc.

**Tipos de AMI por propriedade:**
- **AWS AMIs**: Fornecidas pela Amazon (Amazon Linux, Ubuntu, Windows)
- **Marketplace AMIs**: Vendidas por terceiros no AWS Marketplace
- **Community AMIs**: Compartilhadas pela comunidade
- **Custom AMIs**: Criadas por você a partir de instâncias configuradas

**Analogias para facilitar o entendimento:**
- **AMI**: Como um "molde de bolo" - sempre produz o mesmo resultado
- **Golden Image**: Como uma "foto da configuração perfeita"
- **Template**: Como um "modelo de documento" que você reutiliza

### 2. Criar Instância Base com Configurações Personalizadas

1. **Lance uma instância EC2 base**:
   - Acesse **EC2 > Launch Instance**
   - **Nome**: `ami-base-webserver`
   - **AMI**: Amazon Linux 2023 (Free Tier eligible)
   - **Tipo**: t3.micro
   - **Key pair**: Selecione ou crie um novo
   - **Network settings**: 
     - VPC: Sua VPC existente
     - Subnet: Uma subnet pública
     - Auto-assign public IP: Enable
   - **Security Group**: Crie um novo:
     - Name: `sg-webserver-ami`
     - Rules: SSH (22) e HTTP (80) do seu IP
   - **Storage**: 10 GiB gp3

2. **Conecte-se via SSH**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   ```

3. **Configure um servidor web completo**:
   ```bash
   # Atualize o sistema
   sudo yum update -y
   
   # Instale Apache, PHP e ferramentas úteis
   sudo yum install -y httpd php php-mysqli htop git
   
   # Habilite e inicie o Apache
   sudo systemctl enable httpd
   sudo systemctl start httpd
   
   # Verifique o status
   sudo systemctl status httpd
   ```

4. **Crie aplicação web personalizada**:
   ```bash
   # Crie página inicial personalizada
   sudo tee /var/www/html/index.php << 'EOF'
   <!DOCTYPE html>
   <html>
   <head>
       <title>Servidor AMI Personalizada</title>
       <style>
           body { font-family: Arial; margin: 40px; background: #f0f0f0; }
           .container { background: white; padding: 20px; border-radius: 10px; }
           .info { background: #e7f3ff; padding: 10px; margin: 10px 0; border-radius: 5px; }
       </style>
   </head>
   <body>
       <div class="container">
           <h1>🚀 Servidor Web - AMI Personalizada v1.0</h1>
           <div class="info">
               <strong>Servidor:</strong> <?php echo gethostname(); ?><br>
               <strong>IP Local:</strong> <?php echo $_SERVER['SERVER_ADDR']; ?><br>
               <strong>Data/Hora:</strong> <?php echo date('Y-m-d H:i:s'); ?><br>
               <strong>Zona AZ:</strong> <?php echo file_get_contents('http://169.254.169.254/latest/meta-data/placement/availability-zone'); ?>
           </div>
           <h2>Aplicações Instaladas:</h2>
           <ul>
               <li>✅ Apache HTTP Server</li>
               <li>✅ PHP Runtime</li>
               <li>✅ MySQL Client</li>
               <li>✅ Ferramentas de Sistema (htop, git)</li>
           </ul>
           <p><em>Esta instância foi criada a partir de uma AMI personalizada!</em></p>
       </div>
   </body>
   </html>
   EOF
   ```

5. **Crie script de informações do sistema**:
   ```bash
   # Script para demonstrar configurações pré-instaladas
   sudo tee /var/www/html/info.php << 'EOF'
   <?php
   echo "<h2>Informações do Sistema</h2>";
   echo "<pre>";
   echo "Versão PHP: " . phpversion() . "\n";
   echo "Versão Apache: " . apache_get_version() . "\n";
   echo "Sistema: " . php_uname() . "\n";
   echo "Uptime: " . shell_exec('uptime') . "\n";
   echo "Espaço em disco:\n" . shell_exec('df -h') . "\n";
   echo "</pre>";
   ?>
   EOF
   ```

6. **Configure configurações personalizadas do sistema**:
   ```bash
   # Configurações personalizadas do Apache
   sudo tee -a /etc/httpd/conf/httpd.conf << 'EOF'
   
   # Configurações personalizadas AMI
   ServerTokens Prod
   ServerSignature Off
   EOF
   
   # Reinicie Apache para aplicar configurações
   sudo systemctl restart httpd
   ```

7. **Teste a configuração**:
   ```bash
   # Teste local
   curl http://localhost
   
   # Verifique logs
   sudo tail -f /var/log/httpd/access_log &
   ```

8. **Acesse via navegador**: http://ip-publico-instancia
   - Teste também: http://ip-publico-instancia/info.php

### 3. Preparar Instância para Criação de AMI

1. **Limpe logs e dados temporários**:
   ```bash
   # Limpe logs do sistema
   sudo find /var/log -type f -name "*.log" -exec truncate -s 0 {} \;
   
   # Limpe histórico bash
   history -c && history -w
   
   # Limpe cache do yum
   sudo yum clean all
   
   # Limpe arquivos temporários
   sudo rm -rf /tmp/*
   sudo rm -rf /var/tmp/*
   ```

2. **Remova dados sensíveis (se houver)**:
   ```bash
   # Remova chaves SSH temporárias (mantenha as autorizadas)
   # sudo rm -f /home/ec2-user/.ssh/id_rsa*
   
   # Remova histórico de comandos sensíveis se houver
   unset HISTFILE
   ```

### 4. Criar AMI Personalizada

1. **Pare a instância para garantir consistência**:
   - No console EC2, selecione a instância `ami-base-webserver`
   - **Instance State > Stop Instance**
   - Aguarde o estado `Stopped`

> 💡 Parar a instância antes de criar a AMI garante que todos os dados estejam salvos e consistentes.

2. **Crie a AMI personalizada**:
   - Com a instância parada e selecionada
   - **Actions > Image and templates > Create Image**
   - **Image name**: `webserver-apache-php-v1.0`
   - **Image description**: `Servidor web com Apache, PHP e configurações personalizadas - Versão 1.0`
   - **No reboot**: Deixe desmarcado (instância já está parada)
   - **Instance volumes**: Verifique as configurações do volume root
   - **Tags**: 
     - Key: `Name`, Value: `AMI-WebServer-v1.0`
     - Key: `Environment`, Value: `template`
     - Key: `Version`, Value: `1.0`
   - **Create Image**

3. **Monitore o progresso da criação**:
   - Acesse **EC2 > Images > AMIs**
   - Verifique o status: `pending` → `available`
   - Anote o AMI ID para referência

4. **Verifique snapshots criados**:
   - Acesse **EC2 > Elastic Block Store > Snapshots**
   - Observe que foi criado um snapshot do volume root

### 5. Testar AMI com Novas Instâncias

1. **Lance instância a partir da AMI personalizada**:
   - Acesse **EC2 > Images > AMIs**
   - Selecione `webserver-apache-php-v1.0`
   - **Launch instance from AMI**
   - **Nome**: `webserver-from-ami-01`
   - **Instance type**: t3.micro
   - **Key pair**: Mesmo usado anteriormente
   - **Network**: Subnet pública, IP público habilitado
   - **Security Group**: Selecione `sg-webserver-ami` existente
   - **Launch Instance**

2. **Lance segunda instância para teste de consistência**:
   - Repita o processo com:
   - **Nome**: `webserver-from-ami-02`
   - Demais configurações iguais

3. **Teste as instâncias criadas**:
   ```bash
   # Teste ambas as instâncias via browser
   # http://ip-instancia-01
   # http://ip-instancia-02
   
   # Ou teste via curl se preferir
   curl http://ip-instancia-01
   curl http://ip-instancia-02
   ```

4. **Verifique consistência das configurações**:
   - Acesse http://ip-instancia-01/info.php
   - Acesse http://ip-instancia-02/info.php
   - Compare as informações - devem ser idênticas exceto hostname e IPs

### 6. Explorar Funcionalidades Avançadas

1. **Compartilhar AMI com outra conta (simulação)**:
   - Selecione sua AMI
   - **Actions > Edit AMI permissions**
   - **Private**: Manter selecionado para este lab
   - **Public**: Não marque (apenas para demonstração)
   - **AWS Account IDs**: Onde você adicionaria IDs de outras contas

2. **Copiar AMI para outra região**:
   - Selecione sua AMI
   - **Actions > Copy AMI**
   - **Destination region**: Escolha uma região diferente
   - **Name**: `webserver-apache-php-v1.0-backup`
   - **Description**: `Backup cross-region da AMI webserver`
   - **Copy AMI**

3. **Verificar versioning**:
   - Simule evolução criando versão 2.0
   - Inicie uma instância, adicione nova funcionalidade
   - Crie nova AMI: `webserver-apache-php-v2.0`

### 7. Gerenciar Lifecycle das AMIs

1. **Organize AMIs com tags**:
   - Acesse **EC2 > AMIs**
   - Adicione tags para organização:
     - `Environment`: `production`, `staging`, `development`
     - `Version`: `1.0`, `2.0`, etc.
     - `Application`: `webserver`, `database`, etc.
     - `Owner`: Seu nome ou equipe

2. **Monitore uso e custos**:
   - As AMIs geram custos pelos snapshots EBS
   - Use Cost Explorer para monitorar custos de armazenamento
   - Considere políticas de retenção para AMIs antigas

### 8. Limpeza de Recursos

1. **Termine as instâncias de teste**:
   - Selecione `webserver-from-ami-01` e `webserver-from-ami-02`
   - **Instance State > Terminate Instance**

2. **Termine a instância base**:
   - Selecione `ami-base-webserver`
   - **Instance State > Terminate Instance**

3. **Delete AMIs criadas (opcional)**:
   - **AMI principal**: Mantenha se quiser usar depois
   - **AMI cross-region**: Delete se criou para teste
   - Actions > Deregister AMI

4. **Delete snapshots associados**:
   - Acesse **EC2 > Snapshots**
   - Delete snapshots das AMIs removidas (se deregistrou)

## ✅ Conclusão

Você dominou a criação e gerenciamento de AMIs personalizadas:

**✅ Checklist de Conquistas:**
- [ ] Conceitos fundamentais de AMIs compreendidos
- [ ] Instância base configurada com aplicações personalizadas
- [ ] Servidor web com Apache e PHP configurado
- [ ] Instância preparada adequadamente para criação de AMI
- [ ] AMI personalizada criada com sucesso
- [ ] Múltiplas instâncias lançadas a partir da AMI
- [ ] Consistência entre instâncias verificada
- [ ] Funcionalidades avançadas exploradas (compartilhamento, cópia)
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **Golden Images**: Template padronizado para deployments
* **Consistency**: Garantia de configurações idênticas
* **Scalability**: Rápido provisionamento de instâncias padronizadas
* **Cross-region backup**: Disaster recovery e distribuição geográfica
* **Versioning**: Controle de evolução de configurações
* **Cost optimization**: Gerenciamento de snapshots e lifecycle
