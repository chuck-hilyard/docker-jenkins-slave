# this is called by docker run
#
# starts jenkins
# installs plugins
# adds github based projects to jenkins/jobs

import http.client
import jenkins
import os
import requests
import socket
import subprocess
import time

def install_software():
  # install build/test software
  # TODO: make sure the previous install is done prior to moving on
  subprocess.run(["sudo", "mkdir", "/var/jenkins_home", "/var/jenkins_home/.ssh", "/var/jenkins_home/.aws"])
  subprocess.run(["sudo", "cp", "/tmp/authorized_keys", "/var/jenkins_home/.ssh"])
  subprocess.run(["sudo", "cp", "/tmp/known_hosts", "/var/jenkins_home/.ssh"])
  subprocess.run(["sudo", "cp", "/tmp/credentials", "/var/jenkins_home/.aws"])
  subprocess.run(["sudo", "service", "ssh", "start"])
  subprocess.run(["sudo", "apt-get", "install", "-y", "curl", "chromium-browser", "libgconf2-4", "docker.io", "openjdk-8-jre-headless" ])
  time.sleep(30)
  subprocess.run(["sudo", "useradd", "jenkins"])
  subprocess.run(["curl -sL https://deb.nodesource.com/setup_10.x |sudo -E bash -"], shell=True)
  time.sleep(30)
  subprocess.run(["sudo", "apt-get", "install", "-y", "nodejs"])
  subprocess.run(["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-yq", "awscli", "python3-boto3"])
  time.sleep(30)
  subprocess.run(["usermod", "-aG", "docker", "jenkins"])
  time.sleep(30)
  subprocess.run(["sudo", "npm", "install", "-g", "gulp"])
  time.sleep(30)
  subprocess.run(["sudo", "service", "docker", "start"])
  time.sleep(30)
  subprocess.run(["ssh-keyscan", "github.com", '>>', "/var/jenkins_home/.ssh/known_hosts"])
  time.sleep(30)
  subprocess.run(["chown", "jenkins:jenkins", "-R", "/var/jenkins_home"])
  time.sleep(30)
  subprocess.run(["pip3", "install", "consul_kv"])
  #subprocess.run(["sudo", "service", "ssh", "start"])

def join_jenkins_master():
  print("joining jenkins master")
  containerId = socket.gethostname()
  server = jenkins.Jenkins('http://jenkins-master', username='admin', password='admin')
  params = {
      'port': '22',
      'username': 'jenkins',
      'credentialsId': 'jenkins-credential-id',
      'host': '172.17.0.3'
    }
  server.create_node(
    containerId,
    nodeDescription = "test slave node",
    remoteFS = "/var/jenkins_home",
    labels = "common",
    exclusive = False,
    launcher = jenkins.LAUNCHER_SSH,
    launcher_params = params)

def is_master_up():
  print("is master up?")
  server = jenkins.Jenkins('http://jenkins-master', username='admin', password='admin')
  try:
    master_job_info = server.get_job_info("jenkins-init", depth=0, fetch_all_builds=False)
    is_up = master_job_info['displayName']
  except (http.client.RemoteDisconnected):
    print("jenkins master may have gone down")
    is_up = False
  except (jenkins.JenkinsException):
    print("unable to connect with master")
    is_up = False
  if is_up == 'jenkins-init':
    print("master is up!")
    return True
  else:
    print("master is DOWN!")
    return False

def node_exists_on_master():
  containerId = socket.gethostname()
  server = jenkins.Jenkins('http://jenkins-master', username='admin', password='admin')
  return server.node_exists(containerId)


def main():
  while True:
    print("main loop")
    status = is_master_up()
    if status == True:
      is_node_on_master = node_exists_on_master()
      if is_node_on_master == False:
        # this is removed in favor of master polling consul
        #join_jenkins_master()
        print("dummy line")
      else:
        print("this agent is already on master")
  else:
    print("master is DOWN...rechecking in 30 seconds")
  time.sleep(60)


if __name__ == '__main__':
  install_software()
  main()
