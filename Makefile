build:
	docker compose up --build
down:
	docker compose down
fulldown:
	docker compose down --volumes --remove-orphans
network-down:
	docker network prune -f
bash:
	docker compose exec -it api bash 
