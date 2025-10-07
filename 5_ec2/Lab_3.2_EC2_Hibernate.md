## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab 3.2: EC2 Hibernate - Otimização de Custos

## 🎯 Objetivo

Explorar o recurso EC2 Hibernate para otimização de custos em workloads intermitentes, preservando estado da memória entre sessões e reduzindo tempo de inicialização de aplicações. **Nível: Intermediário**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Instâncias com Hibernate requerem tipos maiores (m5.large+) que NÃO estão no Free Tier.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo moderado para instâncias m5.large ($0.096/hora), mas com potencial economia significativa através da hibernação. Sempre lembrar de hibernar ou desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Hibernate requer instâncias de tipos específicos (não Free Tier)
> * Volume EBS deve ser criptografado e maior que a RAM
> * Instância hibernada ainda gera custos de armazenamento EBS
> * Limite de 60 dias contínuos de hibernação
> * Sempre **termine instâncias** se não precisar mais usar

## ⭐ Passos a Executar

### 1. Entender Conceitos Fundamentais do Hibernate

**O que é EC2 Hibernate?**

EC2 Hibernate permite "pausar" uma instância salvando todo o conteúdo da RAM (memória) no volume EBS root. Quando a instância é reiniciada, ela restaura exatamente o estado anterior, incluindo processos, conexões de rede e dados em memória.

**Como funciona o processo:**
1. **Hibernate**: RAM → Arquivo no EBS → Instância desligada
2. **Resume**: Instância ligada → Arquivo do EBS → RAM restaurada
3. **Continue**: Processos continuam de onde pararam

**Analogias para facilitar o entendimento:**
- **Hibernate**: Como "suspender" um laptop - tudo fica salvo e volta exatamente como estava
- **Stop/Start normal**: Como desligar/ligar um computador - perde todo o estado
- **Arquivo de hibernação**: Como um "save state" de videogame

**Benefícios principais:**
- **Economia de custos**: Sem cobrança de compute durante hibernação
- **Inicialização rápida**: Não reprocessa inicialização de aplicações
- **Continuidade de estado**: Mantém conexões, caches e dados em RAM
- **Flexibilidade**: Liga/desliga conforme demanda

**Limitações importantes:**
- **Tipos de instância**: Apenas famílias compatíveis (M3, M4, M5, C3, C4, C5, R3, R4, R5)
- **Tamanho da RAM**: Máximo 150 GB
- **Volume root**: Deve ser EBS criptografado e >= RAM
- **Tempo limite**: Máximo 60 dias hibernada
- **Sistemas operacionais**: Amazon Linux 2, Ubuntu, Windows

### 2. Preparar Ambiente para Hibernate

1. **Verifique tipos de instância compatíveis**:
   - Famílias suportadas: M3, M4, M5, C3, C4, C5, R3, R4, R5
   - Para este lab: usaremos m5.large (8 GB RAM)

2. **Calcule tamanho necessário do volume root**:
   - RAM da m5.large: 8 GB
   - Volume root mínimo: 8 GB + SO + aplicações
   - Recomendado: 16 GB para margem de segurança

### 3. Criar Instância com Hibernate Habilitado

1. **Lance instância EC2**:
   - Acesse **EC2 > Launch Instance**
   - **Name**: `ec2-hibernate-demo`
   - **AMI**: Amazon Linux 2023 (Free Tier eligible)
   - **Instance type**: `m5.large` ⚠️ (NÃO é Free Tier)
   - **Key pair**: Selecione ou crie um novo

2. **Configure storage com criptografia**:
   - **Volume 1 (Root)**:
     - Size: 16 GiB (maior que RAM de 8GB)
     - Volume type: gp3
     - **Encrypted**: ✅ MARQUE ESTA OPÇÃO (obrigatório para Hibernate)
     - Delete on termination: Yes

3. **Habilite Hibernate**:
   - Expanda **Advanced details**
   - **Stop - Hibernate behavior**: ✅ **Enable**
   - ⚠️ Esta opção só aparece com instâncias compatíveis e volume criptografado

