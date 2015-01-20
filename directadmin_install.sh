#!/bin/bash

if [ ! -f sync_dns_settings.py ]; then
  while true; do
    read -p "What is the IP address of the server you are syncing from? " ip
    if [[ "$ip" ]]; then
      break;
    fi
  done
  while true; do
    read -p "What is your DigitalOcean Personal Access Token? " auth_token
    if [[ "$auth_token" ]]; then
      break;
    fi
  done
  echo $'\n'"ip = \"$ip\""$'\n\n'"auth_token=\"$auth_token\"" >> sync_dns_settings.py
  echo "Settings file created"
  #echo $auth_token
fi

echo $'\n'"Installing scripts"
cp sync_dns.py /usr/local/directadmin/scripts/custom/
cp sync_dns_settings.py /usr/local/directadmin/scripts/custom/
echo "--> Done"

echo $'\n'"Copying DirectAdmin custom scripts"
if [ ! -f /usr/local/directadmin/scripts/custom/domain_post_create.sh ]; then
  # If the script doesn't exist, create the header
  echo "#!/bin/bash"$'\n\n' >> /usr/local/directadmin/scripts/custom/domain_post_create.sh
fi
echo "python /usr/local/directadmin/scripts/custom/digitalocean-dns-sync/sync_dns.py \$domain" > /usr/local/directadmin/scripts/custom/domain_post_create.sh
