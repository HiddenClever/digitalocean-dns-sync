import dns.zone
from dns.rdataclass import *
from dns.rdatatype import *
from dns import rdatatype
import requests
import glob
import json
import os.path
import sys

try:
    from sync_dns_settings import ip, auth_token, bindfolder, bindextension
except ImportError:
    print("[ERROR] Please copy sync_dns_settings.py.example to sync_dns_settings.py "
          "and adjust the values with the server ip address and your digitalocean api key. "
          "Also change the bindfolder and bindextension values if they're different on your server.", file=sys.stderr)
    exit()


base_url = "https://api.digitalocean.com/v2/domains"

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(auth_token)}


def handle_error(response):
    msg = None

    if hasattr(response, 'status_code'):
        if response.status_code == 401:
            msg = "\n[ERROR] An authorization error has occurred, please check your auth_token is correct."
        elif response.status_code == 404:
            # This is a non-fatal error
            print("--> Not found, continuing")
            return
        elif response.status_code == 429:
            msg = "\n[ERROR] You have exceeded DigitalOcean's Rate Limit of 1200 requests per hour. " \
                  "Please wait an hour before trying again and type the last domain synchronised when prompted."

    if msg is None:
        msg = "\n[ERROR] An unknown error has occurred, please re-run the script."
    print(msg, file=sys.stderr)

    if hasattr(response, 'status_code'):
        print("Response status code:", response.status_code, file=sys.stderr)

    try:
        content_msg = json.loads(response.content)['message']
        print("Response message:", content_msg, file=sys.stderr)
    except AttributeError:
        debug_msg = json.dumps(response, indent=4, sort_keys=True)
        print("Response body:", debug_msg, file=sys.stderr)

    exit()


def qualifyName(dnsName, domain):
    dnsName = str(dnsName)
    if domain not in dnsName and dnsName != '@':
        return dnsName + '.' + domain + '.'
    else:
        # Catches the @ symbol case too.
        return domain + '.'


def check_domain(domain_records_url, domain):
    print("\nChecking DigitalOcean DNS for", domain)
    response = requests.get(domain_records_url, headers=headers)

    if response.status_code == 200:
        print("--> Domain records found")
    elif response.status_code == 404:
        print("--> Domain records not found, creating zone")

        data = {"name": domain, "ip_address": ip}
        response = requests.post(base_url, data=json.dumps(data), headers=headers).json()

        if 'domain' in response and 'name' in response['domain'] and response['domain']['name'] == domain:
            print("--> Successfully created zone for", domain)

            # Wipe the default DigitalOcean records
            wipe_zone(domain_records_url)
        else:
            handle_error(response)
    else:
        handle_error(response)


def sync_zone(domain_records_url, domain):
    # Synchronise zone
    print("\nSynchronising DNS zone for", domain, "...")

    # First get all the existing records
    existing_records = requests.get(domain_records_url+"?per_page=9999", headers=headers).json().get('domain_records', [])

    # Create an array to hold all the updated records
    updated_records = []

    # Create an array to hold synchronised record IDs
    synced_record_ids = []

    # Get the BIND raw DNS dump
    bindfile = bindfolder + domain + bindextension
    with open(bindfile, "r") as dns_file:
        dns_dump = dns_file.read()

    dns_dump = "$ORIGIN {0}.\n{1}".format(domain, dns_dump)

    zone = dns.zone.from_text(dns_dump)

    for name, node in zone.nodes.items():
        name = str(name)
        print("\nRecord name:", name)
        print("Qualified name:", qualifyName(name, domain))

        rdatasets = node.rdatasets
        for rset in rdatasets:
            print("--> TTL:", str(rset.ttl))
            print("--> Type:", rdatatype.to_text(rset.rdtype))
            for rdata in rset:
                data = None
                priority = None
                port = None
                weight = None
                if rset.rdtype == MX:
                    priority = rdata.preference
                    print("--> Priority:", priority)
                    if str(rdata.exchange) == "@":
                        data = "%s." % (domain)
                    else:
                        data = "%s.%s." % (rdata.exchange, domain)
                    data = rdata.exchange
                elif rset.rdtype == CNAME:
                    if str(rdata) == "@":
                        data = "@"
                    else:
                        data = rdata.target
                elif rset.rdtype == A:
                    data = rdata.address
                elif rset.rdtype == AAAA:
                    data = rdata.address.lower()
                elif rset.rdtype == NS:
                    data = rdata.target
                elif rset.rdtype == SRV:
                    priority = rdata.priority
                    weight = rdata.weight
                    port = rdata.port
                    data = rdata.target
                elif rset.rdtype == TXT:
                    data = rdata.to_text()
                if data:
                    print("--> Data:", data)

                    data = str(data)
                    type = rdatatype.to_text(rset.rdtype)

                    # Try and find an existing record
                    record_id = None
                    for record in existing_records:
                        if type in ["CNAME", "MX", "NS", "SRV"] and data[-1:] == ".":
                            check_data = data[:-1]
                        else:
                            check_data = data
                        if record['name'] == name and record['type'] == type and record['data'] == check_data:
                            record_id = record['id']
                            synced_record_ids.append(record_id)
                            break

                    if record_id:
                        print("--> Already exists, skipping")
                    else:
                        if type in ["CNAME", "MX", "NS", "SRV"] and data != "@" and data[-1:] != ".":
                            data = "{0}.{1}.".format(data, domain)
                        post_data = {
                            "type": type,
                            "name": name,
                            "data": data,
                            "priority": priority,
                            "port": port,
                            "weight": weight
                        }
                        # Collect records to be updated into the updated_records array
                        print("--> Queuing to update")
                        updated_records.append(post_data)

    # Delete any records that exist with DigitalOcean that have been removed
    print("\nRemoving deleted records")
    for record in existing_records:
        if record['id'] not in synced_record_ids and record['type'] != 'SOA':
            response = requests.delete("{0}/{1}".format(domain_records_url, record["id"]), headers=headers)
            if response.status_code == 204:
                print("--> Deleted record", record["name"], "IN", record["type"], record["data"])
            else:
                handle_error(response)
    print("--> Done")

    # Finally, post the responses for the updated records
    print("\nPosting updated records")
    for record in updated_records:
        response = requests.post(domain_records_url, data=json.dumps(record), headers=headers).json()
        if 'domain_record' in response:
            print("--> Updated record", record["name"], "IN", record["type"], record["data"])
        else:
            handle_error(response)
    print("--> Done")

    print("\n--> Complete\n")


