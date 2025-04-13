#!/bin/bash
set -euo pipefail

CONFIG_FILE="configs/*.txt"

# Check if the CONFIG_FILE exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Config file $CONFIG_FILE not found. Exiting."
  exit 1
fi

# Read the single line from the file
IFS=":" read -r username group description publicKey < "$CONFIG_FILE"

# Check that the username is not empty
if [ -z "$username" ]; then
  echo "Username field is empty in $CONFIG_FILE. Exiting."
  exit 1
fi

echo "Processing user: $username"

# Create the group if it does not exist
if ! getent group "$group" > /dev/null 2>&1; then
  echo "Creating group $group..."
  sudo groupadd "$group"
fi

# Create the user (with Bash as default shell), if not already existing
if id "$username" > /dev/null 2>&1; then
  echo "User $username already exists. Skipping user creation."
else
  echo "Creating user $username with default shell /bin/bash..."
  sudo useradd -m -s /bin/bash -c "$description" -g "$group" "$username"
fi

# Set up the SSH directory and authorized_keys file
SSH_DIR="/home/$username/.ssh"
AUTH_KEYS="$SSH_DIR/authorized_keys"
sudo mkdir -p "$SSH_DIR"
sudo chmod 700 "$SSH_DIR"
sudo chown "$username":"$group" "$SSH_DIR"

echo "Adding public key for $username..."
echo "$publicKey" | sudo tee "$AUTH_KEYS" > /dev/null
sudo chmod 600 "$AUTH_KEYS"
sudo chown "$username":"$group" "$AUTH_KEYS"

# Clean up the config file after successful processing
echo "User processed successfully. Deleting the configuration file..."
rm -f "$CONFIG_FILE"
echo "Done."
