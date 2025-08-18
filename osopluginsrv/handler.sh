#!/bin/bash
# Read request line
read REQUEST
METHOD=$(echo "$REQUEST" | cut -d" " -f1)
PATH=$(echo "$REQUEST" | cut -d" " -f2)

# Read headers and capture Content-Length
CONTENT_LENGTH=0
while read line; do
  [ "$line" = $'\r' ] && break
  if [[ "$line" =~ ^Content-Length:\ ([0-9]+) ]]; then
    CONTENT_LENGTH=${BASH_REMATCH[1]}
  fi
done

if [ "$METHOD" = "GET" ]; then
  if [ -f "./tx.json" ]; then
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
    /usr/bin/cat "./tx.json"
  else
    echo -e "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n"
    echo "File not found"
  fi

elif [ "$METHOD" = "POST" ]; then
  BODY=$(/usr/bin/dd bs=1 count=$CONTENT_LENGTH 2>/dev/null)   # read POST body from stdin
  echo "$BODY" > /tmp/received.json

  echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
  echo "{\"status\":\"saved\",\"file\":\"/tmp/received.json\"}"

else
  echo -e "HTTP/1.1 405 Method Not Allowed\r\n"
fi

