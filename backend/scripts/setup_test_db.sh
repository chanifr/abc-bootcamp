#!/bin/bash
# Setup test database

echo "Creating test database..."
docker compose exec -T db mysql -u root -prootpass123 -e "CREATE DATABASE IF NOT EXISTS hellio_hr_test;"
docker compose exec -T db mysql -u root -prootpass123 -e "GRANT ALL PRIVILEGES ON hellio_hr_test.* TO 'hellio'@'%';"
docker compose exec -T db mysql -u root -prootpass123 -e "FLUSH PRIVILEGES;"
echo "Test database created successfully!"
