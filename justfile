_default:
    @just --list

build:
    uv run main.py

[working-directory: 'tf']
deploy: build
    GRAFANA_AUTH=$(secret-tool lookup app grafana env prod) terraform apply
