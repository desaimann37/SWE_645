pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "desaimann37"        // your DockerHub username
        IMAGE_NAME = "swe645-app"            // image repo name
        IMAGE_TAG = "latest"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git 'git@github.com:desaimann37/SWE_645.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKERHUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                        dockerImage.push()
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh """
                kubectl apply -f deployment.yaml
                kubectl apply -f service.yaml
                """
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed.'
        }
    }
}