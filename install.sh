docker-compose -f docker-compose-dev.yml build &&
echo "----------------------------Build done----------------------------" &&
docker-compose -f docker-compose-dev.yml run users python3 manage.py recreate-db &&
docker-compose -f docker-compose-dev.yml run ratings python3 manage.py recreate-db &&
docker-compose -f docker-compose-dev.yml run delijnapi python3 manage.py recreate-db &&
echo "----------------------------DBs done----------------------------" &&
docker-compose -f docker-compose-dev.yml run delijnapi python3 manage.py seed-db
echo "----------------------------De Lijn Data fetched----------------------------" &&
docker-compose -f docker-compose-dev.yml up -d &&
echo "Docker online" 