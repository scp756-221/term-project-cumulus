[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-f059dc9a6f8d3a56e377f745f24479a46679e63a5d9fe6f495e02850cd0d8118.svg)](https://classroom.github.com/online_ide?assignment_repo_id=7162630&assignment_repo_type=AssignmentRepo)
# SFU CMPT 756 main project directory

This is the repo for CMPT 756 Project (Spring 2022).

Our project 

## Main Directories

`cluster`: Cluster and Service Configuration Files
`db`: Database service
`gatling`: Gatling script to perform load testing
`loader`: Loader service to populate the database
`logs`: Log Files
`s1`: User service
`s2`: Book service
`s3`: Checkout service
`tools`: Make 

## Setup 

1. For our project, we have used Google Cloud Platform for deploying our application. Install [Google Cloud SDk](https://cloud.google.com/sdk/docs/install) on the local machine.

2. Download and install [istioctl](https://istio.io/latest/docs/setup/getting-started/#download).

3. Install [helm](https://helm.sh/docs/helm/helm_install/).

### Instantiate the template files

#### Fill in the required values in the template variable file

Copy the file `cluster/tpl-vars-blank.txt` to `cluster/tpl-vars.txt`
and fill in all the required values in `tpl-vars.txt`.  These include
things like your AWS keys, your GitHub signon, and other identifying
information.  See the comments in that file for details.

Once you have filled in all the details, run

~~~
$ make -f k8s-tpl.mak templates
~~~

### Creating the cluster:
Start the cluster by going to project root directory and using command:

~~~
make -f gcp.mak start
~~~

### Setup the configuration for `Kubenetes`:
~~~
# Create c756ns namespace inside each cluster and set each context to use
$ kubectl config use-context gcp756
$ kubectl create ns c756ns
$ kubectl config set-context gcp756 --namespace=c756ns
~~~

### Build Docker images and push it to ghcr (Container Registry)

Build images for the database service, user service, book service, checkout service, and the data loader. After running this command, you may go to Github packages and make each image public.

~~~
make -B -f k8s.mak cri
~~~

### Deploy the Services

To deploy our services on the cluster, run the below commmand:

~~~
make -f k8s.mak provision`  
~~~

This installs service mesh and istio to enable injection. Also, it will run the cloudformation stack to create DynamoDB tables and loader to initialize data in the DynamoDB tables.

To clear the deployed services from your cluster, run:

~~~
make -f k8s.mak scratch
~~~

To update your services, run:
~~~
make -f k8s.mak rollout
~~~

### Get external IP of our application

To send requests to our application, we can get the external IP of our application by running:

~~~
kubectl -n istio-system get service istio-ingressgateway | cut -c -140
~~~

#### Get grafana url: 

~~~
make -f k8s.mak grafana-url 
~~~
 
#### Get prometheus url: 

~~~
make -f k8s.mak prometheus-url 
~~~

#### Get kiali url: 

~~~
# Install kiali before getting the url
make -f k8s.mak kiali
make -f k8s.mak kiali-url 
~~~ 

### Gatling Simulation

The command below can be run to generate test load using Gatling:

~~~
# Replace n with 5, 10 or 50 
bash tools/gatling-n-user.sh
bash tools/gatling-n-book.sh
bash tools/gatling-n-checkout.sh
~~~

The following command stops Gatling jobs that are currently running:

~~~
./tools/kill-gatling.sh
~~~

## Killing the Cluster

~~~
make -f gc.mak stop
~~~