[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-f059dc9a6f8d3a56e377f745f24479a46679e63a5d9fe6f495e02850cd0d8118.svg)](https://classroom.github.com/online_ide?assignment_repo_id=7162630&assignment_repo_type=AssignmentRepo)
# SFU CMPT 756 main project directory

This is the course repo for CMPT 756 (Spring 2022)

You will find resources for your assignments and term project here.


### 1. Instantiate the template files

#### Fill in the required values in the template variable file

Copy the file `cluster/tpl-vars-blank.txt` to `cluster/tpl-vars.txt`
and fill in all the required values in `tpl-vars.txt`.  These include
things like your AWS keys, your GitHub signon, and other identifying
information.  See the comments in that file for details. Note that you
will need to have installed Gatling
(https://gatling.io/open-source/start-testing/) first, because you
will be entering its path in `tpl-vars.txt`.

#### Instantiate the templates

Once you have filled in all the details, run

~~~
$ make -f k8s-tpl.mak templates
~~~

This will check that all the programs you will need have been
installed and are in the search path.  If any program is missing,
install it before proceeding.

The script will then generate makefiles personalized to the data that
you entered in `clusters/tpl-vars.txt`.

**Note:** This is the *only* time you will call `k8s-tpl.mak`
directly. This creates all the non-templated files, such as
`k8s.mak`.  You will use the non-templated makefiles in all the
remaining steps.

### 2. Ensure AWS DynamoDB is accessible/running

Regardless of where your cluster will run, it uses AWS DynamoDB
for its backend database. Check that you have the necessary tables
installed by running

~~~
$ aws dynamodb list-tables
~~~

The resulting output should include tables `User` and `Music`.

----

## Minikube

**Note:** In the section, all commands are run and tested on Mac operating system. Some command might not work on Windows operating system.

### 1. Follow the link provided below for instruction to install `Minikube` on your local machine:
https://minikube.sigs.k8s.io/docs/start/

### 2. To start the Minikube, run the below command on your local machine:

~~~
$ make -f mk.mak start
~~~

### 3. For external IP of `istio`, open a new window, run: 
(Keep the window open for client to access the cluster!)

~~~
$ minikube tunnel
~~~

**Note:** To use `Minikube` with `istio` (a service mesh that was conceived concurrently with k8s), follow the instructions to install `istio` on your local machine:
(https://istio.io/latest/docs/setup/getting-started/)

~~~
# Download and extract the latest release automatically (Linux or macOS):
$ curl -L https://istio.io/downloadIstio | sh -
~~~
~~~
# Move to the Istio package directory. For example, if the package is istio-1.13.1:
$ cd istio-1.13.1
~~~
~~~
# Add the istioctl client to your path (Linux or macOS):
$ export PATH=$PWD/bin:$PATH
~~~

### 4. Setup the `Kubenetes` on `Minikube`:
~~~
# Create c756ns namespace inside each cluster and set each context to use
$ kubectl config use-context minikube
$ kubectl create ns c756ns
$ kubectl config set-context minikube --namespace=c756ns
~~~
~~~
# Install Istio and label the c756ns namespace
$ kubectl config use-context minikube
$ istioctl install -y --set profile=demo --set hub=gcr.io/istio-release
$ kubectl label namespace c756ns istio-injection=enabled
~~~

### 5. Launch the cliend mcli with the specific Server IP:
~~~
$ make PORT=80 SERVER=host.docker.internal run-mcli
~~~

----

## Deploy New Services

To deploy new services, please always ensure that your template files are up to date. Run this command to update your template files:
```
make -f k8s-tpl.mak templates
```

Build the service images and push them to your container registry:
```
make -f k8s.mak cri
```

Ensure that your cluster is started. To deploy the services, run:
```
make -f k8s.mak deploy
```

To clear the deployed services from your cluster, run:
```
make -f k8s.mak scratch
```

To update your services, run:
```
make -f k8s.mak rollout
```


## Local dynamoDB

**Note:** In the section, all commands are run and tested on Mac operating system. Some command might not work on Windows operating system.

### 1. Download local dynamodb:
https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.zip

### 2. To start the local dynamoDB, run the below command on your local machine: 
(Keep the DB running!)

~~~
$ java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
~~~

### 3. To connect local db, modify the below parameter `dynamodb_url` in `/db/app.py`:

~~~
dynamodb_url = 'http://host.docker.internal:8000'
~~~

### 4. Initialize local DynamoDB and load it with initial data:

~~~
$ make -f k8s.mak local-loader
~~~

### 5. Test
When you create a new music record by `mcli` (client), you can run the command below to see if the record has been added to the local dynamoDB table:

~~~
$ aws dynamodb scan --table-name <TABLE-NAME> --endpoint-url http://localhost:8000
~~~


----

### Client Code: mcli

Go to our client code folder.

```
$ cd /home/k8s/mcli
```

Build the client code image first. Note that everytime a change is made to the client code, the image must be re-built again.

```
$ make build-mcli
```

Supply the DNS name of the EC2 instance that hosts our server code to the make file for the command run-mcli. This will start a Docker container running the client code and connecting to our EC2 server instance.

```
$ make SERVER={EC2-DNS-NAME} run-mcli
```

The client code resides on:

```
/home/k8s/mcli/mcli.py
```

There is a class called **Mcli** which extends the **cmd.Cmd class**. If we want to add a new command to the client code, we need to create a new function under the class Mcli and comply with the following function name format:

```python
def do_{command_name}(self, arg):
    ...
```

For example, if we want to add a new command called **add_playlist**, we need to create a new function under the class Mcli called:

```python
def do_add_playlist(self, arg):
    ...
```
