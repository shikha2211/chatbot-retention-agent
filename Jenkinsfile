properties([
  buildDiscarder(logRotator(numToKeepStr: '3')),
  disableConcurrentBuilds(),
])

library identifier: 'gitflowEnablers_multi@master', retriever: modernSCM([$class: 'GitSCMSource',
  remote: 'https://pscode.lioncloud.net/psinnersource/devsecops/simplified-pipelines-for-jenkins/gitflowEnablers_multi.git',
  credentialsId: 'gitlabtoken'])


library identifier: 'build-nodejs_nix@master', retriever: modernSCM([$class: 'GitSCMSource',
   remote: 'https://pscode.lioncloud.net/psinnersource/devsecops/simplified-pipelines-for-jenkins/build-nodejs_nix.git',
   credentialsId: 'gitlabtoken'])

library identifier: 'build-DockerImage@master',retriever: modernSCM([$class: 'GitSCMSource',
	remote: 'https://pscode.lioncloud.net/psinnersource/devsecops/simplified-pipelines-for-jenkins/build-DockerImage.git',
	credentialsId: 'gitlabtoken'])

library identifier: 'notfications_multi@master', retriever: modernSCM([$class: 'GitSCMSource',
        remote: 'https://pscode.lioncloud.net/psinnersource/devsecops/simplified-pipelines-for-jenkins/notifications_multi.git',
        credentialsId: 'gitlabtoken'])

library identifier: 'helm-charts_nix@helm-test',retriever: modernSCM([$class: 'GitSCMSource',
	remote: 'https://pscode.lioncloud.net/engineering-community/devops/simplified-pipelines-for-jenkins/helm-charts_nix.git',
	credentialsId: 'gitlabtoken'])

def tokens = "${env.JOB_NAME}".tokenize('/')
def branchName = tokens[tokens.size()-1].replace("%2F","-")
def (value1, shortBranch) = "${branchName}".tokenize( '-' )
branchName = env.BRANCH_NAME == "master" ? "master" : "${shortBranch}"
if(branchName != "master") {branchName = env.BRANCH_NAME == "develop" ? "develop" : "${shortBranch}"}
if(branchName != "develop" && branchName != "master") {branchName = env.BRANCH_NAME == "omni" ? "omni" : "${shortBranch}"}
def cloudEnv = env.BRANCH_NAME == "master" ? "prodcluster" : "kubernetes"   // Prodcluster is used for production (master branch)
def finalBranchName = env.CHANGE_BRANCH ?: env.BRANCH_NAME

print(branchName)

