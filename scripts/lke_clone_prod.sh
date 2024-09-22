#!/bin/bash
# Downloads a backup of the latest version of the production database from the LKE
# PostgreSQL database in the Akamai cloud and restores it to the local database.

show_help() {
cat << EOF
Usage: ${0##/*} [-h]

Downloads a backup of the latest version of the production database
from the LKE PostgreSQL cluster in Akamai cloud and restores it to
the local development database.

Flags are as follows:

    -h      display this help and exit

Note that you must have the configuration to the cluster in the
.secrets/.pgpass file and you must have updated the cluster access
controls to accept connections from your IP address.
EOF
}

# Parse command line options with getopt
OPTIND=1

while getopts h opt; do
    case $opt in
        h)
            show_help
            exit 0
            ;;
        *)
            show_help >&2
            exit 2
            ;;
    esac
done
shift "$((OPTIND-1))"

# Figure out the absolute directory of the repository root.
REPO="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"

# Specify the .pgpass file for connection to the LKE postgres cluster
export PGPASSFILE="$REPO/.secrets/.pgpass"

if [ ! -f "$PGPASSFILE" ]; then
    echo "$PGPASSFILE does not exist."
    exit 1
fi

# The .pgpass file should be in the form:
# hostname:port:database:username:password
pgpass=$(head -n 1 $PGPASSFILE)
pgpassarr=(${pgpass//:/ })

# Parse the .pgpass file to get the variables needed for pg_dump
hostname=${pgpassarr[0]}
port=${pgpassarr[1]}
dbname=${pgpassarr[2]}
username=${pgpassarr[3]}

# Dump the database
pg_dump -h $hostname -p $port -U $username --no-owner --no-acl -Fc $dbname > $REPO/tmp/ledger.dump

# Restore the database
psql -U django -h localhost -p 5432 -c "DROP DATABASE ledger"
psql -U django -h localhost -p 5432 -c "CREATE DATABASE ledger WITH OWNER django"
pg_restore -d ledger --clean --if-exists --no-acl --no-owner -h localhost -U django $REPO/tmp/ledger.dump

# Cleanup
rm $REPO/tmp/ledger.dump