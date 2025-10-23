#! /bin/bash
#
# Tries to open all ports specified in docker-compose.yml to see if they are available
#

if [ $# -ge 1 ]; then
    DCOMPOSE=$1
else
    DCOMPOSE=$(realpath $(dirname $0)/..)/config/dev/cab-standalone/docker-compose.yml
fi
if [ ! -r "$DCOMPOSE" ]; then
    echo "Usage: $0 [ <path to docker-compose.yml file> ]"
    echo "Can't open $DCOMPOSE"
    exit 1
fi
which docker >/dev/null
if [ $? -ne 0 ]; then
    echo "Usage: $0 [ <path to docker-compose.yml file> ]"
    echo "Can't find docker command"
    exit 2
fi

PORTS=$(sed -e 's/#.*//' $DCOMPOSE | egrep "[ '\"][0-9]+:[0-9]+" | sed -e 's/^[^0-9]*//' -e 's/:.*//'i | sort -nu | tr '\n' ' ' )
echo "Ports used for InteractiveAI: $PORTS"
NOK=0
for port in $PORTS; do
    docker run -p $port:80 hello-world >/dev/null
    if [ $? -ne 0 ]; then
        let NOK=$NOK+1
    fi
done
if [ $NOK -eq 0 ]; then
    echo "All is fine: all ports used by InteractiveAI are available"
else
    echo "Check your counfiguration: $NOK port(s) used by InteractiveAI are already used"
    echo "InteractiveAI can't run on this platform with this $DCOMPOSE ports configuration"
fi
exit $NOK
