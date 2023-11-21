import paramiko


def restart_server(args):
  print(args)
  server_hostname = args['server_hostname']
  private_key_path = "private_key"
  password = 't00r@@'
  # Load the private key
  try:
    private_key = paramiko.RSAKey.from_private_key_file(
        private_key_path, password)
  except paramiko.SSHException:
    print(
        "Error loading private key. Please check the file path and try again.")
    return

  # Create an SSH client
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  try:
    # Connect to the server
    ssh.connect(hostname=server_hostname, username='root', pkey=private_key)

    # Execute the restart command
    stdin, stdout, stderr = ssh.exec_command('sudo reboot')

    # You can print the output or errors if necessary
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()
    return "Server restart command sent successfully."

  except Exception as e:
    print(f"An error occurred: {e}")
    ssh.close()


if __name__ == "__main__":
  restart_server({"server_hostname": "grandemoisson.ci"})
