Linux
=====

.. code-block::

    # get running processes
    ps --sort -rss -eo rss,pid,command | head

    # free memory
    free -m

    # completely remove a package
    apt-get remove <package>
    apt-get purge <package>


grep
----

.. code-block::

    # look for a string in files
    grep -rnw 'directory' -e 'pattern'


echo
----

.. code-block::

    # insert date into file
    echo Test Job ran at  `date` >> /var/log/testjob.log


ubuntu server
-------------

`Set Timezone <https://help.ubuntu.com/community/UbuntuTime>`_

.. code-block::

    echo "Australia/Adelaide" | sudo tee /etc/timezone
    sudo dpkg-reconfigure --frontend noninteractive tzdata

.. code-block::

    # reboot
    shutdown -r now


User Setup / Commands
---------------------

.. code-block::

# list all Users
cut -d: -f1 /etc/passwd

# create user and add to group
sudo useradd nginx
sudo groupadd nginx
sudo usermod -a -G nginx nginx
sudo passwd nginx

sudo adduser web sudo
sudo deluser web sudo

ssh
---

.. code-block::

    # generate ssh key
    ssh-keygen -t rsa -C "your_email@example.com"

    # start ssh-agent and assign
    eval "$(ssh-agent -s)"
    ssh-add <path_to_key>

    # get ssh rsa fingerprint
    ssh-keygen -lf ~/.ssh/id_rsa.pub

    # required permissions for private / public keys
    chmod 0400 <key>


ports
-----

.. code-block::

    # kill pid using port # 8000
    fuser -k 8000/tcp

    # kill using pid #
    kill -9 pid