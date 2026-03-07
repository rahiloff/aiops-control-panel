import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

def run_remote_command(command):
    """SSH Key vazhi EC2-il kayari command run cheyyunna function."""
    host = os.getenv("SERVER_IP")
    user = os.getenv("SERVER_USER")
    key_path = os.getenv("SSH_KEY_PATH")

    try:
        # Load the .pem private key
        key = paramiko.RSAKey.from_private_key_file(key_path)
        
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to EC2 using the key (No password!)
        client.connect(hostname=host, username=user, pkey=key, timeout=10)
        
        # Run the command
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        client.close()
        
        # Return results
        if error and not output:
            return False, error
        return True, output

    except Exception as e:
        return False, f"Connection Failed: {str(e)}"
