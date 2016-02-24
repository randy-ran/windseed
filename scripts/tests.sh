source .env/bin/activate
source scripts/env.sh

export WINDSEED_DBNAME="windseed_test"

sudo -u postgres psql -c "CREATE DATABASE ${WINDSEED_DBNAME} WITH OWNER=${WINDSEED_USER} ENCODING='utf-8';"

python -m windseed.utils.tables

python -m tornado.testing windseed/tests/models/user.py
python -m tornado.testing windseed/tests/models/record.py

sudo -u postgres psql -c "DROP DATABASE ${WINDSEED_DBNAME};"
