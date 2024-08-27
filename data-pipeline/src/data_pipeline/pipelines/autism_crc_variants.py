import os
from loguru import logger


from data_pipeline.config import PipelineConfig
from data_pipeline.pipeline import Pipeline, run_pipeline
from data_pipeline.helpers.write_schemas import write_schemas

from data_pipeline.datasets.gnomad_v4.gnomad_v4_variants import (
    prepare_gnomad_v4_variants,
)


from data_pipeline.pipelines.genes import pipeline as genes_pipeline

#from data_pipeline.datasets.gnomad_v4.gnomad_v4_validation import (
#    validate_exome_globals_input,
#    validate_genome_globals_input,
#    validate_exome_variant_input,
#    validate_genome_variant_input,
#    validate_step1_output,
#    validate_step2_output,
#    validate_step3_output,
#)

from data_pipeline.data_types.variant import (
    annotate_variants,
    annotate_transcript_consequences,
)

RUN = True

pipeline_name = "autism_crc_variants"

output_sub_dir = "autism_crc"

config = PipelineConfig(
    name=pipeline_name,
    input_root= "gs://gnomad-dev-data-pipeline/autism_crc/",
    output_root="gs://gnomad-dev-data-pipeline/autism_crc/",
)


pipeline = Pipeline(config=config)

pipeline.add_task(
    name="prepare_autism_crc_variants",
    task_function=prepare_autism_crc_variants, # TODO: update this function to be exome optional
    output_path=f"{output_sub_dir}/autism_crc_subsetted_variants_base.ht",
    inputs={
        # TODO: update this when not using subsetted data AND when not using joined table
        "genome_variants_path": "gs://gnomad-dev-data-pipeline/autism_crc/v2_sites_autism_joined.ht/",
    },
)

pipeline.add_task(
    name="annotate_autism_crc_variants",
    task_function=annotate_variants, # TODO: update this function to be exome optional
    output_path=f"{output_sub_dir}/autism_crc_subsetted_variants_annotated_1.ht",
    inputs=(
        {
            "variants_path": pipeline.get_task("prepare_autism_crc_variants"),
            # "exome_coverage_path": "gs://gcp-public-data--gnomad/release/4.0/coverage/exomes/gnomad.exomes.v4.0.coverage.ht",
            "genome_coverage_path": "gs://gnomad-dev-data-pipeline/autism_crc/subsetted_autism_crc_coverage.ht",
            # "caids_path": "gs://gnomad-browser-data-pipeline/caids/gnomad_v4_caids.ht",
        }
    ),
)

pipeline.add_task(
    name="annotate_autism_crc_transcript_consequences",
    task_function=annotate_transcript_consequences, # TODO: check if this function cares about exomes
    output_path=f"{output_sub_dir}/autism_crc_subsetted_variants_annotated_2.ht",
    inputs={
        "variants_path": pipeline.get_task("annotate_autism_crc_variants"),
        # TODO: check this points to autism genes data
        "transcripts_path": genes_pipeline.get_output("base_transcripts_grch38"),
        # TODO: check this points to autism genes data
        "mane_transcripts_path": genes_pipeline.get_output("mane_select_transcripts"),
    },
)

###############################################
# Outputs
###############################################

pipeline.set_outputs({"variants": "annotate_autism_crc_transcript_consequences"})

###############################################
# Run
###############################################

if __name__ == "__main__":
    if RUN:
        run_pipeline(pipeline)

        write_schemas(
            [pipeline],
            os.path.join("/home/msolomon", "schemas"),
            task_names=[
                "prepare_gnomad_v4_variants",
                "annotate_gnomad_v4_variants",
                "annotate_gnomad_v4_transcript_consequences",
            ],
        )
        # copy locally using:
        # gcloud compute scp dp-m:~/schemas . --tunnel-through-iap --recurse

    logger.info("Validating pipeline IO formats")

#    validate_exome_globals_input(pipeline)
#    validate_genome_globals_input(pipeline)
#    validate_exome_variant_input(pipeline)
#    validate_genome_variant_input(pipeline)
#    validate_step1_output(pipeline)
#    validate_step2_output(pipeline)
#    validate_step3_output(pipeline)
