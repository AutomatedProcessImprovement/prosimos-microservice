# Prosimos API (backend)

## Start the API via the docker
1) `docker build --progress=plain --no-cache -f Dockerfile.api -t prosimos-api .`
2) `docker run --rm -p 5000:5000 prosimos-api`

## Release the new version of the API docker image
1) Build the image from the current code version.
    ```
    docker build --progress=plain --no-cache -f Dockerfile.api -t prosimos-api .
    ```

2) Get the image id of the created image in step 1
    ```
    docker images prosimos-api
    ```

3) Tag the image specifying the version we will be releasing, e.g. `0.1.2`
    ```
    docker tag 39a635198e63 irynahalenok/prosimos-api:0.1.2
    ```

4) Push the created version to the Docker hub
    ```
    docker push irynahalenok/prosimos-api:0.1.2
    ```

5) Tag the created version in git
    ```
    git tag v0.1.2 <SHA>
    ```
    where `<SHA>` should be changed to the SHA of the last commit in the release.

6) Push the created tag
    ```
    git push origin v0.1.2
    ```