4. **Configure User Data**:
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y htop stress-ng python3 pip
   
   # Instala ferramentas para simular workload
   pip3 install psutil
   
   # Cria script para demonstrar continuidade de estado
   cat > /home/ec2-user/memory_test.py << 'EOF'
   #!/usr/bin/env python3
   import time
   import datetime
   import psutil
   
   # Simula aplicação que mantém estado na memória
   print("🚀 Aplicação iniciada:", datetime.datetime.now())
   
   # Cria dados em memória
   memory_data = {}
   for i in range(100000):
       memory_data[f"key_{i}"] = f"valor_importante_{i}"
   
   print(f"📊 Dados carregados em memória: {len(memory_data)} registros")
   print(f"💾 Uso de RAM: {psutil.virtual_memory().percent}%")
   
   # Loop contínuo para demonstrar estado
   counter = 0
   while True:
       counter += 1
       print(f"⏰ {datetime.datetime.now()} - Contador: {counter} - RAM: {psutil.virtual_memory().percent}%")
       time.sleep(30)
   EOF
   
   chmod +x /home/ec2-user/memory_test.py
   chown ec2-user:ec2-user /home/ec2-user/memory_test.py
   ```

5. **Configure Security Group**:
   - **Name**: `sg-hibernate-demo`
   - **Rules**: SSH (22) do seu IP

6. **Lance a instância**: Click **Launch Instance**

### 4. Simular Aplicação com Estado

1. **Conecte-se à instância**:
   ```bash
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   ```

2. **Verifique configuração de hibernação**:
   ```bash
   # Verifique se swap está configurado (necessário para hibernate)
   free -h
   
   # Verifique se hibernação está habilitada
   cat /sys/power/state
   # Deve mostrar: freeze mem disk
   
   # Verifique espaço em disco
   df -h
   ```

3. **Inicie aplicação de teste**:
   ```bash
   # Execute aplicação em background
   nohup python3 memory_test.py > app.log 2>&1 &
   
   # Verifique se está executando
   ps aux | grep memory_test
   
   # Monitore logs
   tail -f app.log
   ```

4. **Crie mais carga na memória**:
   ```bash
   # Em outro terminal SSH
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   
   # Use stress-ng para simular uso intensivo de RAM
   stress-ng --vm 1 --vm-bytes 2G --timeout 0 &
   
   # Monitore uso de recursos
   htop
   # Ou
   free -h
   watch -n 2 free -h
   ```

5. **Anote estado atual**:
   ```bash
   # Anote o último número do contador
   tail app.log
   
   # Anote processos em execução
   ps aux | grep -E "(memory_test|stress-ng)"
   
   # Anote uso de memória
   free -h
   ```

### 5. Hibernate a Instância

1. **Prepare para hibernação**:
   ```bash
   # Pare de monitorar logs (Ctrl+C se estiver executando tail -f)
   # Mas deixe os processos executando em background
   ```

2. **Hibernate via console AWS**:
   - Acesse **EC2 > Instances**
   - Selecione `ec2-hibernate-demo`
   - **Instance State > Stop Instance**
   - Na caixa de diálogo, confirme que está usando **Hibernate**
   - Clique **Stop**

3. **Monitore o processo**:
   - Estado mudará: `running` → `stopping` → `stopped`
   - Note que pode demorar alguns minutos para hibernar
   - Processo salva 8GB de RAM no volume EBS

4. **Verifique comportamento de cobrança**:
   - Instância hibernada NÃO é cobrada por compute
   - Volume EBS continua sendo cobrado
   - Economia típica: 60-70% dos custos

### 6. Restaurar da Hibernação

1. **Aguarde hibernação completa**:
   - Certifique-se que estado está `stopped`
   - Aguarde pelo menos 2-3 minutos após parar

2. **Restaure a instância**:
   - Selecione `ec2-hibernate-demo`
   - **Instance State > Start Instance**
   - Estado mudará: `stopped` → `pending` → `running`

3. **Conecte-se rapidamente após boot**:
   ```bash
   # Conecte assim que a instância estiver "running"
   ssh -i sua-chave.pem ec2-user@ip-publico-instancia
   ```

4. **Verifique continuidade do estado**:
   ```bash
   # Verifique se processos continuaram
   ps aux | grep -E "(memory_test|stress-ng)"
   
   # Verifique logs - contador deve continuar de onde parou
   tail -20 app.log
   
   # Monitore em tempo real
   tail -f app.log
   
   # Verifique uso de memória
   free -h
   ```

> 💡 O contador deve continuar exatamente do número onde parou antes da hibernação!

### 7. Demonstrar Diferença vs Stop/Start Normal

1. **Termine os processos atuais**:
   ```bash
   # Mate processos de teste
   pkill -f memory_test
   pkill stress-ng
   
   # Confirme que pararam
   ps aux | grep -E "(memory_test|stress-ng)"
   ```

2. **Execute stop/start normal**:
   - No console AWS, **Stop Instance** (normal, não hibernate)
   - Aguarde parar completamente
   - **Start Instance**
   - Conecte-se novamente

3. **Inicie aplicação novamente**:
   ```bash
   # Execute aplicação de novo
   nohup python3 memory_test.py > app_new.log 2>&1 &
   
   # Compare logs
   echo "=== LOG ANTERIOR (hibernate) ==="
   tail -10 app.log
   
   echo "=== LOG NOVO (start normal) ==="
   tail -10 app_new.log
   ```

4. **Observe a diferença**:
   - Após hibernate: contador continuou
   - Após stop/start normal: contador reiniciou do zero

### 8. Testar Funcionalidades Avançadas

1. **Múltiplos ciclos de hibernação**:
   ```bash
   # Execute aplicação com timestamp
   nohup python3 -c "
   import time, datetime
   for i in range(1000):
       print(f'Ciclo {i}: {datetime.datetime.now()}')
       time.sleep(60)
   " > ciclos.log 2>&1 &
   ```

2. **Teste hibernação múltipla**:
   - Hibernate instância
   - Espere 10 minutos
   - Restaure
   - Verifique continuidade
   - Repita 2-3 vezes

3. **Simule workload real**:
   ```bash
   # Simule cache de aplicação
   python3 -c "
   import time
   import datetime
   
   # Simula cache populado
   cache = {}
   for i in range(50000):
       cache[f'user_{i}'] = {'login': datetime.datetime.now(), 'data': 'sensitive_data'}
   
   print(f'Cache populado com {len(cache)} usuários')
   print('Aplicação pronta para hibernação...')
   
   # Mantém aplicação em execução
   while True:
       print(f'Cache ativo: {len(cache)} usuários - {datetime.datetime.now()}')
       time.sleep(120)
   "
   ```

### 9. Analisar Economia de Custos

1. **Calcule economia potencial**:
   ```bash
   # Custo m5.large (exemplo região us-east-1)
   # On-Demand: ~$0.096/hora
   # 24h executando: $2.30/dia
   # 8h executando + 16h hibernada: $0.77/dia
   # Economia: ~66%
   ```

2. **Cenários ideais para Hibernate**:
   - Ambientes de desenvolvimento (8h/dia)
   - Aplicações batch (execução periódica)
   - Workloads sazonais
   - Aplicações com warm-up longo

### 10. Limpeza de Recursos

1. **Termine processos**:
   ```bash
   # Se conectado à instância, mate processos
   pkill -f python3
   pkill stress-ng
   ```

2. **Termine a instância**:
   - **EC2 > Instances**
   - Selecione `ec2-hibernate-demo`
   - **Instance State > Terminate Instance**

3. **Verifique recursos órfãos**:
   - **EC2 > Volumes**: Volumes devem ser deletados automaticamente
   - **EC2 > Security Groups**: Delete `sg-hibernate-demo` se não estiver em uso

## ✅ Conclusão

Você dominou o uso do EC2 Hibernate para otimização de custos:

**✅ Checklist de Conquistas:**
- [ ] Conceitos fundamentais do Hibernate compreendidos
- [ ] Instância m5.large criada com volume EBS criptografado
- [ ] Hibernate habilitado corretamente na instância
- [ ] Aplicação com estado criada e executada
- [ ] Processo de hibernação executado com sucesso
- [ ] Estado da aplicação preservado após hibernação
- [ ] Diferença entre hibernate e stop/start normal demonstrada
- [ ] Múltiplos ciclos de hibernação testados
- [ ] Economia de custos calculada e analisada
- [ ] Recursos limpos para evitar cobranças

**🎓 Conceitos Reforçados:**
* **State preservation**: Hibernação mantém estado completo da RAM
* **Cost optimization**: Economia de 60-70% em workloads intermitentes
* **Use cases**: Desenvolvimento, batch processing, aplicações sazonais
* **Technical requirements**: Volume criptografado, tipos específicos de instância
* **Limitations**: 60 dias máximo, 150GB RAM máximo, tipos específicos
* **Performance**: Inicialização rápida vs boot completo
