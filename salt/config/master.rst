Sync minion grains automatically
--------------------------------
Location
    /etc/salt/master

config

..code-block::
    
    reactor:
        - 'minion_start':
            - /srv/reactor/sync_grains.sls

explanation
    With the above code block added to the master config file and `/srv/reactor/sync_grains.sls`

link
    http://docs.saltstack.com/en/latest/topics/reactor/index.html#minion-start-reactor