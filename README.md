# digitalocean-dns-sync
Python script to synchronise the DNS records from any server running BIND with DigitalOcean's DNS servers.

Usage:

1. sudo pip install requests
2. Create a settings.py file in the project directory (it's listed in .gitignore so won't be committed) containing 
2 variables: ip is the IP address of the server you are syncing an auth_token is your DigitalOcean API token.
3. Either run:
```
python sync_dns.py
```
to do a complete wipe of all zones that are on the server and a re-sync from scratch. It won't wipe domains from 
DigitalOcean's DNS it doesn't find on the server so you are free to use DO's DNS for extra domains if you wish. Or 
alternatively run:
```
python sync_dns.py domainname
```
to do an intelligent sync of just that domain.
