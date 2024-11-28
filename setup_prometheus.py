import os
import subprocess
import shutil
import sys
import tarfile
import urllib.request


PROMETHEUS_VERSION = "2.47.0"
PROMETHEUS_USER = "prometheus"
INSTALL_DIR = "/usr/local/bin"
CONFIG_DIR = "/etc/prometheus"
DATA_DIR = "/var/lib/prometheus"
SERVICE_FILE = "/etc/systemd/system/prometheus.service"
TAR_FILE = f"prometheus-{PROMETHEUS_VERSION}.linux-amd64.tar.gz"
PROMETHEUS_URL = f"https://github.com/prometheus/prometheus/releases/download/v{PROMETHEUS_VERSION}/{TAR_FILE}"
DOWNLOAD_DIR = "/tmp/prometheus"

def run_command(command, check=True):
    """Helper function to run a shell command."""
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, check=check, text=True)
    return result

def download_prometheus():
    """Download the Prometheus tarball."""
    print("Downloading Prometheus...")
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    tarball_path = os.path.join(DOWNLOAD_DIR, TAR_FILE)
    urllib.request.urlretrieve(PROMETHEUS_URL, tarball_path)
    return tarball_path

def extract_prometheus(tarball_path):
    """Extract the Prometheus tarball."""
    print(f"Extracting {tarball_path}...")
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(path=DOWNLOAD_DIR)

def create_prometheus_user():
    """Create a Prometheus user."""
    print("Creating Prometheus user...")
    run_command(f"sudo useradd -rs /bin/false {PROMETHEUS_USER}")
    run_command(f"sudo mkdir -p {CONFIG_DIR} {DATA_DIR}")
    run_command(f"sudo chown -R {PROMETHEUS_USER}:{PROMETHEUS_USER} {CONFIG_DIR} {DATA_DIR}")

def move_binaries_and_configs():
    """Move Prometheus binaries and configuration files."""
    print("Moving binaries and config files...")
    extracted_dir = os.path.join(DOWNLOAD_DIR, f"prometheus-{PROMETHEUS_VERSION}.linux-amd64")
    
    shutil.move(os.path.join(extracted_dir, "prometheus"), INSTALL_DIR)
    shutil.move(os.path.join(extracted_dir, "promtool"), INSTALL_DIR)
    shutil.move(os.path.join(extracted_dir, "consoles"), CONFIG_DIR)
    shutil.move(os.path.join(extracted_dir, "console_libraries"), CONFIG_DIR)
    shutil.move(os.path.join(extracted_dir, "prometheus.yml"), CONFIG_DIR)

def create_systemd_service():
    """Create a systemd service for Prometheus."""
    print("Creating systemd service file...")
    service_content = f"""
[Unit]
Description=Prometheus Service
Wants=network-online.target
After=network-online.target

[Service]
User={PROMETHEUS_USER}
Group={PROMETHEUS_USER}
Type=simple
ExecStart={INSTALL_DIR}/prometheus \\
  --config.file={CONFIG_DIR}/prometheus.yml \\
  --storage.tsdb.path={DATA_DIR} \\
  --web.console.templates={CONFIG_DIR}/consoles \\
  --web.console.libraries={CONFIG_DIR}/console_libraries

[Install]
WantedBy=multi-user.target
"""
    with open(SERVICE_FILE, "w") as service_file:
        service_file.write(service_content)

def start_and_enable_prometheus():
    """Start and enable Prometheus as a service."""
    print("Starting and enabling Prometheus service...")
    run_command("sudo systemctl daemon-reload")
    run_command("sudo systemctl start prometheus")
    run_command("sudo systemctl enable prometheus")

def cleanup():
    """Clean up the installation files."""
    print("Cleaning up installation files...")
    shutil.rmtree(DOWNLOAD_DIR)

def main():
    try:
        # Step 1: Download Prometheus
        tarball_path = download_prometheus()

        # Step 2: Extract Prometheus
        extract_prometheus(tarball_path)

        # Step 3: Create Prometheus user and directories
        create_prometheus_user()

        # Step 4: Move binaries and config files
        move_binaries_and_configs()

        # Step 5: Create systemd service file
        create_systemd_service()

        # Step 6: Start and enable the Prometheus service
        start_and_enable_prometheus()

        # Step 7: Clean up
        cleanup()

        print("Prometheus setup completed successfully!")
        print("Access Prometheus at http://<your_server_ip>:9090")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
