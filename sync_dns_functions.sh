#!/bin/bash

# Checks to see whether there is a DNS sync already scheduled
check_sync_scheduled() {
    for job in $(atq | cut -f 1)
    do
        SCHEDULED=`at -c $job | ack-grep "sync_dns.py $1" | wc -l`
        if [ "$SCHEDULED" -gt "0" ]
        then
            return 1
        fi
    done
    return 0
}