pipeline {

   // options { timestamps() }

    environment{
            PROJECT_NAME = 'psi-crypto-service'
            VERSION = '1.0.0'
            NAMESPACE = 'ps-innersource'
            RELEASE_NAME = 'psi-crypto-service-1.0'
            gitWorkFlow = ''
            registry= 'psregistry.pscloudhub.com'
            tag = "${branchName}-${BUILD_NUMBER}"
            BRANCH_NAME = "${branchName}"
            ENV_NAME = "${params.ENVIRONMENT}"
            FINAL_BRANCH_NAME = "${finalBranchName}"

    }

    agent {
        kubernetes {
          
            cloud "${cloudEnv}"  // Prodcluster is used for production
            inheritFrom "iris-pwa-${UUID.randomUUID().toString()}" // label is depreciated
            yaml """
                apiVersion: v1
                kind: Pod
                metadata:
                  labels:
                  jenkins: jenkins-pipeline
                spec:
                  volumes:
                  - name: docker-sock
                    hostPath:
                      path: /var/run/docker.sock
                  - name: psregistry
                    projected:
                      sources:
                      - secret:
                          name: psregistry-creds
                          items:
                            - key: .dockerconfigjson
                              path: config.json
                  containers:
                  - name: docker
                    image: docker
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - mountPath: /var/run/docker.sock
                      name: docker-sock
                  - name: kaniko
                    image: psregistry.pscloudhub.com/tools/kaniko:latest
                    imagePullPolicy: Always
                    command:
                    - /busybox/cat
                    tty: true
                    volumeMounts:
                    - name: psregistry
                      mountPath: /kaniko/.docker
                  - name: java-build-tools
                    image: psregistry.pscloudhub.com/tools/openjdk17:gradle8.8
                    imagePullPolicy: Always
                    command:
                    - cat
                    tty: true
                  - name: kube-tools
                    image: psregistry.pscloudhub.com/tools/kube-tools:helm3
                    imagePullPolicy: Always
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - mountPath: /var/run/docker.sock
                      name: docker-sock
                  - name: trivy
                    image: psregistry.pscloudhub.com/tools/aquasec-trivy:0.57.0
                    imagePullPolicy: Always
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - mountPath: /var/run/docker.sock
                      name: docker-sock
                  - name: sonarscanner
                    image: psregistry.pscloudhub.com/tools/sonarscanner:1
                    imagePullPolicy: Always
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - mountPath: /var/run/docker.sock
                      name: docker-sock
                  - name: trufflehog
                    image: psregistry.pscloudhub.com/tools/trufflehog:3.42.0
                    command:
                    - cat
                    tty: true
                  - name: gitleaks
                    image: psregistry.pscloudhub.com/tools/gitleaks:8.18
                    command:
                    - cat
                    tty: true

            """
        }
    }

    stages {
            
            stage('Setup') {
              steps {
                script {
                    // Condition to show parameters only if the branch is not develop, omni, or master
                    if (!(BRANCH_NAME in ['develop', 'omni', 'master'])) {
                        properties([
                            parameters([
                                booleanParam(name: 'DEPLOYABLE', defaultValue: false, description: 'Should we proceed with deployment?'),
                                choice(name: 'ENVIRONMENT', choices: ['develop', 'omni', 'master'], description: 'Select the environment for deployment')
                            ])
                        ])
                    }
                }
              }
            }

  


        stage('kaniko: Build n Publish') {
          steps {
            container('kaniko') {
              echo "Deploying api ...."
                script {
                // Set the environment variable OTEL_SERVICE_NAME
                env.OTEL_SERVICE_NAME = "${FINAL_BRANCH_NAME}-${PROJECT_NAME}"

                 sh "/kaniko/executor --force --dockerfile `pwd`/Dockerfile --context `pwd` --destination=${registry}/psinnersource_platform/engage_pro/chatbot-retention-agent:${tag}"


                } //container
           }
          }
        }

       

        stage('Helm Deploy') {
            when {
              anyOf {
                expression { params.DEPLOYABLE == true }
                anyOf {
                    branch 'develop'
                    branch 'master'
                    branch 'omni'
                }
              }
            }
          steps {
            container('kube-tools') {
              echo "Deploying to environment: ${params.ENVIRONMENT}"
                  helmdeploy()
            }
          }  
        }

        // stage('Cleanup Harbor Image') {
        //   steps {
        //     script {
        //       if (!(env.FINAL_BRANCH_NAME in ['master', 'develop', 'omni'])) {
        //           echo "Deleting image for branch ${env.FINAL_BRANCH_NAME}..."
        //           withCredentials([
        //               string(credentialsId: 'HARBOR_URL', variable: 'HARBOR_URL'),
        //               string(credentialsId: 'HARBOR_CREDENTIALS_USR', variable: 'HARBOR_USERNAME'),
        //               string(credentialsId: 'HARBOR_CREDENTIALS_PSW', variable: 'HARBOR_SECRET')
        //           ]) {
        //               sh '''#!/bin/bash
        //               curl --user "$HARBOR_USERNAME:$HARBOR_SECRET" -X DELETE "$HARBOR_URL/api/v2.0/projects/psinnersource_platform/repositories/psi-crypto-service/artifacts/${tag}"
        //               '''
        //           }
        //       } else {
        //           echo "Branch ${env.FINAL_BRANCH_NAME} is in the allowed list. Skipping image deletion."
        //       }
        //     }
        //   }
        // }

        stage('Reporting') {
          steps {
            container('puppeteer') {
              //blueOceanScreenShot()
            }
          }
        }
 }

  post {
    always {
     // emailNotify()
     sh "echo skip"
     
    }
  }
}
