# Prosimos API (backend)

## Start the API via the docker
1) `docker build --progress=plain --no-cache -f Dockerfile.api -t prosimos-api .`
2) `docker run --rm -p 5000:5000 prosimos-api`

## Access API endpoints 

<details>
    <summary>Curl</summary>

1. Discover simulation parameters based on logs. 
```
curl -X POST "http://localhost:5000/api/discovery" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "bpmnFile=@purchasing_example.bpmn" -F "logsFile=@PurchasingExample.xes"
```
where `@purchasing_example.bpmn` and `@PurchasingExample.xes` should be replaced with the full path to the file on your computer, for example, `@"/Users/iryna/Documents/proposed.json"`

2. Perform the simulation
```
curl -X POST "http://localhost:5000/api/simulate" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "startDate=2022-05-03T12:05:19.1919+03:00" -F "numProcesses=1" -F "modelFile=@purchasing_example.bpmn" -F "simScenarioFile=@discovery_results_mos9tbez.json;type=application/json"
```
where `@purchasing_example.bpmn` and `@discovery_results_mos9tbez.json` should be replaced with the full path to the file on your computer.

3. Get files generated together with the simulation (logs and statistics). 
```
curl -X GET "http://localhost:5000/api/simulationFile?fileName=stats_kjv4fq1r.csv" -H "accept: application/json"
```
where `stats_kjv4fq1r.csv` should be replaced with the filename which you want to get (the filename is being returned on `/api/simulate` call).

</details>

<details>
    <summary>Swagger</summary>

To access Swagger and perform API calls directly from the web browser, you can access <http://localhost:5000/apidocs/>

![swagger-ui](https://user-images.githubusercontent.com/14131790/168087906-19788c31-9d2d-4f30-9401-7d05ddd94f54.png)
</details>


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