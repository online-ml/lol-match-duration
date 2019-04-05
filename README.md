# League of Legends match duration forecasting

## Usage

### Development

Create an `.env` file with the following structure:

```sh
RIOT_API_KEY=https://developer.riotgames.com/
```

You first have to build the stack.

```sh
docker-compose build
```

You can then start the stack.

```sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

You only have to build the stack once. However you have to rebuild it if you add or modify a service. You can now navigate to the following pages:

- `localhost:8000` for the app
- `localhost:8082` for [Redis Commander](http://joeferner.github.io/redis-commander/)

The following commands should suffice to cover most use cases.

```sh
# Start the stack
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Visualize application logs
docker-compose logs

# Remove all existing containers
docker rm -f $(docker ps -a -q)

# Remove unused volumes
docker volume prune

# Delete everything (use with care)
docker stop $(docker container ls -a -q) && docker system prune -a -f --volumes
```

### Production

Create an `.env` file with the following structure:

```sh
SECRET_KEY=Keep_it_secret,_keep_it_safe
RIOT_API_KEY=https://developer.riotgames.com/
REDIS_PASSWORD=redis
ADMIN_PASSWORD=creme
```

## Useful resources

- [MDN Django guide](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django)
- [Separation of business logic and data access in Django](separation-of-business-logic-and-data-access-in-django)
- [How To Remove Docker Images, Containers, and Volumes](https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes)
- [Clean out your Docker images, containers and volumes with single commands](https://medium.com/the-code-review/clean-out-your-docker-images-containers-and-volumes-with-single-commands-b8e38253c271)
