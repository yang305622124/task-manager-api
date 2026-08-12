pipeline {
    agent any
    parameters {
        booleanParam(name: 'X86', defaultValue: false, description: '是否制作 x86 架构镜像？')
        booleanParam(name: 'ARM64', defaultValue: false, description: '是否制作 arm64 架构镜像？')
        booleanParam(name: 'MANIFEST', defaultValue: false, description: '是否制作 多架构(x86 & arm64) 镜像清单？')
        choice(name: 'CLUSTERNAME', choices: ['10.211.55.5','10.3.5.5','hz-dev-x86', 'hz-test-x86', 'hz-dev-arm64'], description: '请选择要部署的环境')
    }
    environment {
        namespaces = "task-manager"
        servicename = "task-manager-api"

        registry = "hub.xiaohua99.cn:32005"
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
        stage('arm64_Docker_Build_Push') {
            when{
                expression { return params.ARM64 }
            }
            agent {
                label 'arm64_10.211.55.5'
            }
            steps {
                echo '---- ---- ---- arm64_Docker_Build_Push Begin ---- ---- ---- '
                withCredentials([usernamePassword(credentialsId: 'harbor', usernameVariable: 'harborUser', passwordVariable: 'harborPassword')]) {
                  sh 'docker login -u ${harborUser} -p ${harborPassword} $registry'
                  sh 'docker build -t $image_arm64 -f Dockerfile .'
                  //sh 'trivy image --skip-db-update --severity HIGH,CRITICAL $image_arm64'
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
                    if ( params.CLUSTERNAME == '10.211.55.5' ) {
                        echo "替换镜像: $image_arm64"
                        sh "sed -i 's#image:.*#image: $image_arm64#' k8s/deployment.yaml"
                    }
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
                    sh 'cat k8s/deployment.yaml'
                    //sh '部署 yaml 脚本'
                    sh 'kubectl apply -f k8s/'
                }
                echo '---- ---- ---- Deploy to k8s End ---- ---- ---- '
            }
        }
    }
}
