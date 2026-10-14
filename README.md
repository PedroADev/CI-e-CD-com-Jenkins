# Exercício A2 – Arquitetura CI/CD com Jenkins, Containers e Observabilidade

**Disciplina:** DevOps & QA  
**Pipeline:** V5.1 (Portável Windows/macOS/Linux)  
**Ambiente:** Jenkins LTS 2.580.1, Docker Desktop (Engine 29.8.0), PostgreSQL 17, Prometheus, Grafana, Cypress E2E  

---

## 1. Topologia da Arquitetura e Portas Locais

| Componente | Tipo / Serviço | Porta Local | Descrição |
| :--- | :--- | :--- | :--- |
| **Jenkins LTS** | CI/CD Server | `:9090` | Servidor de automação e orquestração de pipelines |
| **API Spring Boot** | Backend HOMOL | `:8081` | Aplicação Jogo Enigma com métricas Actuator / Prometheus |
| **BFF / Frontend** | Node.js Gateway | `:3000` | Frontend web servido em container |
| **pgAdmin 4** | Database Admin | `:5050` | Interface web para administração do banco PostgreSQL |
| **PostgreSQL 17** | Banco de Dados | `interno:5432` | Banco relacional para ambiente HOMOL |
| **Prometheus** | Observabilidade | `:9091` | Coletor de métricas via `/actuator/prometheus` (Target UP) |
| **Grafana** | Visualização | `:3001` | Dashboard com 4 painéis de monitoramento PromQL |
| **Cypress E2E** | Testes de Sistema | Container | Execução automatizada de testes E2E headless |

![Diagrama de Arquitetura CI/CD e Observabilidade](evidencias/fluxo_ci_cd_obs.png)

---

## 2. Prática 1 – Freestyle CI (Projeto `integracao_v1`)

### 2.1 Configuração do Job
- **Nome do Job:** `A2_P1_integracao_ci`
- **Tipo:** Freestyle Project
- **SCM:** Git local (`file:///C:/Users/pedro/Downloads/integracao_v1/integracao_v1`)
- **Build Steps:** Invocação do Maven com meta `clean verify`
- **Pós-Build Actions:**
  - Publicação de Relatórios de Teste JUnit (`**/target/surefire-reports/*.xml`)
  - Publicação do Relatório de Cobertura JaCoCo (`target/site/jacoco`)

