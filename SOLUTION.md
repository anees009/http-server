# Building a simple HTTP API service and Deploying it on Kubernetes - Minikube.

The solution contains code that 
1) Builds a python app using Flask that performs basic CRUD operations
2) Deploys the app to any kubernetes cluster

## Prerequisites
1. Have `Docker` and the `Kubernetes CLI` (`kubectl`) installed together with `Minikube`

## Features

The below are the list of features of this python `restapi` app.

* The following endpoints are accessible
```
| Name   | Method      | URL               
| ---    | ---         | ---
| List   | `GET`       | `/configs`
| Create | `POST`      | `/configs`
| Get    | `GET`       | `/configs/{name}`
| Update | `PUT`       | `/configs/{name}`
| Delete | `DELETE`    | `/configs/{name}`
```
* The application exposes metrics in Prometheus format - metric type: `Counter`.

* All application logging is structured in JSON format to stdout.

* Distributed tracing data is published in Jaeger format (No testing done for this feature).

## Building blocks

The application is built using Flask framework for its ease and simplicity in implemention of REST APIs.
The clients and libraries used in this application are:
    * `python-json-logger` - Used as a JsonFormatter to get logs in json format
    * `marshmallow` -  It is a framework-agnostic library for converting complex datatypes, such as objects, to and from native Python datatypes. This is used extensively in the implementation of `config Schema`. Serialization and de-serialization of data is achived by using this libarary. This is used to handle nested schema.
    * `jaeger_client` and `flask_opentracing` - A python client to implement jaeger tracing for flask app

## Project structure

```
$ tree
.
├── Dockerfile
├── README.md
├── SOLUTION.md
├── bootstrap.sh
├── requirements.txt
├── restapi
│   ├── __init__.py
│   ├── main.py
│   ├── model
│   │   ├── __init__.py
│   │   ├── configs.py
│   │   └── metrics_exporter.py
│   └── unittests
│       ├── __init__.py
│       └── test_models_config.py
└── restapi-deployment.yml

3 directories, 13 files
```

## Code Walk-thru

* `main.py` - It is the main file, all the routes are defined here, Before starting, the app is initialize with a small dataset to work with.
* `configs.py` - A seperate library to handle the data-structure of configs, Using `marshmallow` data-structure is defined and all operations related to serialization and de-serialization of data is done here, `class Configs():` implements the required nested schema.
* `metrics_exporter` - A promethues metrics exporter (adapter) is implemented, This is a ground up approch to collect metrics in prometheus format, We can achive metrics collection using promethues python client, but that would be a straight forward way (I was unsure whether it is allowed for this test).
* `restapi-deployment.yml` - Kubernetes manifests, pip requirements in `requirements.txt` and a `Dockerfile` to build docker image.
* `test_models_config.py` - Unit tests

## How to Run locally

* Clone the repo
* pip install requirements.txt
```
pip install -r requirements.txt 
```
* export environment variable `SERVE_PORT` to any port and run `bootstrap.sh`
```
export SERVE_PORT=4999
chmod +x bootstrap.sh
./bootstrap.sh
```
`bootstrap.sh` defaults python to python3, if your environment has both python and python3, edit the `bootstrap.sh` file to point to python3
* curl endpoints
```
curl http://localhost:4999/configs

curl http://localhost:4999/configs/<dcname>

curl -X POST -H "Content-Type: application/json" -d '{"dcname": "datacenter-5425", "metadata": { "limits": { "cpu": { "enabled": true} }, "monitoring": { "enabled": false } } }' http://localhost:4999/configs

curl -X DELETE http://localhost:4999/configs/<dcname>

```
 * Query Promethues metrics
```
curl http://localhost:4999/metrics

# HELP http_requests_config The total number of HTTP requests for /config.
# TYPE http_requests_config counter
http_requests_config{endpoint="/configs", method="get", code="200"} 3
# HELP http_requests The total number of HTTP requests.
# TYPE http_requests counter
http_requests{method="post", code="204"} 1
http_requests{method="post", code="403"} 1
http_requests{method="delete", code="204"} 1
http_requests{method="delete", code="404"} 3
```
## Build docker image and run locally

* Build docker
```
docker build . -t restapi-image
```
* Run by specifing the environment variable `SERVE_PORT`
```
export SERVE_PORT=4999
docker run -d -e SERVE_PORT=$SERVE_PORT -p $SERVE_PORT:$SERVE_PORT --name restapi_docker restapi-image
```
* curl the endpoints
```
curl http://localhost:<PORT>/configs/
curl http://localhost:<PORT>/configs/datacenter-1
curl -X DELETE http://localhost:<PORT>/configs/datacenter-1
curl -X DELETE http://localhost:<PORT>/configs/datacenter-1
```
* Discover logs
```
$ docker logs ba4e49e80ea8
* Serving Flask app './restapi/main.py'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://172.17.0.2:5001
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 133-551-471
{"asctime": "2022-10-24 18:22:55,088", "levelname": "INFO", "funcName": "get_all_configs", "message": "Retriving all configs"}
172.17.0.1 - - [24/Oct/2022 18:22:55] "GET /configs HTTP/1.1" 200 -
{"asctime": "2022-10-24 18:23:01,029", "levelname": "INFO", "funcName": "get_config", "message": "GET: /configs/datacenter-1"}
172.17.0.1 - - [24/Oct/2022 18:23:01] "GET /configs/datacenter-1 HTTP/1.1" 200 -
{"asctime": "2022-10-24 18:23:17,568", "levelname": "INFO", "funcName": "delete_config", "message": "DELETE: Deleting config datacenter-1."}
```
## Deploy to kubernetes

* Install kubectl and minikubeStart the minikube, 
* Make Docker CLI uses the Docker deamon
```
eval $(minikube docker-env)
```
* Start minikube
```
minikube start
```
* Build the docker image, ignore if already exisits
```
docker build . -t restapi-image
```
Please do not change the image name, as kubenetes manifests refer to this image
* Kubernetes apply
```
kubectl apply -f restapi-deployment.yml
```
* Check if all pods come up
```
$ kubectl get po
NAME                                  READY   STATUS    RESTARTS   AGE
restapi-deployment-76f9968bbd-b55b8   1/1     Running   0          45m
restapi-deployment-76f9968bbd-c22n6   1/1     Running   0          45m
restapi-deployment-76f9968bbd-pdj48   1/1     Running   0          45m
```
* Expose the app to outside environment, This is similar to using a NodePort.
```
$minikube service restapi-service --url
http://127.0.0.1:56852
❗  Because you are using a Docker driver on darwin, the terminal needs to be open to run it.
```
* curl the url provided
```
curl http://127.0.0.1:56852/configs

[
  {
    "dcname": "datacenter-1",
    "metadata": {
      "limits": {
        "cpu": {
          "enabled": true,
          "value": "500m"
        }
      },
      "monitoring": {
        "enabled": true
      }
    }
  },
  {
    "dcname": "datacenter-2",
    "metadata": {
      "limits": {
        "cpu": {
          "enabled": true,
          "value": "500m"
        }
      },
      "monitoring": {
        "enabled": true
      }
    }
  }
]
```
## Scope for improvements

* Using a database would help persist data and also help in case of distributed app deployment (kubernetes). No database is used in the current implementation
* Using promethues python client will help collect a wide veriety of metrics across all metric types, `Counter`, `Guage` and `Histogram`
* Improve logging
* Memory management for kubernetes pods would help isolate the app from causing any disruptions to other services
* To access kubernetes app we use minikube inbuilt service, for local kubernetes `kind` cluster we could use NodePort, For production instances we can improve to use IngressController.