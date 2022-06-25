This folder is empty and will be used for sharing files between celery and flask instances.

In details, Flask API will request Celery to process some tasks. As result of our tasks are files, we need to store and share them. That's why this folder is serving us the shared folder functionality. It's being reference in both `worker` and `api` services in `docker-compose.yml`.