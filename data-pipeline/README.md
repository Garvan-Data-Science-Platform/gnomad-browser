# gnomAD Browser Data Pipeline

## Requirements

- [Google Cloud SDK](https://cloud.google.com/sdk/)

  See https://cloud.google.com/sdk/docs/quickstarts for instructions on installing and initializing the Google Cloud SDK.

- [Hail](https://hail.is/)

  See https://hail.is/docs/0.2/getting_started.html for instructions on installing Hail.

## Data preparation

Data preparation for the gnomAD browser is split into multiple pipelines:

- genes
- clinvar_grch37
- clinvar_grch38
- exac
- gnomad_v2
- gnomad_sv_v2
- gnomad_v3

The genes pipeline must be run first. The others can be run in any order.

The genes pipeline shuffles a lot and thus should not be run on clusters with preemptible workers.

The ClinVar pipelines must be run on clusters with VEP installed and configured for the appropriate reference genome.

### Running a pipeline on a Dataproc cluster

- Configure pipeline.

  Project and zone settings are used for Dataproc clusters.

  Staging path specifies the destination for intermediate Hail Tables.

  ```
  ./deployctl config set project <project-id>
  ./deployctl config set zone <zone>
  ./deployctl config set pipeline_output_path <gs://bucket/path/to/staging/directory>
  ```

- Start a cluster.

  ```
  ./deployctl dataproc-cluster start <cluster-name>
  ```

- Run a pipeline.

  A list of all pipelines can be seen with `./deployctl data-pipeline run --help`.

  ```
  ./deployctl data-pipeline run --cluster <cluster-name> <pipeline> -- <pipeline-args>
  ```

- Stop cluster.

  Clusters created with `deployctl dataproc-cluster start` are configured with a max idle time and will automatically stop.

  ```
  ./deployctl dataproc-cluster stop <cluster-name>
  ```
