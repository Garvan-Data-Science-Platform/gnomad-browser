# Makefile to make it easier to deploy gnomAD

PROJECT_ID:=gnomad-dev
REGION:=australia-southeast1
ZONE:=$(REGION)-a
OUTPUT_BUCKET:=gs://gnomad-dev-data-pipeline
CLUSTER_NAME:=gnomad-dev
SUBNET_NAME:=garvan-gnomad-dataproc
AUTOSCALING_POLICY_NAME:=gnomad-dataproc-scaling
ENVIRONMENT_TAG:=dev
DOCKER_TAG:=dev_2023-11-22

### Data Pipeline ###

config:
	./deployctl config set project $(PROJECT_ID)
	./deployctl config set zone $(ZONE)
	./deployctl config set data_pipeline_output $(OUTPUT_BUCKET)
	./deployctl config set subnet_name $(SUBNET_NAME)
	./deployctl config set environment_tag $(ENVIRONMENT_TAG)

# need to do `gcloud auth login` first.
dataproc-start:
	./deployctl dataproc-cluster start $(CLUSTER_NAME)

help:
	./deployctl data-pipeline run --help

run:
	./deployctl data-pipeline run --cluster $(CLUSTER_NAME) $(PIPELINE) -- $(PIPELINE_ARGS)

dataproc-stop:
	./deployctl dataproc-cluster stop $(CLUSTER_NAME)

# https://cloud.google.com/dataproc/docs/concepts/configuring-clusters/autoscaling
dataproc-cluster-config: pyspark_scaling.yaml
	gcloud dataproc autoscaling-policies import $(AUTOSCALING_POLICY_NAME) \
  	--source=./$< \
    --region=$(REGION) && \
	gcloud dataproc clusters update $(CLUSTER_NAME) \
		--autoscaling-policy=$(AUTOSCALING_POLICY_NAME) \
		--region=$(REGION)

data-clone:
	gsutil -m rsync -r gs://gcp-public-data--gnomad/release/4.0 $(OUTPUT_BUCKET)/

### Pre-Deployment ###

kube-config:
	gcloud container clusters get-credentials $(CLUSTER_NAME) \
		    --zone=$(ZONE)

eck-create:
	kubectl create -f https://download.elastic.co/downloads/eck/2.9.0/crds.yaml

eck-apply:
	kubectl apply -f https://download.elastic.co/downloads/eck/2.9.0/operator.yaml

eck-check:
	kubectl -n elastic-system logs -f statefulset.apps/elastic-operator

# Check `deployctl_config.json`

elastic-create:
	./deployctl elasticsearch apply --cluster-name=$(CLUSTER_NAME)

redis-deploy:
	cd deploy/manifests/redis/ && kubectl apply -k .

docker-auth:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev

### Deployment ###

docker:
	./deployctl images build --push --tag $(DOCKER_TAG)
	./deployctl reads-images build --push --tag $(DOCKER_TAG)

# OPTIONAL ARGS: --browser-tag <BROWSER_IMAGE_TAG> --api-tag <API_IMAGE_TAG>
deploy-create:
	./deployctl deployments create --name $(PROJECT_ID) 
	./deployctl reads-deployments create --name $(PROJECT_ID) 

deploy-apply:
	./deployctl deployments apply $(PROJECT_ID) 
	./deployctl reads-deployments apply $(PROJECT_ID) 

ingress-apply:
	./deployctl demo apply-ingress $(PROJECT_ID) 

ingress-describe:
	kubectl describe ingress gnomad-ingress-demo-$(PROJECT_ID) 

### Clean up deployment ###

deployments-list:
	./deployctl deployments list

deployments-clean-local:
	./deployctl deployments clean $(PROJECT_ID)
	./deployctl reads-deployments clean $(PROJECT_ID)

deployments-delete-cluster:
	./deployctl deployments delete $(PROJECT_ID)
	./deployctl reads-deployments delete $(PROJECT_ID)

ingress-get:
	kubectl get ingress

ingress-delete:
	kubectl delete ingress gnomad-ingress-demo-$(PROJECT_ID) 
