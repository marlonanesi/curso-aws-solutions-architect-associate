[plus] Laboratório Aurora MySQL com Read Replica (Custo Otimizado)

⚠️ Aviso Importante

Este é um laboratório opcional do tipo [plus], voltado a demonstrar o funcionamento do Amazon Aurora MySQL na prática.

Custo: Este lab utiliza recursos fora do Free Tier, podendo gerar cobranças por hora para a instância Aurora e armazenamento. Recomendamos executar, testar e remover os recursos imediatamente após a demonstração.

📋 Objetivo

Criar um cluster Amazon Aurora MySQL com:

Instância Writer (primária)

Instância Reader (Read Replica)

Visualização de endpoints

Explicação da arquitetura e exemplos de uso real

Uso de configurações otimizadas para menor custo possível

✅ Etapa 1: Criar o Cluster Aurora

Navegue até:

Serviço: Amazon RDS > Criar banco de dados

Modo de criação: Padrão

Mecanismo: Amazon Aurora MySQL

Versão: Aurora MySQL 3.x (compatível com MySQL 8)

Modelo:

☑ Produção (para acesso a recursos reais do Aurora)

🔐 Etapa 2: Configurações do Cluster

Identificador: cluster-aurora-condominio

Usuário mestre: admin

Senha: segura (anote!)

Gerenciamento de credenciais: Autogerenciada

Criptografia: Padrão com KMS (aws/rds)

Aurora oferece criptografia em repouso por padrão usando KMS. Ideal para conformidade sem configuração adicional.

📁 Etapa 3: Armazenamento e Instância

Tipo de Armazenamento: Aurora Standard (mais barato)

Classe da instância: db.t3.medium ✅

Tipo: Classes com capacidade de intermitência

Evite I/O-Optimized e instâncias grandes como r6g para não incorrer em altos custos.

Multi-AZ: Não criar (opcional)

🚧 Etapa 4: Rede e Conectividade

VPC: Condominio-Central-VPC

Grupo de sub-redes: (duas subnets em AZs diferentes)

Acesso público: Não

Grupo de segurança: banco-dados-privado-sg (com porta 3306 liberada)

A instância deve estar isolada, mas acessível para testes internos via EC2 ou bastion.

🕵️‍♂️ Etapa 5: Opções Avançadas

RDS Proxy: Não ativar ❌

Encaminhamento de gravação: Não ativar

Etiquetas: Ex: projeto: saa-c03-hands-on

Autenticação do IAM / Kerberos: Não ativar

Monitoring: Database Insights - Padrão

Enhanced Monitoring: Desmarcado

Logs e exportações: Desnecessários neste lab

📈 Etapa 6: Criar a Instância

Clique em Criar banco de dados.Aguarde o provisionamento do cluster e da instância.

🌐 Etapa 7: Visualizar Componentes

Após concluído:

Cluster: cluster-aurora-condominio

Instância: cluster-aurora-condominio-instance-1

Verificar Endpoints:

Endpoint do cluster: para aplicações, redireciona dinamicamente

Endpoint do Writer: exclusivo para operações de escrita

Endpoint do Reader: distribui leitura entre as réplicas

Aurora diferencia endpoints para escrita e leitura, otimizando escalabilidade.

➕ Etapa 8: Adicionar Read Replica

Selecione o cluster

Clique em Ações > Adicionar leitor

Nome: aurora-reader-1

Classe: db.t3.medium

AZ diferente da Writer

Finalize a criação

Ideal para workloads com alto volume de leitura, BI, dashboards, etc.

📄 Exemplos de uso real

Writer: aplicação web ou API realizando inserções no banco

Readers: dashboard de relatórios, sistemas de busca, exportações em massa

Failover: se a Writer cair, uma Reader é promovida automaticamente

❌ Finalização (Evitar Custos)

Excluir:

Cluster Aurora

Instâncias

Snapshots gerados (se houver)

Grupos de sub-rede (opcional)

🌟 Encerramento

"Neste lab opcional, vimos o poder do Amazon Aurora na prática. Criamos um cluster escalável com read replica, entendemos os endpoints e a arquitetura gerenciada da AWS para bancos relacionais.

Este é o primeiro de três labs essenciais sobre bancos de dados: veremos ainda DynamoDB (NoSQL proprietário da AWS) e DocumentDB (NoSQL tradicional), cada um representando um pilar arquitetural importante para o arquiteto de soluções."