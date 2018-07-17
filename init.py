import subprocess


params = [ 'java', '-jar', '/usr/share/jenkins/jenkins.war']
subprocess.Popen(params, stdout=subprocess.PIPE)

# setup the suggested and desired plugins list
f = open('./plugins.txt', 'r')
suggested_plugins = []
for line in f:
  stripped = line.strip()
  suggested_plugins.append(stripped)

i = 0
while i < len(suggested_plugins):
  PLUGIN = suggested_plugins[i]
  subprocess.run(["java", "-jar", "/var/jenkins_home/war/WEB-INF/jenkins-cli.jar", "-s", "http://127.0.0.1:8080/", "-auth", "admin:admin", "install-plugin", PLUGIN])
  i += 1
