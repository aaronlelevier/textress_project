Install
-------
- Install all dependencies from: http://docs.saltstack.com/en/latest/topics/installation/ubuntu.html 
on the salt master server named `salt`

- Install all dependencies from above except `salt-master` on a server name `minion`

- On the `minion` server, change the `/etc/salt/minion` file:
`# master: salt`
to
`master: <ip addrs of master>`

- Restart salt-minion: `service salt-minion restart`

- Test on salt master server: `salt '*' test.ping`


Common Commands
---------------
# get all IP addresses for master and minions
salt '*' network.ip_addrs

# send state to all
salt '*' state.sls <state_name>

# send out `highstate` from /srv/salt/top.sls
salt '*' state.highstate
[note: the '*' is always an arg, so if I want to send out state to only certain
minions, then I would just name them there instead of '*']