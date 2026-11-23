# Análise de Riscos Cibernéticos e Contramedidas de Segurança

**Projeto:** FarmTech Solutions — Safra do Conhecimento Cibernético (Fase 4)  
**Instituição:** FIAP - Faculdade de Informática e Administração Paulista  
**Aluno:** Angelo Guilherme Sfreddo (RM: 566580) — Turma: 1TIAO  

---

## 1. Contexto e Motivação da Segurança no Agronegócio 4.0

À medida que a **FarmTech Solutions** evolui de um sistema de simples leitura de sensores para uma plataforma orientada a dados que automatiza a irrigação por Inteligência Artificial e registra ocorrências fitossanitárias, o sistema se torna um alvo de alto valor para agentes maliciosos:
- **Sabotagem da Produção Agrícola:** Alterar leituras de umidade para induzir o desligamento forçado da bomba de irrigação durante períodos de estiagem, provocando perda irreversível de lavoura;
- **Fraude Sanitária e Reputacional:** Excluir ou adulterar registros de ocorrência de pragas quarentenárias em talhões de exportação;
- **Vazamento de Segredos de Negócio:** Exposição de credenciais de acesso e parâmetros do modelo preditivo em repositórios de código aberto.

---

## 2. Mapeamento de Ativos Críticos

| Ativo | Tipo | Descrição | Requisitos de Segurança |
| :--- | :---: | :--- | :---: |
| **Histórico de Sensores e Telemetria** | Dado | Leituras horárias de umidade, pH e nutrientes da lavoura | Integridade e Disponibilidade |
| **Registros de Ocorrências de Campo** | Dado | Histórico de pragas, geadas e anomalias registradas por operadores | **Integridade (Não-repudiação) e Confidencialidade** |
| **Modelo Preditivo Scikit-Learn** | Aplicação | Artefatos treinados (`.joblib`) que orientam o acionamento da bomba | Integridade e Autenticidade |
| **Credenciais de Banco e Painel** | Segredo | Usuários, senhas e chaves criptográficas de API | **Confidencialidade Estrita** |
| **Painel Interativo Streamlit** | Interface | Ponto central de tomada de decisão do gestor agrícola | Controle de Acesso e Auditoria |

---

## 3. Matriz de Riscos Cibernéticos (Probabilidade vs. Impacto)

| ID | Ameaça / Vetor de Ataque | Vulnerabilidade Explorada | Probabilidade | Impacto | Nível de Risco |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **R01** | **Vazamento de Credenciais no Git** | Chaves e senhas *hardcoded* em scripts enviados ao GitHub | Média | **Crítico** | **ALTO** |
| **R02** | **Acesso Não Autorizado ao Painel** | Ausência de tela de autenticação ou senhas fracas em texto plano | Alta | Alto | **ALTO** |
| **R03** | **Adulteração Clandestina de Ocorrências (Tampering)** | Modificação direta de linhas na base de dados para ocultar pragas | Média | **Crítico** | **ALTO** |
| **R04** | **Injeção de Dados Espúrios via Serial/IoT** | Falta de validação e sanitização nos pacotes enviados ao ESP32 | Média | Médio | **MÉDIO** |
| **R05** | **Falsificação de Decisão da Bomba (Spoofing)** | Manipulação do arquivo `.joblib` para gerar decisões errôneas | Baixa | Alto | **MÉDIO** |

---

## 4. Contramedidas Implementadas e Evidências de Funcionamento

Atendendo rigorosamente às diretrizes do edital da Fase 4, foram implementadas e testadas as seguintes salvaguardas:

### Contramedida 1: Gestão Segura de Segredos Fora do Código
- **Implementação:** Todas as credenciais de banco, segredos de salt e hashes de autenticação foram movidos para o arquivo `.env`, o qual é estritamente ignorado pelo controle de versão no arquivo `.gitignore`.
- **Documentação de Apoio:** Foi disponibilizado o arquivo modelo documentado [`.env.example`](../.env.example), sem conter segredos de produção, permitindo que qualquer membro da equipe instale e configure o ambiente com segurança.
- **Evidência:** O Git não rastreia o arquivo `.env` real, prevenindo a exposição involuntária no GitHub.

---

### Contramedida 2: Controle de Acesso e Autenticação Criptográfica no Streamlit
- **Implementação:** O painel interativo implementa um *gate* de autenticação obrigatório. Nenhuma informação ou gráfico é renderizado antes da validação do usuário e senha.
- **Armazenamento Seguro:** As senhas nunca são armazenadas em texto claro. O sistema utiliza a função criptográfica **SHA-256 com Salt dinâmico** (`gerar_hash_senha()` em `src/security.py`).
- **Credenciais Padrão de Demonstração:**
  - Usuário: `gestor_farmtech`
  - Senha: `farmtech2026`
  - Hash Armazenado: `3a28d48666e6786d973db885dd645df7cd1e6fb14ed337417e3c8a9559f0e08c`
- **Evidência:** Tentativas com senhas erradas disparam alerta na tela e gravam imediatamente um registro de evento com status `FALHA` no log de auditoria.

---

### Contramedida 3: Trilha de Auditoria e Verificação de Integridade por Hash Criptográfico (SHA-256)
- **Implementação:** Para impedir a adulteração clandestina de ocorrências de campo (vetor R03), cada registro inserido na tabela `FT4_OCORRENCIA_CAMPO` recebe uma assinatura criptográfica gerada no momento da gravação:
  $$\text{Hash} = \text{SHA256}(\text{DataHora} \parallel \text{Talhão} \parallel \text{Tipo} \parallel \text{Gravidade} \parallel \text{Observação} \parallel \text{Operador} \parallel \text{Salt})$$
- **Verificação em Tempo Real:** O painel disponibiliza o botão de auditoria que recalcula o hash de cada linha do banco. Se qualquer caractere da observação for alterado diretamente via SQL sem passar pela aplicação, o hash calculado não coincidirá com o hash gravado.

---

## 5. Evidência Prática de Detecção de Adulteração

Para comprovar o funcionamento da contramedida, foi desenvolvido o script de teste automatizado `simular_teste_adulteracao()` em `src/security.py`:

```text
--- INICIANDO TESTE PRÁTICO DE SEGURANÇA: DETECÇÃO DE ADULTERAÇÃO ---
1. Registro criado com ID 5 e Hash SHA-256 legitimo: 470173306dd2a408...
2. Registro ID 5 adulterado clandestinamente no banco de dados!
3. ALERTA DE SEGURANCA: O hash calculado nao coincide com o hash gravado!
   - Hash Gravado no Banco:    470173306dd2...
   - Hash Real Recalculado:    11155a8a5865...
   - STATUS DE INTEGRIDADE:    VIOLADA (REGISTRO CORROMPIDO / ADULTERADO)
```

No painel Streamlit (Módulo 4: Segurança & Auditoria), esse alerta é exibido visualmente em vermelho com o detalhamento do registro comprometido e a notificação de incidente enviada para a tabela `FT4_LOG_SEGURANCA`.

