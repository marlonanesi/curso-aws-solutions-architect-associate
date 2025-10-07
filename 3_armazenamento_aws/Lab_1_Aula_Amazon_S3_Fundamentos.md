## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# � Lab 1: Fundamentos do Amazon S3 – Armazenamento, Classes e Versionamento

## 🎯 Objetivo

Explorar os fundamentos do **Amazon S3**, criando um bucket, armazenando objetos, compreendendo as **classes de armazenamento** e ativando o **versionamento** para controle de versões dos arquivos. **Nível: Básico**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> Este laboratório está dentro do Free Tier tradicional (12 meses).
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo baixo seguindo o lab e lembrando de desprovisionar/excluir depois de finalizar a atividade prática, se quiser aprofundar mais em custos acesse a calculadora AWS para precisar melhor e sempre lembrar de desprovisionar para evitar extrapolar seus créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * Uploads e downloads excessivos ou arquivos muito grandes podem gerar custos
> * Classes como Glacier e One Zone-IA têm características específicas de recuperação
> * Sempre **remova recursos** ao final do exercício

## Passo 1: Acessar o Serviço Amazon S3

1. Acesse o **console AWS** e procure por **S3**
2. O painel centraliza todas as operações de buckets e objetos – o **Guarda-Volumes da Nuvem** da AWS

## Passo 2: Criar um Bucket (Nosso Guarda-Volumes)

1. Clique em **Criar bucket**
2. Defina um nome único globalmente: `meu-guarda-volumes-condominio-2025-seunome`
3. Escolha a **região AWS** desejada: `us-east-1`
4. Configure as seguintes opções:
   - **ACLs**: `Desabilitadas (Recomendado)`
   - **Bloquear todo o acesso público**: `Ativado`
   - **Versionamento**: `Desativado` (ativaremos depois)
   - **Criptografia**: `SSE-S3` (padrão)
5. Adicione uma tag:
   - **Nome**: `GuardaVolumesCondominio`
6. Clique em **Criar bucket**

> � **Essas configurações seguem as boas práticas** de segurança e organização na AWS

## Passo 3: Upload de Objetos (Guardando Pacotes)

1. Acesse o bucket recém-criado
2. Clique em **Fazer upload**
3. Adicione um arquivo pequeno local (qualquer tipo)
4. Na seção **Propriedades**, confirme:
   - **Classe de armazenamento**: `S3 Standard`
   - **Criptografia**: `SSE-S3` (padrão)
5. Clique em **Fazer upload**

> � **Esse processo demonstra** a capacidade do S3 de armazenar arquivos com segurança e performance

## Passo 4: Conhecer as Classes de Armazenamento

### Principais Classes:

- **S3 Standard**
  - Alta performance e disponibilidade (99.99%)
  - Redundância em múltiplas AZs

- **S3 Intelligent-Tiering**
  - Otimiza automaticamente entre acessos frequentes e infrequentes

- **S3 Standard-IA** (Infrequent Access)
  - Menor custo de armazenamento com taxa para leitura

- **S3 One Zone-IA**
  - Armazenamento em uma única AZ (sem redundância)
  - ⚠️ **Cuidado com a resiliência** — pegadinha comum em provas!

- **S3 Glacier / Deep Archive**
  - Retenção de longo prazo
  - Recuperação lenta: minutos (Glacier) ou até 12h (Deep Archive)

> � **A escolha correta da classe** reduz custos e melhora a eficiência do armazenamento

## Passo 5: Ativar o Versionamento

1. Volte para o bucket → aba **Propriedades**
2. Encontre a seção **Versionamento do bucket**
3. Clique em **Editar** → Selecione **Habilitar** → **Salvar alterações**

> � **O versionamento protege** contra sobrescritas e exclusões acidentais

## Passo 6: Testar o Versionamento

1. Faça upload novamente de um arquivo com o **mesmo nome** do anterior
2. Acesse a aba **Objetos** do bucket
3. Habilite **Mostrar versões** (canto superior direito)
4. Observe que agora há **múltiplas versões** do mesmo objeto

> � **Cada versão possui um ID único** e pode ser restaurada individualmente — ideal para auditoria, rollback e rastreabilidade

## ✅ Conclusão

Ao final deste laboratório você:

- [x] Criou e configurou um bucket S3 com boas práticas de segurança
- [x] Armazenou arquivos com diferentes classes de armazenamento
- [x] Compreendeu as diferenças entre classes Standard, IA, One Zone-IA e Glacier
- [x] Ativou e testou o versionamento para proteção de dados
- [x] Explorou conceitos fundamentais do Amazon S3

> 🌟 **Este laboratório cobre os fundamentos** mais importantes do Amazon S3, tanto para a certificação quanto para o uso profissional em nuvem
