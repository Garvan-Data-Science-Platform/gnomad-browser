# Makefile to make it easier to deploy gnomAD

PROJECT_ID:=gnomad-dev
REGION:=australia-southeast1
ZONE:=$(REGION)-a
OUTPUT_BUCKET:=gs://gnomad-dev-data-pipeline
CLUSTER_NAME:=gnomad-dev
SUBNET_NAME:=garvan-gnomad-dataproc
AUTOSCALING_POLICY_NAME:=gnomad-dataproc-scaling
ENVIRONMENT_TAG:=dev
DOCKER_TAG:=dev_2023-11-24
DEPLOYMENT_STATE:=green
READS_INSTANCE_NAME:=readvis-data
LOAD_NODE_POOL_SIZE:=48
READS_DISK_SIZE:=20


### Initial Config ###

config:
	./deployctl config set project $(PROJECT_ID)
	./deployctl config set zone $(ZONE)
	./deployctl config set data_pipeline_output $(OUTPUT_BUCKET)
	./deployctl config set subnet_name $(SUBNET_NAME)
	./deployctl config set environment_tag $(ENVIRONMENT_TAG)

gcloud-auth:
	gcloud auth login

kube-config:
	gcloud container clusters get-credentials $(CLUSTER_NAME) \
		    --zone=$(ZONE)

### Data Pipeline ###

dataproc-start:
	./deployctl dataproc-cluster start $(CLUSTER_NAME)

dataproc-help:
	./deployctl data-pipeline run --help

dataproc-run:
	./deployctl data-pipeline run --cluster $(CLUSTER_NAME) $(PIPELINE) -- $(PIPELINE_ARGS)

dataproc-stop:
	./deployctl dataproc-cluster stop $(CLUSTER_NAME)

# https://cloud.google.com/dataproc/docs/concepts/configuring-clusters/autoscaling
# Adjust for clinvar pipelines: make CLUSTER_NAME="vep85" dataproc-cluster-config
dataproc-cluster-config: pyspark_scaling.yaml
	gcloud dataproc autoscaling-policies import $(AUTOSCALING_POLICY_NAME) \
  	--source=./$< \
    --region=$(REGION) && \
	gcloud dataproc clusters update $(CLUSTER_NAME) \
		--autoscaling-policy=$(AUTOSCALING_POLICY_NAME) \
		--region=$(REGION)

dataproc-vep-grch37-start:
	./deployctl dataproc-cluster start vep85 \
		--vep GRCh37 \
		--num-secondary-workers 32

dataproc-vep-grch37-run:
	./deployctl data-pipeline run --cluster vep85 clinvar_grch37

dataproc-vep-grch37-stop:
	./deployctl dataproc-cluster stop vep85

dataproc-vep-grch38-start:
	./deployctl dataproc-cluster start vep105 \
		--init=gs://gcp-public-data--gnomad/resources/vep/v105/vep105-init.sh \
		--metadata=VEP_CONFIG_PATH=/vep_data/vep-gcloud.json,VEP_CONFIG_URI=file:///vep_data/vep-gcloud.json,VEP_REPLICATE=us \
		--master-machine-type n1-highmem-8 \
		--worker-machine-type n1-highmem-8 \
		--worker-boot-disk-size=200 \
		--secondary-worker-boot-disk-size=200 \
		--num-secondary-workers 16

dataproc-vep-grch38-run:
	./deployctl data-pipeline run --cluster vep105 clinvar_grch38

dataproc-vep-grch38-stop:
	./deployctl dataproc-cluster stop vep105

### Reads data  ###

# based upon steps in `reads/reference-data/prepare_readviz_disk_v4.sh
# use `tabix -p bed gencode.v39.annotation.bed.bgz`

reads-instance-create:
	gcloud compute instances create $(READS_INSTANCE_NAME) \
		--machine-type e2-standard-8 \
		--zone $(ZONE)

reads-disk-create:
	gcloud compute disks create $(READS_INSTANCE_NAME)-disk \
		--size=$(READS_DISK_SIZE)GB \
		--type=pd-balanced \
		--zone $(ZONE)

reads-disk-attach:
	gcloud compute instances attach-disk $(READS_INSTANCE_NAME) \
		--disk $(READS_INSTANCE_NAME)-disk \
		--device-name reads-disk \
		--zone $(ZONE)

reads-ssh:
	gcloud compute ssh --zone $(ZONE) $(READS_INSTANCE_NAME) \
		--project $(PROJECT_ID)

# Format disk because you are not copying from existing snapshot
# ls -l /dev/disk/by-id/google-*
#
# sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb
#
# sudo mkdir -p /mnt/disks/reads/reference
#
# sudo mount -o discard,defaults /dev/disk/by-id/google-reads-disk /mnt/disks/reads
#
# sudo resize2fs /dev/disk/by-id/google-reads-disk

