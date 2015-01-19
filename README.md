# DigitalOcean DNS Synchronisation
DigitalOcean offers a fantastic DNS service and API but it is time consuming and cumbersome to manually update it if you 
have a droplet with domain management tools already on it. This python script will synchronise the DNS records from any 
droplet running BIND with DigitalOcean's DNS servers. It removes the need for running 2 droplets to run your 
own 2-nameserver setup and also means you get to take advantage of DO's far better DNS infrastructure.

Usage:

1. sudo pip install requests
2. Create a settings.py file in the project directory (it's listed in .gitignore so won't be committed) containing 
2 variables: ip is the IP address of the server you are syncing and auth_token is your DigitalOcean API token.
3. Either run:```python sync_dns.py``` to do a complete wipe of all zones that are on the server and a re-sync from 
scratch. It won't wipe domains from DigitalOcean's DNS it doesn't find on the server so you are free to use DO's DNS 
for extra domains if you wish. Or alternatively run:```python sync_dns.py domainname```to do an intelligent sync of 
just that domain.
4. Check your DO DNS entries to make sure it's correct then set your nameservers to ns1.digitalocean.com, 
ns2.digitalocean.com and ns3.digitalocean.com
