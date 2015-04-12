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
`salt '*' network.ip_addrs`

