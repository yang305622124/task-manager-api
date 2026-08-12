pipeline {
    agent any
    parameters {
        booleanParam(name: 'X86', defaultValue: false, description: '是否制作 x86 架构镜像？')
        booleanParam(name: 'ARM64', defaultValue: false, description: '是否制作 arm64 架构镜像？')
        booleanParam(name: 'MANIFEST', defaultValue: false, description: '是否制作 多架构(x86 & arm64) 镜像清单？')
        choice(name: 'CLUSTERNAME', choices: ['10.3.5.5','hz-dev-x86', 'hz-test-x86', 'hz-dev-arm64'], description: '请选择要部署的环境')
    }
    environment {
        namespaces = "imp3"
        servicename = "imp-33-risk"

        registry = "10.3.5.8"
        now = sh(script: "echo `date '+%Y%m%d%H%M%S'`", returnStdout: true).trim()
        image_x86 = "$registry/imp-system/$servicename:dev-x86-${BUILD_ID}-${now}"
        image_arm64 = "$registry/imp-system/$servicename:dev-arm64-${BUILD_ID}-${now}"
        //image = "$registry/imp-system/$servicename:dev-${BUILD_ID}-${now}"

        workdir = """${sh(
                returnStdout: true,
                script: 'pwd'
            )}"""
    }
    stages {
        stage('Test') {
            steps {
                echo 'Testing... none'
                //echo "镜像: $image"
            }
        }
        // stage('NodeJS_Build') {
        //     agent {
        //         docker {
        //             image 'node:14.18.0'
        //         }
        //     }
        //     steps {
        //         echo '---- ---- ---- NodeJS_Build Begin ---- ---- ---- '
        //         sh 'yarn config set registry https://registry.npm.taobao.org'
        //         //sh 'npm install -g cnpm --registry=https://registry.npmmirror.com'
        //         sh 'yarn install'
        //         sh 'yarn run build'
        //         sh 'ls'
        //         sh 'cp -rf dist ${workdir}'
        //         sh 'sleep 5s'
        //         echo '---- ---- ---- NodeJS_Build End ---- ---- ---- '
        //     }
        // }
        stage('x86_Docker_Build_Push') {
            when{
                expression { return params.X86 }
            }
            agent {
                label 'node01_x86_docker'
            }
            steps {
                echo '---- ---- ---- x86_Docker_Build_Push Begin ---- ---- ---- '
                withCredentials([usernamePassword(credentialsId: 'harbor', usernameVariable: 'harborUser', passwordVariable: 'harborPassword')]) {
                  sh 'docker login -u ${harborUser} -p ${harborPassword} $registry'
                  sh 'docker build -t $image_x86 -f Jenkins-dockerfile .'
                  sh 'trivy image --skip-db-update --severity HIGH,CRITICAL $image_x86'
                  sh 'docker push $image_x86'
                  //sh 'docker rmi $image_x86'
                }
                echo "镜像地址: $image_x86"
                echo "镜像地址: $image_x86"
                echo "镜像地址: $image_x86"
                echo '---- ---- ---- x86_Docker_Build_Push End ---- ---- ---- '
            }
        }
        stage('arm64_Docker_Build_Push') {
            when{
                expression { return params.ARM64 }
            }
            agent {
                label 'node02_arm64_docker'
            }
            steps {
                echo '---- ---- ---- arm64_Docker_Build_Push Begin ---- ---- ---- '
                withCredentials([usernamePassword(credentialsId: 'harbor', usernameVariable: 'harborUser', passwordVariable: 'harborPassword')]) {
                  sh 'docker login -u ${harborUser} -p ${harborPassword} $registry'
                  sh 'docker build -t $image_arm64 -f Jenkins-dockerfile .'
                  sh 'trivy image --skip-db-update --severity HIGH,CRITICAL $image_arm64'
                  sh 'docker push $image_arm64'
                  //sh 'docker rmi $image_arm64'
                }
                echo "镜像地址: $image_arm64"
                echo "镜像地址: $image_arm64"
                echo "镜像地址: $image_arm64"
                echo '---- ---- ---- arm64_Docker_Build_Push End ---- ---- ---- '
            }
        }
        //stage('manifest_Docker_Build_Push') {
        //    when{
        //        expression { return params.MANIFEST }
        //    }
        //    agent {
        //        label 'node01_x86_docker'
        //    }
        //    steps {
        //        echo '---- ---- ---- manifest_Docker_Build_Push Begin ---- ---- ---- '
        //        withCredentials([usernamePassword(credentialsId: 'harbor', usernameVariable: 'harborUser', passwordVariable: 'harborPassword')]) {
        //          sh 'docker login -u ${harborUser} -p ${harborPassword} $registry'
        //          sh 'docker manifest create $image $image_x86 $image_arm64'
        //          sh 'docker manifest push $image'
        //        }
        //        echo '---- ---- ---- manifest_Docker_Build_Push End ---- ---- ---- '
        //    }
        //}
        stage('Deploy') {
            agent {
                docker {
                    image 'kubesphere/kubectl:v1.22.9'
                }
            }
            steps {
                echo '---- ---- ---- Deploy to k8s Begin ---- ---- ---- '
                script {
                    if ( params.CLUSTERNAME == '10.3.5.5' ) {
                        echo "替换镜像: $image_x86"
                        sh "sed -i 's#image:.*#image: $image_x86#' Jenkins-deploy.yaml"
                    }
                    if ( params.CLUSTERNAME == 'hz-dev-x86' ) {
                        echo "替换镜像: $image_x86"
                        sh "sed -i 's#image:.*#image: $image_x86#' Jenkins-deploy.yaml"
                    }
                    if ( params.CLUSTERNAME == 'hz-test-x86' ) {
                        echo "替换镜像: $image_x86"
                        sh "sed -i 's#image:.*#image: $image_x86#' Jenkins-deploy.yaml"
                    }
                    if ( params.CLUSTERNAME == 'hz-dev-arm64' ) {
                        echo "替换镜像: $image_arm64"
                        sh "sed -i 's#image:.*#image: $image_arm64#' Jenkins-deploy.yaml"
                    }
                }

                withCredentials([file(credentialsId: "${params.CLUSTERNAME}", variable: 'FILE')]) {
                    //echo "配置 kubectl config 文件"
                    sh 'mkdir -p ~/.kube && cp $FILE ~/.kube/config'
                    // 输出部署的脚本-检查
                    sh 'cat Jenkins-configmap-dev.yaml'
                    sh 'cat Jenkins-deploy.yaml'
                    //sh '部署 yaml 脚本'
                    sh 'kubectl get namespace $namespaces || kubectl create namespace $namespaces'
                    sh 'kubectl apply -f Jenkins-configmap-dev.yaml -n $namespaces'
                    sh 'kubectl apply -f Jenkins-deploy.yaml -n $namespaces'
                }
                echo '---- ---- ---- Deploy to k8s End ---- ---- ---- '
            }
        }
    }
}
