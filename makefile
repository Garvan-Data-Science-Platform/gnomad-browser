# Makefile to make it easier to deploy gnomAD

PROJECT_ID:=gnomad-dev
REGION:=australia-southeast1
ZONE:=$(REGION)-a
OUTPUT_BUCKET:=gs://gnomad-dev-data-pipeline
CLUSTER_NAME:=gnomad-dev
SUBNET_NAME:=garvan-gnomad-dataproc
AUTOSCALING_POLICY_NAME:=gnomad-dataproc-scaling

config:
	./deployctl config set project $(PROJECT_ID)
	./deployctl config set zone $(ZONE)
	./deployctl config set data_pipeline_output $(OUTPUT_BUCKET)
	./deployctl config set subnet_name $(SUBNET_NAME)

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
