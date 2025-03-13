# Panel mill

This is a prototype library to programmatically build Grafana dashboards using the Grafana Foundation SDK. There are no tests, no linters, no documentation.

## Adding new dashboards

1. Add a new dashboard definition in `./dashboards`. You can use the existing dashboards as a model.
2. Add the class Path to the dashboard class and a JSON file name to `./main.py`.

## Building JSON models for dashboards

Running `just build` generates a JSON file for each dashboard in `./build`. You can manually import these files into Yardstick.

## Deploying dashboards with Terraform

This repository contains Terraform code to deploy dashboards to Yardstick. The code is currently hard-wired to write dahboards to the Folder "sven". If you want to use the code, you need to make the following changes:

1. Create your own folder in Yardstick.
2. Change the Terraform code to point to that folder.
3. Change the UIDs of all dashboards in `./dashboards`. Dashboard UIDs must be unique.
4. Create a service account in Yardstick with the "Editor" role.
5. Create an auth token for the service account and store it in your operating system's keychain or keyring.
6. Edit `justfile` with the correct command to retrieve the auth token from your OS's keychain.
7. Run `just deploy` to deploy the dashboards.
