apt-get update
ufw deny
ufw logging on
ufw allow 22/tcp
ufw allow salt
ufw enable
ufw status