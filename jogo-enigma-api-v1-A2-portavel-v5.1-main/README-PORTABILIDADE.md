# V5 - Portabilidade real: Windows + macOS + Linux

A V5 preserva a arquitetura da V4.1, inclusive o teste de repositorio com PostgreSQL real via Testcontainers, mas remove os dois acoplamentos encontrados em laboratorio.

## O que foi corrigido

1. **Jenkins multiplataforma:** o Jenkinsfile escolhe `bat` no Windows e `sh` no macOS/Linux.
2. **Maven Wrapper multiplataforma:** `mvnw.cmd` continua atendendo Windows; `mvnw` agora baixa e usa Maven 3.9.11 no macOS/Linux sem exigir Maven global.
3. **Testcontainers atualizado:** 1.21.3 -> **1.21.4**, linha com correcoes para Docker Engine recente, inclusive Docker 29.
4. **Testcontainers mantido:** `ParticipanteRepositoryTest` continua subindo `postgres:17-alpine`; nao foi substituido por H2.
5. **Health check portavel:** executado por um container `curlimages/curl`, sem depender de PowerShell/curl do host.
6. **Cypress continua em container.**

## Pre-requisitos do aluno

- JDK 17 ou superior no PATH do usuario que executa Jenkins.
- Docker Desktop/Engine iniciado.
- Docker Compose v2 (`docker compose`).
- Git.
- Jenkins com acesso ao mesmo Docker usado pelo terminal.

Nao e necessario instalar Maven, Node.js, npm ou Cypress globalmente.

## Teste local antes do Jenkins

### Windows PowerShell

```powershell
docker version
docker pull postgres:17-alpine
.\mvnw.cmd clean test
```

### macOS/Linux

```bash
docker version
docker pull postgres:17-alpine
chmod +x mvnw
./mvnw clean test
```

O `ParticipanteRepositoryTest` deve iniciar um PostgreSQL temporario pelo Testcontainers e encerra-lo ao final.

## Se Docker funciona, mas Testcontainers falha

Compare `docker version` e o stack trace do teste. A V5 usa Testcontainers 1.21.4 para compatibilidade com Docker Engine recente. Nao crie H2 e nao remova o teste de repositorio para contornar falhas de ambiente.

Comando de diagnostico:

Windows:
```powershell
.\mvnw.cmd "-Dtest=ParticipanteRepositoryTest" test -e
```

macOS/Linux:
```bash
./mvnw -Dtest=ParticipanteRepositoryTest test -e
```

## Portas de HOMOL

| Servico | Host | Container |
|---|---:|---:|
| API | 8081 | 8080 |
| BFF/Front | 3000 | 3000 |
| pgAdmin | 5050 | 80 |
| Prometheus | 9091 | 9090 |
| Grafana | 3001 | 3000 |

## Observacao para Mac Apple Silicon

O pipeline nao fixa `linux/amd64`. As imagens usadas devem selecionar automaticamente a variante adequada (`arm64` ou `amd64`) pelo Docker Desktop. Evite adicionar `platform: linux/amd64` sem necessidade.
