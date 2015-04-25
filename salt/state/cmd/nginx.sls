ufw 80/tcp:
    cmd.run:
        - name: ufw allow 80/tcp

ufw 443/tcp:
    cmd.run:
        - name: ufw allow 443/tcp
        
ufw allow salt:
    cmd.run:
        - name: ufw allow salt

ufw 22/tcp:
    cmd.run:
        - name: ufw allow 22/tcp