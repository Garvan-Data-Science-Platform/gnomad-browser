from data_pipeline.pipeline import Pipeline, run_pipeline

from data_pipeline.data_types.coverage import prepare_coverage


pipeline = Pipeline()

pipeline.add_task(
    "prepare_autism_crc_coverage",
    prepare_coverage,
    "/autism_crc/autism_crc_genome_coverage_subset_computed.ht",
    {"coverage_path": "gs://gnomad-dev-data-pipeline/autism_crc/autism_crc_coverage_subset.ht"},
)

###############################################
# Outputs
##############################################

pipeline.set_outputs({"coverage": "prepare_autism_crc_coverage"})

###############################################
# Run
###############################################

if __name__ == "__main__":
    run_pipeline(pipeline)
