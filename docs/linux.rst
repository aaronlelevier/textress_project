# get running processes
ps --sort -rss -eo rss,pid,command | head

# free memory
free -m


ssh
---
# generate ssh key
ssh-keygen -t rsa -C "your_email@example.com"

# start ssh-agent and assign
eval "$(ssh-agent -s)"
ssh-add <path_to_key>

# get ssh rsa fingerprint
ssh-keygen -lf ~/.ssh/id_rsa.pub


ports
-----
# kill pid using port # 8000
fuser -k 8000/tcp

# kill using pid #
kill -9 pid


nginx
-----
# make unix websocket executable
chomod 0666 textress.sock