reads-upload:
	gcloud compute scp reads/reference-data/gencode.v39.annotation.bed.bgz --zone $(ZONE) $(READS_INSTANCE_NAME):~/
	gcloud compute scp reads/reference-data/gencode.v39.annotation.bed.bgz.tbi --zone $(ZONE) $(READS_INSTANCE_NAME):~/

# on VM
# sudo mv ~/gencode* /mnt/disks/reads/reference/
#
# sudo umount /mnt/disks/reads

reads-disk-detach:
	gcloud compute instances detach-disk $(READS_INSTANCE_NAME) \
		--disk $(READS_INSTANCE_NAME)-disk \
		--zone $(ZONE)

reads-instance-delete:
	gcloud compute instances delete $(READS_INSTANCE_NAME) \
		--zone $(ZONE)

### Pre-Deployment ###

eck-create:
	kubectl create -f https://download.elastic.co/downloads/eck/2.9.0/crds.yaml

eck-apply:
	kubectl apply -f https://download.elastic.co/downloads/eck/2.9.0/operator.yaml

eck-check:
	kubectl -n elastic-system logs -f statefulset.apps/elastic-operator

# Check `deploy_config.json`

elastic-create:
	./deployctl elasticsearch apply --cluster-name=$(CLUSTER_NAME)

redis-deploy:
	cd deploy/manifests/redis/ && kubectl apply -k .

docker-auth:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev

### Elasticsearch ###
# get elasticsearch ip
es-ip-get:
	kubectl get service $(PROJECT_ID)-elasticsearch-lb --output=jsonpath="{.status.loadBalancer.ingress[0].ip}"

# bash command to set env var:
# `-s` is silent (e.g. doesn't print recipe)
# export ELASTICSEARCH_IP=$(make -s es-ip-get)

# requires pre-deployment steps
# `deploy/docs/LoadingLargeDatasets.md`
# create GKE node pool - I tried to add this to deployctl, but need to check the command works first
#es-gke-node-pool-create:
#	./deployctl elasticsearch create-gke-node-pool --dry_run

es-gke-node-pool-create:
	gcloud container node-pools create es-ingest \
    --cluster $(CLUSTER_NAME) \
    --zone $(ZONE) \
    --service-account $(PROJECT_ID)-gke@$(PROJECT_ID).iam.gserviceaccount.com \
    --num-nodes $(LOAD_NODE_POOL_SIZE) \
    --machine-type e2-highmem-4 \
    --enable-autorepair --enable-autoupgrade \
    --shielded-secure-boot \
		--shielded-integrity-monitoring \
    --metadata=disable-legacy-endpoints=true

es-gke-node-pool-add:
	./deployctl elasticsearch apply --n-ingest-pods=$(LOAD_NODE_POOL_SIZE) --cluster-name=$(CLUSTER_NAME)

es-dataproc-start:
	./deployctl dataproc-cluster start es --num-preemptible-workers $(LOAD_NODE_POOL_SIZE)

# I'm assuming DATASET refers to a `.ht` file in the datapipeline bucket
# run with `make DATASET=gnomad_v2_exome_coverage es-load`
es-load:
	./deployctl elasticsearch load-datasets --dataproc-cluster es $(DATASET) --cluster-name=$(CLUSTER_NAME)

es-dataproc-stop:
	./deployctl dataproc-cluster stop es

# move data to persistent pool
# remember to do logs indices too
es-index-move:
	curl -u "elastic:$$ELASTICSEARCH_PASSWORD" \
		"http://localhost:9200/$(INDEX)/_settings" -XPUT \
		--header "Content-Type: application/json" \
		--data @- {"index.routing.allocation.require._name": "$(CLUSTER_NAME)-es-data-*"}

# if there are errors with 'indexes don't have primary shards' (likely cos of log files left on old temp load node pool). These can be forced to move (with data loss) to a new node with this command:
#
#curl -u "elastic:$ELASTICSEARCH_PASSWORD" -XPOST "localhost:9200/_cluster/reroute?pretty" -H 'Content-Type: application/json' -d'
#{
#    "commands" : [
#        {
#          "allocate_empty_primary" : {
#                "index" : ".ds-ilm-history-5-2023.12.05-000001",
#                "shard" : 0,
#                "node" : "gnomad-dev-es-data-green-0",
#                "accept_data_loss" : "true"
#          }
#        }
#    ]
#}
#'
# 

es-index-watch:
	curl -s -u "elastic:$$ELASTICSEARCH_PASSWORD" "http://localhost:9200/_cat/shards?v" | grep RELOCATING

es-aliases-list:
	curl -u "elastic:$$ELASTICSEARCH_PASSWORD" http://localhost:9200/_cat/aliases

# have issues auto stripping timestamp
#test:
#	echo $(echo $(INDEX_NAME) | sed -E "s/-\+[0-9]\{2,4\}//g")

es-alias-add:
	curl -u "elastic:$$ELASTICSEARCH_PASSWORD" \
		-XPOST http://localhost:9200/_aliases \
		--header "Content-Type: application/json" \
		--data '{"actions": [{"add": {"index": "$(INDEX_NAME)", "alias": "$(ALIAS_NAME)"}}]}'

