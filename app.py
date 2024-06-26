import os
import subprocess
import streamlit as st

# Streamlit App Title
st.title("Linux Remote Desktop Setup")

# Input fields for authentication and setup parameters
CRD_SSH_Code = st.text_input("Google CRD SSH Code:", type="password")
VNC_Password = st.text_input("VNC Password:", type="password")
username = st.text_input("Username:", value="user")
password = st.text_input("Password:", type="password", value="root")
CRD_Pin = st.number_input("CRD PIN:", value=123456, step=1)
VNC_Port = 5901  # Default VNC port
Autostart = st.checkbox("Enable Autostart", value=True)

class RemoteDesktopSetup:
    def __init__(self, username, password, crd_ssh_code, vnc_password, crd_pin, vnc_port, autostart):
        self.username = username
        self.password = password
        self.crd_ssh_code = crd_ssh_code
        self.vnc_password = vnc_password
        self.crd_pin = crd_pin
        self.vnc_port = vnc_port
        self.autostart = autostart
        self.setup()

    def setup(self):
        try:
            self.add_user_and_sudo()
            self.switch_to_user()
            self.install_packages()
            self.setup_crd()
            self.setup_vnc()
            self.setup_autostart()
            self.display_connection_details()
        except Exception as e:
            st.error(f"Error occurred during setup: {e}")

    def add_user_and_sudo(self):
        st.write(f"Adding user '{self.username}' and granting sudo access...")
        try:
            os.system(f"useradd -m {self.username}")
            os.system(f"echo '{self.username}:{self.password}' | sudo chpasswd")
            os.system(f"adduser {self.username} sudo")
            os.system("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")
            st.success(f"User '{self.username}' added with sudo access.")
        except Exception as e:
            raise RuntimeError(f"Failed to add user and grant sudo access: {e}")

    def switch_to_user(self):
        st.write(f"Switching to user '{self.username}'...")
        try:
            os.system(f"su - {self.username} -c 'cd ~'")
            st.success(f"Switched to user '{self.username}'.")
        except Exception as e:
            raise RuntimeError(f"Failed to switch to user '{self.username}': {e}")

    def install_packages(self):
        st.write("Installing necessary packages...")
        try:
            self.run_command(["sudo", "apt-get", "update"])  # Update package index
            self.run_command(["sudo", "apt-get", "install", "-y", "chrome-remote-desktop", "gnome-session", "gnome-shell", "tightvncserver"])
            st.success("Packages installed successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to install packages: {e}")

    def setup_crd(self):
        st.write("Setting up Google Chrome Remote Desktop (CRD)...")
        try:
            subprocess.run(["wget", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb"])
            subprocess.run(["sudo", "dpkg", "--install", "chrome-remote-desktop_current_amd64.deb"])
            subprocess.run(["sudo", "apt-get", "install", "--assume-yes", "--fix-broken"])
            subprocess.run(["sudo", "adduser", self.username, "chrome-remote-desktop"])

            # Configure CRD for autostart if enabled
            if self.autostart:
                crd_command = f"{self.crd_ssh_code} --pin={self.crd_pin}"
                subprocess.run(["sudo", "su", "-", self.username, "-c", crd_command])

            st.success("Google Chrome Remote Desktop setup completed.")
        except Exception as e:
            raise RuntimeError(f"Failed to setup Google Chrome Remote Desktop: {e}")

    def setup_vnc(self):
        st.write("Setting up VNC server...")
        try:
            # Start VNC server and set password
            subprocess.run(["sudo", "-u", self.username, "vncserver"])
            os.system(f"sudo -u {self.username} bash -c 'echo {self.vnc_password} | vncpasswd -f > ~/.vnc/passwd'")
            st.success("VNC server setup completed.")
        except Exception as e:
            raise RuntimeError(f"Failed to setup VNC server: {e}")

    def setup_autostart(self):
        st.write("Configuring autostart for remote desktop services...")
        try:
            # Configure CRD autostart if enabled
            if self.autostart:
                crd_autostart_file = f"/home/{self.username}/.config/autostart/chrome-remote-desktop.desktop"
                with open(crd_autostart_file, "w") as f:
                    f.write("[Desktop Entry]\n")
                    f.write("Type=Application\n")
                    f.write("Name=Chrome Remote Desktop\n")
                    f.write("Exec=/opt/google/chrome-remote-desktop/chrome-remote-desktop --start\n")
                    f.write("NoDisplay=true\n")
                    f.write("X-GNOME-Autostart-enabled=true\n")
                    f.write("Hidden=false\n")
                os.system(f"chmod +x {crd_autostart_file}")
                os.system(f"chown {self.username}:{self.username} {crd_autostart_file}")

            st.success("Autostart configured for remote desktop services.")
        except Exception as e:
            raise RuntimeError(f"Failed to configure autostart: {e}")

    def display_connection_details(self):
        st.subheader("Connection Details:")
        host_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
        st.write(f"Host IP Address: {host_ip}")
        st.write(f"Access your desktop through Google Chrome Remote Desktop or VNC on port {self.vnc_port}.")

    def run_command(self, command):
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                st.success(f"Command {' '.join(command)} executed successfully:")
                st.code(stdout.decode('utf-8'))
            else:
                st.error(f"Error executing command {' '.join(command)}:")
                st.code(stderr.decode('utf-8'))
                raise RuntimeError(f"Command {' '.join(command)} returned non-zero exit status {process.returncode}")
        except Exception as e:
            raise RuntimeError(f"Exception occurred while executing command {' '.join(command)}: {e}")

def main():
    if CRD_SSH_Code and len(str(CRD_Pin)) >= 6 and VNC_Password:
        try:
            remote_setup = RemoteDesktopSetup(username, password, CRD_SSH_Code, VNC_Password, CRD_Pin, VNC_Port, Autostart)
        except RuntimeError as e:
            st.error(f"Error during setup: {e}")
    else:
        st.warning("Please enter valid CRD SSH Code, VNC Password (at least 6 characters), and CRD PIN (PIN should be at least 6 digits).")

if __name__ == "__main__":
    main()
