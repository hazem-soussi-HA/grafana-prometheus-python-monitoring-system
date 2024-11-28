import os
import subprocess

def run_command(command):
    """Run a shell command and print its output."""
    try:
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

def install_grafana():
    # Update the system
    run_command("apt update && apt upgrade -y")
    
    # Install gnupg if not already installed
    run_command("apt install -y gnupg")
    
    # Add Grafana repository and GPG key
    run_command("wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -")
    run_command("echo 'deb https://packages.grafana.com/oss/deb stable main' > /etc/apt/sources.list.d/grafana.list")
    run_command("apt update")
    
    # Install Grafana
    run_command("apt install -y grafana")
    
    # Start and enable Grafana service
    run_command("systemctl start grafana-server")
    run_command("systemctl enable grafana-server")
    
    print("Grafana installation completed successfully.")

if __name__ == "__main__":
    install_grafana()
