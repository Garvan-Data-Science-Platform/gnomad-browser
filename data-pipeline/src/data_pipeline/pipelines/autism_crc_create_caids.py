# Pipeline to create Autism CRC caids dataset as precursor for variants pipeline

import hail as hl

from data_pipeline.pipeline import Pipeline, run_pipeline

from data_pipeline.datasets.autism_crc.autism_crc_coverage import prepare_autism_crc_coverage
# for vcf?
from data_pipeline.pipelines.autism_crc_create_sites import pipeline as create_sites_pipeline


INPUT_DATA_URL = "gs://gnomad-dev-data-pipeline/autism_crc/subsetted_autism_crc.ht"

pipeline = Pipeline()


###############################################
# Compute coverage
###############################################

pipeline.add_task(
    "prepare_autism_crc_coverage",
    prepare_autism_crc_coverage,
    "/autism_crc/autism_crc_coverage_subset.ht",
    {"path": INPUT_DATA_URL},
)

###############################################
# Run
###############################################

if __name__ == "__main__":
    run_pipeline(pipeline)
