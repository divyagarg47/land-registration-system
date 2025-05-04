#!/bin/bash
 
# Ensure the CHANNEL_NAME variable is set
if [ -z "$CHANNEL_NAME" ]; then
    echo "Error: CHANNEL_NAME is not set."
    exit 1
fi
 
# Fetch blockchain info
INFO_OUTPUT=$(peer channel getinfo -c $CHANNEL_NAME 2>&1)
 
# Extract height using grep and sed
HEIGHT=$(echo "$INFO_OUTPUT" | grep -oP '(?<=\"height\":)\d+')
 
if [ -z "$HEIGHT" ]; then
    echo "Error: Unable to fetch blockchain height."
    exit 1
fi
 
echo "Blockchain height: $HEIGHT"
 
# Loop through blocks from 0 to height-1
for ((i=0; i<$HEIGHT; i++)); do
    echo "Fetching block $i..."
    peer channel fetch $i block_$i.pb -c $CHANNEL_NAME
    
    echo "Converting block $i to JSON..."
    configtxlator proto_decode --input block_$i.pb --type common.Block | jq '.' > block_$i.json
 
done
 
echo "Getting file sizes..."
ls -lh block_*.pb block_*.json