import streamlit as st
import os
import subprocess
import secrets
import shutil

# Function to check if sudo access is available
def check_sudo():
    try:
        # Attempt to run a harmless sudo command
        subprocess.run(["sudo", "-n", "true"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Function to install required packages if not already installed
def install_packages():
    st.write("Checking and installing necessary packages...")
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "ubuntu-desktop", "x11vnc"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to install packages: {e}")
        return False
    return True

# Function to generate a secure VNC password
def generate_vnc_password():
    return secrets.token_urlsafe(12)

# Function to start the x11vnc server
def start_vnc_server(vnc_password):
    st.write("Starting VNC server...")
    try:
        # Write the VNC password to a file (for initial setup purposes)
        password_file = "/tmp/vnc_password"
        with open(password_file, "w") as f:
            f.write(vnc_password)
        
        # Set permissions to read-only by the owner
        os.chmod(password_file, 0o600)
        
        # Start x11vnc server with the specified password file
        subprocess.run(["sudo", "x11vnc", "-storepasswd", vnc_password, password_file], check=True)
        subprocess.Popen(["sudo", "x11vnc", "-display", ":0", "-auth", "guess", "-rfbauth", password_file])
        st.success("VNC server started successfully.")
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to start VNC server: {e}")

# Function to display connection details
def display_connection_details():
    st.subheader("Connection Details:")
    host_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
    st.write(f"Host IP Address: {host_ip}")
    st.write("VNC Port: 5900 (default)")
    st.write("Connect using any VNC client with the above details.")

# Main function to run the Streamlit app
def main():
    st.title("Linux VNC Server Setup")
    
    # Check if sudo access is available
    if not check_sudo():
        st.error("Sudo access is required to run this app.")
        return
    
    # Install necessary packages if not already installed
    if not install_packages():
        st.error("Failed to install necessary packages.")
        return
    
    # Generate a secure VNC password
    vnc_password = generate_vnc_password()
    
    # Start the VNC server
    start_vnc_server(vnc_password)
    
    # Display connection details
    display_connection_details()

if __name__ == "__main__":
    main()
