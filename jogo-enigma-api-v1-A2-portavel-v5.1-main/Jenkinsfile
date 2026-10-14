// V5.1 - Pipeline portavel Windows + macOS + Linux
// Preflight diagnostico: identifica exatamente o comando com problema e evita travamento indefinido.
// Mantem Testcontainers/PostgreSQL real e elimina dependencia de BAT fora do Windows.

def runCmd(String command) {
    if (isUnix()) {
        sh command
    } else {
        bat command
    }
}

def mvnw(String args) {
    if (isUnix()) {
        sh "chmod +x mvnw && ./mvnw ${args}"
    } else {
        bat "call mvnw.cmd ${args}"
    }
}

pipeline {
    agent any

    parameters {
        booleanParam(name: 'PUSH_DOCKER_HUB', defaultValue: false,
            description: 'Opcional: publicar a imagem no Docker Hub apos o build local.')
    }

    environment {
        DOCKER_IMAGE = 'andprof/jogo-enigma-api'
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        IMAGE_TAG = "${BUILD_NUMBER}"
        COMPOSE_FILE = 'docker-compose.homol.yml'
        API_PORT = '8081'
        BFF_PORT = '3000'
        PGADMIN_PORT = '5050'
        PROMETHEUS_PORT = '9091'
        GRAFANA_PORT = '3001'
    }

    stages {
        stage('0 - Preflight do Ambiente') {
            steps {
                script {
                    echo "Plataforma Jenkins: ${isUnix() ? 'macOS/Linux (Unix)' : 'Windows'}"

                    echo '>>> [1/4] JAVA - verificando runtime usado pelo agente Jenkins'
                    timeout(time: 30, unit: 'SECONDS') {
                        runCmd('java -version')
                    }
                    echo '>>> [OK 1/4] JAVA'

                    echo '>>> [2/4] DOCKER CLI/ENGINE - verificando comunicacao cliente-servidor'
                    timeout(time: 60, unit: 'SECONDS') {
                        runCmd('docker version')
                    }
                    echo '>>> [OK 2/4] DOCKER CLI/ENGINE'

                    echo '>>> [3/4] DOCKER COMPOSE - verificando plugin Compose'
                    timeout(time: 30, unit: 'SECONDS') {
                        runCmd('docker compose version')
                    }
                    echo '>>> [OK 3/4] DOCKER COMPOSE'

                    echo '>>> [4/4] DOCKER ENGINE - verificando acesso completo ao daemon'
                    timeout(time: 60, unit: 'SECONDS') {
                        runCmd('docker info')
                    }
                    echo '>>> [OK 4/4] DOCKER ENGINE'

                    echo '>>> PREFLIGHT CONCLUIDO COM SUCESSO'
                    echo '[OK] Maven, Node, npm e Cypress globais nao sao obrigatorios.'
                }
            }
        }

        stage('1 - Checkout') {
            steps { checkout scm }
        }

        stage('2 - CI - JUnit + Testcontainers + JaCoCo') {
            steps {
                script {
                    // Inclui ParticipanteRepositoryTest com PostgreSQL 17 real via Testcontainers.
                    mvnw('-B clean test')
                }
            }
            post {
                always {
                    junit testResults: 'target/surefire-reports/*.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'target/site/jacoco/**', allowEmptyArchive: true
                }
            }
        }

        stage('3 - CI - Qualidade PMD') {
            steps { script { mvnw('-B pmd:pmd -DskipTests') } }
            post {
                always { archiveArtifacts artifacts: 'target/site/pmd.html', allowEmptyArchive: true }
            }
        }

        stage('4 - CI - Package') {
            steps { script { mvnw('-B package -DskipTests') } }
        }

        stage('5 - CD - Build dos Containers') {
            steps { script { runCmd('docker compose -f ' + env.COMPOSE_FILE + ' build api bff') } }
        }

        stage('6 - Registry - Docker Hub (opcional)') {
            when { expression { return params.PUSH_DOCKER_HUB } }
            steps {
                withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID,
                    usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
                    script {
                        if (isUnix()) {
                            sh 'echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin'
                        } else {
                            bat 'echo %DOCKER_PASSWORD% | docker login -u %DOCKER_USER% --password-stdin'
                        }
                        runCmd("docker push ${env.DOCKER_IMAGE}:${env.IMAGE_TAG}")
                        runCmd('docker logout')
                    }
                }
            }
        }

        stage('7 - CD - Deploy HOMOL') {
            steps {
                script {
                    runCmd('docker compose -f ' + env.COMPOSE_FILE + ' down --remove-orphans')
                    runCmd('docker compose -f ' + env.COMPOSE_FILE + ' up -d postgres pgadmin api bff prometheus grafana')
                }
            }
        }

        stage('8 - CD - Health Check HOMOL') {
            steps {
                script {
                    // Health check executado de dentro do BFF, pela rede interna do Compose.
                    // Assim nao dependemos de PowerShell/curl do host nem de --network host.
                    def healthCmd = "docker compose -f ${env.COMPOSE_FILE} exec -T bff node -e \"let n=0; const t=setInterval(async()=>{n++;try{const r=await fetch('http://api:8080/actuator/health');if(r.ok){console.log(await r.text());clearInterval(t);process.exit(0)}}catch(e){} if(n>=18){clearInterval(t);process.exit(1)}},5000)\""
                    try {
                        runCmd(healthCmd)
                    } catch (err) {
                        runCmd('docker compose -f ' + env.COMPOSE_FILE + ' ps')
                        runCmd('docker compose -f ' + env.COMPOSE_FILE + ' logs --tail=100 api')
                        throw err
                    }
                }
            }
        }

        stage('9 - CD - Cypress E2E em Container') {
            steps { script { runCmd('docker compose -f ' + env.COMPOSE_FILE + ' --profile e2e run --rm cypress') } }
            post {
                always {
                    archiveArtifacts artifacts: 'frontend/cypress/screenshots/**,frontend/cypress/videos/**', allowEmptyArchive: true
                }
            }
        }

        stage('10 - Observabilidade') {
            steps {
                echo "API: http://localhost:${API_PORT}"
                echo "BFF/Front: http://localhost:${BFF_PORT}"
                echo "pgAdmin: http://localhost:${PGADMIN_PORT}"
                echo "Prometheus: http://localhost:${PROMETHEUS_PORT}"
                echo "Grafana: http://localhost:${GRAFANA_PORT}"
            }
        }
    }

    post {
        success { echo 'Pipeline V5.1 concluido: Windows/macOS/Linux, Testcontainers, HOMOL, E2E e observabilidade aprovados.' }
        failure { echo 'Pipeline interrompido. Consulte o stage e os logs para identificar ambiente, teste ou servico responsavel.' }
        always {
            archiveArtifacts artifacts: 'target/site/jacoco/**,target/site/pmd.html,frontend/cypress/screenshots/**,frontend/cypress/videos/**', allowEmptyArchive: true
        }
    }
}
