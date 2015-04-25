cmd_update:
    cmd.run:
        - name: |
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw status
