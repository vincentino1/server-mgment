# tasks.py
import subprocess
from app import celery  # ensure celery instance is imported properly

@celery.task(bind=True, max_retries=3)
def create_user_account(self, username, group, description, publicKey):
    try:
        # Ensure the group exists
        subprocess.run(["sudo", "groupadd", "-f", group], check=True)
        
        # Check if the user already exists, then create if not
        user_check = subprocess.run(["id", username], capture_output=True, text=True)
        if user_check.returncode != 0:  # User does not exist
            subprocess.run(
                ["sudo", "useradd", "-m", "-s", "/bin/bash", "-c", description, "-g", group, username],
                check=True
            )
        
        # Setting up SSH directory and authorized_keys
        ssh_dir = f"/home/{username}/.ssh"
        auth_keys = f"{ssh_dir}/authorized_keys"
        
        subprocess.run(["sudo", "mkdir", "-p", ssh_dir], check=True)
        subprocess.run(["sudo", "chmod", "700", ssh_dir], check=True)
        subprocess.run(["sudo", "chown", f"{username}:{group}", ssh_dir], check=True)
        
        # Add the public key
        subprocess.run(
            f"echo '{publicKey}' | sudo tee {auth_keys}",
            shell=True,
            check=True
        )
        subprocess.run(["sudo", "chmod", "600", auth_keys], check=True)
        subprocess.run(["sudo", "chown", f"{username}:{group}", auth_keys], check=True)
        
    except subprocess.CalledProcessError as e:
        # Log error and retry if appropriate
        self.retry(exc=e, countdown=60)
