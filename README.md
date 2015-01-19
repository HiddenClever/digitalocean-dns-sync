# DigitalOcean DNS Synchronisation
DigitalOcean offers a fantastic DNS service but it is time consuming and cumbersome to manually update it if you 
have a droplet running a control panel that generates DNS records as part of domain management (e.g. cPanel, 
DirectAdmin etc).

This python script will synchronise the DNS records from any droplet running BIND with DigitalOcean's 
DNS servers. It removes the need for 2 droplets to run your own 2-nameserver setup and also means you get to take 
advantage of DO's far better DNS infrastructure.

###Usage###

0. Generate a personal access token from https://cloud.digitalocean.com/settings/applications if you haven't got one 
already.
1. Run ```sudo pip install requests``` or install the Python Requests library however you would normally 
http://docs.python-requests.org/en/latest/.
2. Create a settings.py file in the project directory (it's listed in .gitignore so won't be committed) containing 
2 variables: ip is the IP address of the server you are syncing and auth_token is your DigitalOcean API Personal Access
Token.
3. Either run:```python sync_dns.py``` to do a complete wipe of DO's records for all domains that are on the droplet and
re-sync from scratch. It won't wipe domains from DO's DNS it doesn't find on the server so you are free to use it 
for extra domains if you wish. Or alternatively run:```python sync_dns.py domainname```to do an intelligent sync of 
just that domain.
4. Check your DO DNS entries to make sure it's correct then set your nameservers to ns1.digitalocean.com, 
ns2.digitalocean.com and ns3.digitalocean.com or follow this tutorial 
https://www.digitalocean.com/community/tutorials/how-to-create-vanity-or-branded-nameservers-with-digitalocean-cloud-servers 
to brand your own nameservers.

###Credit###

Initial inspiration came from here https://cloud.google.com/dns/migrating-bind-zone-python
