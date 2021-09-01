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
  echo -e "\nip = \"$ip\"\n\nauth_token = \"$auth_token\"" > sync_dns_settings.py
  echo "Settings file created"
fi

echo -e "\nInstalling sync scripts"
cp sync_dns.py /usr/local/directadmin/scripts/custom/
cp sync_dns_settings.py /usr/local/directadmin/scripts/custom/
cp sync_dns_functions.sh /usr/local/directadmin/scripts/custom/
echo "--> Done"

echo -e "\nCreating DirectAdmin custom scripts"

HEADER="#!/bin/bash\n"
CLEARQUEUE="source /usr/local/directadmin/scripts/custom/sync_dns_functions.sh\n\nclear_sync_queue"
DIR="/usr/local/directadmin/scripts/custom"
CMD="python $DIR/sync_dns.py"

if [ ! -f $DIR/domain_change_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/domain_change_post.sh
fi
echo -e "$CLEARQUEUE \$domain\n\necho \"$CMD \$domain --delete\" | at now + 1 minute > /dev/null 2>&1\n" >> $DIR/domain_change_post.sh
echo -e "clear_sync_queue \$newdomain\n\necho \"$CMD \$newdomain\" | at now + 1 minute > /dev/null 2>&1\n\necho \"DNS records will sync in 1 minute\"" >> $DIR/domain_change_post.sh

if [ ! -f $DIR/domain_create_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/domain_create_post.sh
fi
echo -e "$CLEARQUEUE \$domain\n\necho \"$CMD \$domain\" | at now + 1 minute > /dev/null 2>&1\necho \"DNS records will sync in 1 minute\"" >> $DIR/domain_create_post.sh

if [ ! -f $DIR/domain_destroy_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/domain_destroy_post.sh
fi
echo -e "$CLEARQUEUE \$domain\n\necho \"$CMD \$domain --delete\" | at now + 1 minute > /dev/null 2>&1\necho \"DNS records will sync in 1 minute\"" >> $DIR/domain_destroy_post.sh

if [ ! -f $DIR/domain_pointer_create_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/domain_pointer_create_post.sh
fi
echo -e "$CLEARQUEUE \$DOMAIN\n\necho \"$CMD \$DOMAIN\" | at now + 1 minute > /dev/null 2>&1\necho \"DNS records will sync in 1 minute\"" >> $DIR/domain_pointer_create_post.sh

if [ ! -f $DIR/domain_pointer_destroy_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/domain_pointer_destroy_post.sh
fi
echo -e "$CLEARQUEUE \$from\n\necho \"$CMD \$from --delete\" | at now + 1 minute > /dev/null 2>&1\necho \"DNS records will sync in 1 minute\"" >> $DIR/domain_pointer_destroy_post.sh

if [ ! -f $DIR/dns_write_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/dns_write_post.sh
fi
echo -e "$CLEARQUEUE \$DOMAIN\n\necho \"$CMD \$DOMAIN\" | at now + 1 minute > /dev/null 2>&1\necho \"DNS records will sync in 1 minute\"" >> $DIR/dns_write_post.sh

if [ ! -f $DIR/subdomain_create_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/subdomain_create_post.sh
fi
echo -e "$CLEARQUEUE \$domain\n\necho \"$CMD \$domain\" | at now + 1 minute > /dev/null 2>&1\necho \"DNS records will sync in 1 minute\"" >> $DIR/subdomain_create_post.sh

if [ ! -f $DIR/subdomain_destroy_post.sh ]; then
  # If the script doesn't exist, create the header
  echo -e $HEADER > $DIR/subdomain_destroy_post.sh
fi
echo -e "$CLEARQUEUE \$domain\n\necho \"$CMD \$domain --delete\" | at now + 1 minute > /dev/null 2>&1\necho \"DNS records will sync in 1 minute\"" >> $DIR/subdomain_destroy_post.sh

echo "--> Done"

echo -e "\nSetting permissions"
chown -R diradmin:diradmin /usr/local/directadmin/scripts/custom/*
chmod -R +x /usr/local/directadmin/scripts/custom/*.sh
echo "--> Done"

echo -e "\n\nDirectAdmin-DigitalOcean DNS Sync Installation Complete\n"