### 2.2 Ciclo de Falha Controlada (Build Vermelho)
- **Alteração induzida:** Modificação na classe `Aluno.java`, invertendo a regra de frequência de `frequencia >= 75` para `frequencia < 75`.
- **Resultado:** O build falhou imediatamente na fase de testes unitários com status vermelho.
- **Evidências salvas:**
  - `evidencias/p1/01_job_configuracao.png`: Tela de configuração do job.
  - `evidencias/p1/02_build_vermelho.png`: Histórico de builds indicando falha (#4).
  - `evidencias/p1/03_console_falha.png`: Console output com falhas nos testes unitários Surefire.
  - `evidencias/p1/04_resultado_junit_falha.png`: Relatório do JUnit no Jenkins destacando o teste reprovado.

### 2.3 Ciclo de Sucesso e Cobertura (Build Verde)
- **Correção:** Regra de negócio restaurada em `Aluno.java` (`frequencia >= 75`) e comitada no Git.
- **Resultado:** Build executado com sucesso total (azul/verde), testes aprovados e relatório JaCoCo publicado.
- **Evidências salvas:**
  - `evidencias/p1/05_build_verde.png`: Histórico de builds com status estável (#5).
  - `evidencias/p1/06_junit_verde.png`: Relatório JUnit indicando 0 falhas e todos os testes passando.
  - `evidencias/p1/07_jacoco_coverage_report_verde.png`: Relatório JaCoCo com cobertura de linhas, branches e instruções.

---

## 3. Prática 2 – Pipeline as Code (Projeto `jogo-enigma`)

### 3.1 Configuração do Pipeline
- **Nome do Job:** `A2_P2_jogo_enigma_pipeline`
- **Tipo:** Pipeline (`workflow-job`)
- **Definição:** Pipeline script from SCM (Git local apontando para `Jenkinsfile` na branch `*/main`)

### 3.2 Execução dos Estágios (V5.1 Portável)
O pipeline executou com sucesso absoluto todos os seus estágios definidos:
1. **0 - Preflight do Ambiente:** Validação do runtime Java (17/26), Docker CLI (29.8.0), Docker Compose e daemon do Docker Engine.
2. **1 - Checkout:** Checkout automatizado do código-fonte via Git SCM.
3. **2 - CI - JUnit + Testcontainers + JaCoCo:** Execução de testes unitários e de integração utilizando container real do PostgreSQL 17 via Testcontainers e geração do relatório JaCoCo.
4. **3 - CI - Qualidade PMD:** Análise estática de código Java via plugin PMD (`pmd.html`).
5. **4 - CI - Package:** Empacotamento do artefato da aplicação Spring Boot em `.jar`.
6. **5 - CD - Build dos Containers:** Criação otimizada das imagens Docker locais para a API (`andprof/jogo-enigma-api`) e para o BFF (`bff`).
7. **6 - Registry - Docker Hub (opcional):** Ignorado por padrão via parâmetro booleano.
8. **7 - CD - Deploy HOMOL:** Orquestração do ambiente com `docker compose down` seguido de `docker compose up -d` subindo PostgreSQL, pgAdmin, API, BFF, Prometheus e Grafana.
9. **8 - CD - Health Check HOMOL:** Validação automática do endpoint `/actuator/health` disparada de dentro do container do BFF pela rede interna do Docker Compose.
10. **9 - CD - Cypress E2E em Container:** Execução completa dos testes ponta a ponta (E2E) via imagem oficial `cypress/included:14.5.4`.
11. **10 - Observabilidade:** Exibição das URLs e portas de acesso aos serviços de telemetria.

### 3.3 Evidências Salvas
- `evidencias/p2/01_job_config.xml`: Configuração do job pipeline exportada em XML.
- `evidencias/p2/02_console_output_build2_success.txt`: Log completo da execução com status final `SUCCESS`.
- `evidencias/p2/03_stage_view_build2_success.json`: Metadados de cada estágio com durações e status.
- `evidencias/p2/04_build_summary_build2_success.json`: Resumo consolidado do build.
- `evidencias/p2/05_stage_view_success.png`: Screenshot do painel **Stage View** no Jenkins com todos os estágios verdes.

---

## 4. Prática 3 – CD, Containers e Observabilidade

### 4.1 Validação dos Serviços em HOMOL
Todos os serviços responderam com HTTP 200 e integridade funcional:
- **API Spring Boot (`http://localhost:8081/actuator/health`):** Retorna `{"status":"UP"}`.
- **BFF / Frontend (`http://localhost:3000`):** Interface web servida com sucesso.
- **Prometheus (`http://localhost:9091/api/v1/targets`):** Target `jogo-enigma-api` ativo com status `health: up` coletando métricas em `/actuator/prometheus`.
- **Grafana (`http://localhost:3001`):** Conectado ao datasource Prometheus (`http://prometheus:9090`).

### 4.2 Evidências Salvas
- `evidencias/p3/00_p3_summary.json`: Resumo dos testes de endpoints.
- `evidencias/p3/01_api_health.json`: Resposta JSON do health check da API.
- `evidencias/p3/02_bff_response.html`: Snapshot da resposta HTML do BFF.
- `evidencias/p3/03_prometheus_targets.json`: Dados dos targets do Prometheus confirmando a API em UP.
- `evidencias/p3/04_prometheus_query_up.json`: Consulta da métrica `up{job="jogo-enigma-api"}` retornando 1.
- `evidencias/p3/05_grafana_health.json`: Health check do Grafana.
- `evidencias/p3/06_grafana_datasources.json`: Configuração do datasource Prometheus no Grafana.
- `evidencias/p3/07_prometheus_targets_up.png`: Screenshot da interface do Prometheus comprovando o target em estado UP.

---

## 5. Fechamento – Dashboard Grafana

### 5.1 Especificação do Dashboard
- **Nome:** `Jogo Enigma – Observabilidade HOMOL`
- **UID:** `jogo-enigma-homol`
- **Painéis configurados:**
  1. **Status da API:** Painel do tipo *Stat* com query PromQL `up{job="jogo-enigma-api"}`, exibindo indicador verde com o texto `UP`.
  2. **Requisições HTTP/s:** Gráfico de série temporal com query PromQL `rate(http_server_requests_seconds_count{job="jogo-enigma-api"}[1m])`.
  3. **Tempo Médio de Resposta:** Gráfico de série temporal calculando a latência média via PromQL:  
     `rate(http_server_requests_seconds_sum{job="jogo-enigma-api"}[1m]) / rate(http_server_requests_seconds_count{job="jogo-enigma-api"}[1m])`.
  4. **Memória JVM – Heap:** Gráfico de série temporal com query PromQL `jvm_memory_used_bytes{job="jogo-enigma-api", area="heap"}` exibindo o consumo em bytes.

### 5.2 Evidências Salvas
- `evidencias/grafana/01_dashboard_completo.png`: Captura de tela do dashboard no Grafana com os 4 painéis operacionais.
- `evidencias/grafana/dashboard.json`: Especificação completa do dashboard exportada em JSON.
- `evidencias/grafana/datasources.json`: Configuração do datasource provisionado.

---

## 6. Gabarito das Perguntas e Análises Teóricas (Para o Documento Oficial)

### 6.1 Prática 1 – Freestyle CI
1. **O que é um job Freestyle no Jenkins e qual sua principal limitação?**  
   *Resposta:* Um job Freestyle é um modelo tradicional de configuração do Jenkins gerenciado inteiramente por interface gráfica (GUI), onde passos de compilação, testes e notificações são configurados em formulários web. Sua principal limitação é a ausência de versionamento junto ao código (não segue o conceito de Pipeline as Code): as configurações residem exclusivamente no servidor Jenkins, inviabilizando revisões por Pull Request, replicação entre ambientes e rastreabilidade histórica via Git.
2. **Por que é fundamental demonstrar tanto o ciclo de falha quanto o ciclo de sucesso em CI?**  
   *Resposta:* A demonstração de ambos os ciclos valida a eficácia do pipeline como um "portão de qualidade" (quality gate). Se o pipeline nunca falhar diante de um defeito no código, ele não cumpre sua função de proteção. A falha controlada comprova que quebras de contrato de negócio são bloqueadas imediatamente, enquanto o sucesso posterior comprova que o código corrigido é liberado com confiabilidade.
3. **Qual é o papel do JaCoCo e por que métricas de cobertura são vitais?**  
   *Resposta:* O JaCoCo (Java Code Coverage) afere quais linhas, ramos condicionais (branches) e instruções foram executadas durante a suíte de testes. Essa métrica é vital porque evidencia áreas cegas e trechos críticos de código desprovidos de testes automatizados, direcionando esforços de QA para mitigar riscos de regressão em produção.
4. **Qual é a diferença entre executar `clean test` e `clean verify` no Maven?**  
   *Resposta:* O comando `clean test` compila o código e executa apenas os testes unitários (fase `test`), sem acionar integrações nem gerar relatórios agregados de cobertura. Já o comando `clean verify` avança por todo o ciclo de vida padrão do Maven até a fase `verify`, executando testes unitários, testes de integração e acionando o goal `jacoco:report`, garantindo a geração consolidada dos relatórios de qualidade.

### 6.2 Prática 2 – Pipeline as Code
1. **Quais são os benefícios do Pipeline as Code (Jenkinsfile) frente ao Freestyle?**  
   *Resposta:* O Jenkinsfile fica versionado no próprio repositório Git junto com o código da aplicação. Isso assegura que qualquer alteração na esteira seja auditável, passe por code review, suporte ramificações de branches e permita que qualquer novo servidor Jenkins recrie o ambiente de build imediatamente sem necessidade de configuração manual em telas web.
2. **O que é o Stage View e como ele auxilia o diagnóstico de falhas?**  
   *Resposta:* O Stage View é a interface visual que decompõe o pipeline em estágios sequenciais lógicos, indicando o tempo de execução e o status de cada fase. Ele permite isolar em segundos a etapa exata em que uma quebra ocorreu (por exemplo, diferenciando uma falha de compilação de uma falha de deploy de container), sem exigir a leitura manual de milhares de linhas de log.
3. **Por que incluir um estágio de Preflight no pipeline?**  
   *Resposta:* O Preflight adota a filosofia *fail-fast*: ele verifica previamente se o agente Jenkins possui acesso ao daemon do Docker, Docker Compose e runtimes necessários antes de disparar processos demorados. Isso impede desperdício de tempo e recursos em compilações que inevitavelmente falhariam em etapas posteriores de containerização.
4. **O que são Testcontainers e qual a vantagem de utilizá-los no Stage de CI?**  
   *Resposta:* Testcontainers é uma biblioteca que instancia containers reais e descartáveis (como um PostgreSQL 17) diretamente a partir dos testes Java. Sua vantagem é erradicar falsos positivos gerados por mocks ou bancos em memória (como H2), testando queries, tipos e comportamentos reais do banco de dados em ambiente idêntico ao de produção.

### 6.3 Prática 3 – Containers e Observabilidade
1. **O que é o endpoint `/actuator/health` e por que ele é crucial em pipelines de CD?**  
   *Resposta:* Trata-se de um endpoint do Spring Boot Actuator que reporta a saúde operacional do serviço e de suas dependências (conexão com banco, espaço em disco, etc.). No CD, ele atua como verificação de prontidão (readiness probe): o pipeline só prossegue para os testes E2E após receber HTTP 200 com status `UP`, assegurando que a aplicação inicializou por completo.
2. **Por que o Health Check foi disparado a partir do container do BFF?**  
   *Resposta:* O comando utilizou a rede interna gerenciada pelo Docker Compose (`http://api:8080/actuator/health`). Essa abordagem elimina qualquer dependência de ferramentas locais do host (como curl, PowerShell ou wget) e testa de forma fidedigna a comunicação e resolução de nomes DNS entre os próprios microserviços na rede virtual.
3. **Como o Prometheus realiza a coleta de métricas e o que significa o target em UP?**  
   *Resposta:* O Prometheus opera via modelo de scraping (pull), realizando requisições HTTP periódicas ao endpoint `/actuator/prometheus` da API. O target apresentar estado `health: up` (métrica `up=1`) atesta que a API está acessível na rede e que o Prometheus obteve sucesso na raspagem e indexação de suas métricas.
4. **O que assegura a integridade de uma esteira completa de CI/CD e Observabilidade?**  
   *Resposta:* A integração contínua e a entrega só são completas quando unem testes estáticos (PMD), testes automatizados com banco real (JUnit/Testcontainers), validação empacotada em container (Docker Compose), validação ponta a ponta (Cypress E2E) e telemetria contínua em tempo real (Prometheus/Grafana), fechando o ciclo de visibilidade operacional.

### 6.4 Fechamento – Dashboard Grafana
1. **O que é um Datasource no Grafana?**  
   *Resposta:* É o conector configurado no Grafana para consultar uma fonte de dados externa. No caso do Prometheus, o Grafana utiliza o protocolo HTTP para executar expressões PromQL contra a API do Prometheus e traduzir os dados em gráficos dinâmicos.
2. **Qual o propósito de cada um dos 4 painéis criados no Dashboard?**  
   *Resposta:*
   - *Status da API:* Fornece visibilidade instantânea de disponibilidade binária (UP/DOWN).
   - *Requisições HTTP/s:* Monitora a vazão e tráfego da aplicação em tempo real.
   - *Tempo Médio de Resposta:* Avalia a latência percebida pelos clientes, detectando degradações de performance.
   - *Memória JVM (Heap):* Acompanha a saúde da máquina virtual Java, prevenindo vazamentos de memória e erros de OutOfMemoryError.
3. **Por que empregar PromQL em vez de bancos relacionais para métricas de sistemas?**  
   *Resposta:* Bancos de séries temporais e a linguagem PromQL são projetados para lidar com altíssimas taxas de ingestão de dados carimbados no tempo, oferecendo operadores estatísticos nativos (`rate`, `irate`, `histogram_quantile`) de alta performance com baixo consumo de armazenamento.
