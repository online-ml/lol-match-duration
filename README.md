# League of Legends match duration forecasting

## Usage

### Development

You first have to build the stack.

```sh
docker-compose build
```

You only have to build the stack once. However you have to rebuild it if you add or modify a service. You can then start the stack.

```sh
docker-compose up
```

You can now navigate to the following pages:

- `localhost:8000` for the app
- `localhost:8082` for [Redis Commander](http://joeferner.github.io/redis-commander/)

The following commands should suffice to cover most use cases.

```sh
# Start the stack
docker-compose up

# Stop the stack
docker-compose down

# Visualize application logs
docker-compose logs

# Remove all existing containers
docker rm -f $(docker ps -a -q)

# Remove unused volumes
docker volume prune
```

### Production

Create a `.env` file with the following structure:

```sh
SECRET_KEY=Keep_it_secret,_keep_it_safe

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

CASSANDRA_USER=cassandra
CASSANDRA_PASSWORD=cassandra

ADMIN_PASSWORD=houdini
```

## Useful resources

- [MDN Django guide](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django)
- [Separation of business logic and data access in Django](separation-of-business-logic-and-data-access-in-django)
- [How To Remove Docker Images, Containers, and Volumes](https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes)
- [Clean out your Docker images, containers and volumes with single commands](https://medium.com/the-code-review/clean-out-your-docker-images-containers-and-volumes-with-single-commands-b8e38253c271)
