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
  echo $'\n'"ip = \"$ip\""$'\n\n'"auth_token = \"$auth_token\"" > sync_dns_settings.py
  echo "Settings file created"
  #echo $auth_token
fi

echo $'\n'"Installing scripts"
cp sync_dns.py /usr/local/directadmin/scripts/custom/
cp sync_dns_settings.py /usr/local/directadmin/scripts/custom/
echo "--> Done"

echo $'\n'"Creating DirectAdmin custom scripts"
if [ ! -f /usr/local/directadmin/scripts/custom/domain_post_create.sh ]; then
  # If the script doesn't exist, create the header
  echo "#!/bin/bash"$'\n' > /usr/local/directadmin/scripts/custom/domain_post_create.sh
fi
echo "python /usr/local/directadmin/scripts/custom/sync_dns.py \$domain" >> /usr/local/directadmin/scripts/custom/domain_post_create.sh
echo "--> Done"

if [ ! -f /usr/local/directadmin/scripts/custom/domain_create_post.sh ]; then
  # If the script doesn't exist, create the header
  echo "#!/bin/bash"$'\n' > /usr/local/directadmin/scripts/custom/domain_post_create.sh
fi
echo "python /usr/local/directadmin/scripts/custom/sync_dns.py \$domain at now + 2 minutes" >> /usr/local/directadmin/scripts/custom/domain_post_create.sh
echo "--> Done"

echo $'\n'"Setting permissions"
chown -R diradmin:diradmin /usr/local/directadmin/scripts/custom/*
echo "--> Done"