# set up snapshot bucket
#curl -u "elastic:$ELASTICSEARCH_PASSWORD" -XPUT http://localhost:9200/_snapshot/backups --header "Content-Type: application/json" --data @- <<EOF
#{
#   "type": "gcs",
#   "settings": {
#     "bucket": "gnomad-dev-elastic-snaps",
#     "client": "default",
#     "compress": true
#   }
#}
#EOF

# create snapshot
#curl -u "elastic:$ELASTICSEARCH_PASSWORD" -XPUT 'http://localhost:9200/_snapshot/backups/%3Csnapshot-%7Bnow%7BYYYY.MM.dd.HH.mm%7D%7D%3E?pretty'


es-gke-node-pool-remove:
	./deployctl elasticsearch apply --n-ingest-pods=0 --cluster-name=$(CLUSTER_NAME)

es-gke-node-pool-destroy:
	gcloud container node-pools delete es-ingest \
    --cluster $(CLUSTER_NAME) \
    --zone $(ZONE)

es-port-forward:
	kubectl port-forward service/$(CLUSTER_NAME)-es-http 9200

#es-check:
#	curl -u "elastic:$$ELASICSEARCH_PASSWORD" http://localhost:9200/_cluster/health

es-secret-delete:
	gcloud secrets delete gnomad-elasticsearch-password

# Cannot set env var in parent shell from within make
es-secret-get:
	./deployctl elasticsearch get-password --cluster-name=gnomad-dev

# bash command to set env var with password
# `-s` is silent (e.g. doesn't print recipe)
# export ELASTICSEARCH_PASSWORD=$(make -s es-secret-get)

es-secret-create:
	echo -n "$$ELASTICSEARCH_PASSWORD" | gcloud secrets create gnomad-elasticsearch-password --data-file=- --locations=australia-southeast1 --replication-policy=user-managed

es-secret-add:
	gcloud secrets add-iam-policy-binding gnomad-elasticsearch-password \
		--member="serviceAccount:$(PROJECT_ID)-data-pipeline@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/secretmanager.secretAccessor"

es-data-load:
	./deployctl elasticsearch load-datasets --dataproc-cluster $(PROJECT_ID) gnomad_v4_exome_coverage --cluster-name=$(CLUSTER_NAME)


### Deployment ###

docker:
	./deployctl images build --push --tag $(DOCKER_TAG)
	./deployctl reads-images build --push --tag $(DOCKER_TAG)

# OPTIONAL ARGS: --browser-tag <BROWSER_IMAGE_TAG> --api-tag <API_IMAGE_TAG>
deploy-create:
	./deployctl deployments create --name $(PROJECT_ID)-$(DEPLOYMENT_STATE) 
	./deployctl reads-deployments create --name $(PROJECT_ID)-$(DEPLOYMENT_STATE) 

deploy-apply:
	./deployctl deployments apply $(PROJECT_ID)-$(DEPLOYMENT_STATE)
	./deployctl reads-deployments apply $(PROJECT_ID)-$(DEPLOYMENT_STATE) 

ingress-apply:
	./deployctl demo apply-ingress $(PROJECT_ID)-$(DEPLOYMENT_STATE)

ingress-describe:
	kubectl describe ingress gnomad-ingress-demo-$(PROJECT_ID)-$(DEPLOYMENT_STATE) 

### Clean up deployment ###

deployments-list:
	./deployctl deployments list

deployments-local-clean:
	./deployctl deployments clean $(PROJECT_ID)-$(DEPLOYMENT_STATE)
	./deployctl reads-deployments clean $(PROJECT_ID)-$(DEPLOYMENT_STATE)

deployments-cluster-delete:
	./deployctl deployments delete $(PROJECT_ID)-$(DEPLOYMENT_STATE)
	./deployctl reads-deployments delete $(PROJECT_ID)-$(DEPLOYMENT_STATE)

ingress-get:
	kubectl get ingress

ingress-delete:
	kubectl delete ingress gnomad-ingress-demo-$(PROJECT_ID)-$(DEPLOYMENT_STATE) 

redis-delete:
	cd deploy/manifests/redis/ && kubectl delete -k .

### Docker command for running hail locally ###
hail-docker:
	docker run -it --rm \
		-e USERID=$$(id -u) \
		-e GROUPID=$$(id -g) \
		-v $$(pwd):/work \
		--net=host \
		broadinstitute/dig-loam:hail-0.2.94 bash 

### Tidy up ###

unused-disks-list:
	gcloud compute disks list --filter="-users:*" --format "value(uri())"

unused-disks-delete:
	gcloud compute disks delete $$(gcloud compute disks list --filter="-users:*" --format "value(uri())")

unused-disks-delete-alt:
	gcloud compute disks delete $$(gcloud compute disks list --filter="-users:*" --format "value(uri())")
