#!/bin/bash

# Clears the sync queue of any existing tasks for the specified domain
# This ensures the most recent command is run
clear_sync_queue() {
    for job in $(atq | cut -f 1)
    do
        SCHEDULED=`at -c $job | ack-grep "sync_dns.py $1" | wc -l`
        if [ "$SCHEDULED" -gt "0" ]
        then
            atrm $job
        fi
    done
    return 0
}
