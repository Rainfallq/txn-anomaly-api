// Declarative pipeline for the txn-anomaly-api project.
// Stages: checkout, unit tests (inside Docker), build image, smoke test,
// optional push to Docker Hub.
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // A local Jenkins cannot receive GitHub webhooks, so it checks the repo for new commits.
    triggers {
        pollSCM('H/2 * * * *')
    }

    parameters {
        booleanParam(name: 'PUSH_IMAGE', defaultValue: false,
                     description: 'Push the built image to Docker Hub')
        string(name: 'DOCKERHUB_REPO', defaultValue: 'your-dockerhub-user/txn-anomaly-api',
               description: 'Docker Hub repository, used only when PUSH_IMAGE is on')
    }

    environment {
        IMAGE = 'txn-anomaly-api'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Unit tests') {
            steps {
                // Tests run in the same Python version as the final image.
                sh '''
                    docker build --target test -t ${IMAGE}:test-${BUILD_NUMBER} .
                    set +e
                    docker run --name tests-${BUILD_NUMBER} ${IMAGE}:test-${BUILD_NUMBER} \
                        pytest -q --junitxml=/tmp/junit.xml
                    status=$?
                    docker cp tests-${BUILD_NUMBER}:/tmp/junit.xml junit.xml
                    docker rm -f tests-${BUILD_NUMBER}
                    exit $status
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'junit.xml'
                }
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .'
                sh 'docker image ls ${IMAGE}'
            }
        }

        stage('Smoke test') {
            steps {
                // Start the container and ask its own /health endpoint.
                sh '''
                    docker rm -f smoke-${BUILD_NUMBER} || true
                    docker run -d --name smoke-${BUILD_NUMBER} ${IMAGE}:${BUILD_NUMBER}
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if docker exec smoke-${BUILD_NUMBER} python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"; then
                            echo "Service is healthy"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "Service did not become healthy"
                    docker logs smoke-${BUILD_NUMBER}
                    exit 1
                '''
            }
        }

        stage('Push to Docker Hub') {
            when {
                expression { return params.PUSH_IMAGE }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker tag ${IMAGE}:${BUILD_NUMBER} ${DOCKERHUB_REPO}:${BUILD_NUMBER}
                        docker tag ${IMAGE}:${BUILD_NUMBER} ${DOCKERHUB_REPO}:latest
                        docker push ${DOCKERHUB_REPO}:${BUILD_NUMBER}
                        docker push ${DOCKERHUB_REPO}:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f smoke-${BUILD_NUMBER} tests-${BUILD_NUMBER} || true'
        }
        success {
            echo 'Pipeline finished successfully'
        }
        failure {
            echo 'Pipeline failed, see the console output'
        }
    }
}
