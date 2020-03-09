# RabbitMQ Tutorial

# System Requirements

- Install python 3.x (3.7.x was used)
- Install Docker and docker-compose

# Installation

- Install virtualenv `pip install virtualenv`
- Setup the environment `venv --python=pytho3.7 env`
- Activate the environment
    - Run `source env/bin/activate` (*nix)
    - Run `env/Scripts/activate.bat` (Windows) 
- `pip install -r requirements`

# Usage
- Run the RabbitMQ container via docker compose `docker-compose up -d`
- The [examples](./src/examples) folder holds different scenarios for sending and receiving messages