def wipe_zone(domain_records_url):
    # Wipe all the existing records for a given domain
    print("\nWiping default DigitalOcean records...")

    response = requests.get(domain_records_url, headers=headers).json()
    # print("Response body:", json.dumps(response, indent=4, sort_keys=True)
    if 'domain_records' in response:
        for record in response['domain_records']:
            response = requests.delete("{0}/{1}".format(domain_records_url, record["id"]), headers=headers)
            if response.status_code == 204:
                print("--> Deleted record", record["type"], record["data"])
            elif response.status_code == 422:
                print("--> SOA record detected, ignoring")
            else:
                handle_error(response)
        print("--> Done")
    else:
        handle_error(response)


if __name__ == '__main__':
    args = sys.argv
    if "--delete" in args:
        args.remove("--delete")
        delete = True
    else:
        delete = False
    if len(args) == 1:
        print("You have not specified a domain, would you like to wipe and re-sync all domains in the system?")
        sync_all = input("Please type y or n: ")
        print("Did you run this previously and reach the DigitalOcean API limit?")
        resume_domain = input("If so type the last domain name here to resume: ")
        if sync_all == "y":
            found = False
            for filename in sorted(glob.glob(bindfolder + "*" + bindextension)):
                domain = os.path.basename(filename)[:-3]
                domain_url = base_url + "/{0}".format(domain)
                domain_records_url = "{0}/records".format(domain_url)

                if resume_domain:
                    if resume_domain == domain:
                        found = True
                    if not found:
                        continue

                # 1. Delete the domain. We do this because it is quicker than wiping each record individually.
                print("\nDeleting", domain, "...")
                response = requests.delete(domain_url, headers=headers)
                if response.status_code == 204:
                    print("--> Done")
                else:
                    handle_error(response)

                # 2. Re-create the domain
                check_domain(domain_records_url, domain)

                # 3. Sync zone
                sync_zone(domain_records_url, domain)
        else:
            exit()
    elif len(args) == 2:
        domain_url = base_url + "/{0}".format(args[1])
        if delete:
            print("\nDeleting", args[1], "...")
            response = requests.delete(domain_url, headers=headers)
            if response.status_code == 204:
                print("--> Done")
            else:
                handle_error(response)
        else:
            domainfile = bindfolder + args[1] + bindextension
            if os.path.isfile(domainfile):
                domain_records_url = "{0}/records".format(domain_url)
                check_domain(domain_records_url, args[1])
                sync_zone(domain_records_url, args[1])
            else:
                print("[ERROR] Could not find zone file for {0}".format(args[1]), file=sys.stderr)
    else:
        print("You have supplied too many arguments. Usage:")
        print("python sync_dns.py will wipe and re-sync all DNS records in the droplet")
        print("python sync_dns.py domainname will do an intelligent sync of just that domain")
        print("python sync_dns.py domainname --delete will delete the domain record")
