#!/bin/bash
docker compose down -v
sleep 5
docker compose up -d
sleep 10
docker exec -i linkace_dev-php-1 php artisan migrate --force
docker exec -i linkace_dev-php-1 php artisan setup:complete
docker exec -i linkace_dev-php-1 php artisan registeruser --admin <<EOF
wajdi
wagde.abo164@gmail.com
password
EOF
