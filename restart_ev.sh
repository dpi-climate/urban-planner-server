#!/bin/bash

while true; do
    /home/carolvfs/anaconda3/envs/env_ejust/bin/python app.py --cert="/etc/ssl/certs/_.evl.uic.edu.crt" --key="/etc/ssl/private/_.evl.uic.edu.key"
    if [ $? -ne 0 ]; then
        echo "Script crashed with error code $?. Restarting..." >&2
        sleep 5  # Wait for 5 seconds before restarting
    else
        break  # Exit the loop if the script ends without error
    fi
done

