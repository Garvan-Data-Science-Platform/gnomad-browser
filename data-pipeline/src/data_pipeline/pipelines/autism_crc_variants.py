from data_pipeline.pipeline import Pipeline, run_pipeline

from data_pipeline.data_types.variant import annotate_variants, annotate_transcript_consequences

# from data_pipeline.datasets.gnomad_v2.gnomad_v2_mnvs import (
#     prepare_gnomad_v2_mnvs,
#     annotate_variants_with_mnvs,
#     replace_quote_char,
# )
from data_pipeline.datasets.autism_crc.autism_crc_variants import prepare_autism_crc_variants

from data_pipeline.pipelines.autism_crc_coverage import pipeline as coverage_pipeline
from data_pipeline.pipelines.autism_crc_create_sites import pipeline as create_sites_pipeline
from data_pipeline.pipelines.genes import pipeline as genes_pipeline

CAIDS_PATH = 'gs://gnomad-dev-data-pipeline/autism_crc/data-prep/caids.ht'

pipeline = Pipeline()

###############################################
# MNVs
###############################################

# pipeline.add_download_task(
#     "download_mnvs",
#     "https://storage.googleapis.com/gcp-public-data--gnomad/release/2.1/mnv/gnomad_mnv_coding_v0.tsv",
#     "/autism_crc/data-prep/gnomad_mnv_coding_v0.tsv",
# )

# pipeline.add_download_task(
#     "download_3bp_mnvs",
#     "https://storage.googleapis.com/gcp-public-data--gnomad/release/2.1/mnv/gnomad_mnv_coding_3bp_fullannotation.tsv",
#     "/autism_crc/data-prep/gnomad_mnv_coding_3bp_fullannotation.tsv",
# )

# pipeline.add_task(
#     "replace_mnv_quote_char",
#     replace_quote_char,
#     "/autism_crc/data-prep/gnomad_mnv_coding_v0-quoted.tsv",
#     {"path": pipeline.get_task("download_mnvs")},
# )

# pipeline.add_task(
#     "replace_3bp_mnv_quote_char",
#     replace_quote_char,
#     "/autism_crc/data-prep/gnomad_mnv_coding_3bp_fullannotation-quoted.tsv",
#     {"path": pipeline.get_task("download_3bp_mnvs")},
# )

# pipeline.add_task(
#     "prepare_gnomad_v2_mnvs",
#     prepare_gnomad_v2_mnvs,
#     "/autism_crc/data-prep/gnomad_v2_mnvs.ht",
#     {
#         "mnvs_path": pipeline.get_task("replace_mnv_quote_char"),
#         "three_bp_mnvs_path": pipeline.get_task("replace_3bp_mnv_quote_char"),
#     },
# )

###############################################
# Variants
###############################################

# TODO: what is impact of excluding exomes?
# pipeline.add_task(
#     "prepare_autism_crc_variants",
#     prepare_autism_crc_variants,
#     "/autism_crc/data-prep/autism_crc_variants_base.ht",
#     {
#         # "exome_variants_path": "gs://gcp-public-data--gnomad/release/2.1.1/ht/exomes/gnomad.exomes.r2.1.1.sites.ht",
#         "genome_variants_path": create_sites_pipeline.get_output("variants"),
#     },
# )

# TODO: what is impact of excluding exomes? - Nothing! :)
pipeline.add_task(
    "annotate_autism_crc_variants",
    annotate_variants,
    "/autism_crc/data-prep/autism_crc_variants_annotated_1.ht",
    {
        # "variants_path": pipeline.get_task("prepare_autism_crc_variants"),
        "variants_path": create_sites_pipeline.get_output("variants"),
        # "exome_coverage_path": coverage_pipeline.get_output("exome_coverage"),
        "genome_coverage_path": coverage_pipeline.get_output("coverage"),
        "caids_path": CAIDS_PATH,
    },
)

# pipeline.add_task(
#     "annotate_gnomad_v2_variants_with_mnvs",
#     annotate_variants_with_mnvs,
#     "/autism_crc/data-prep/gnomad_v2_variants_annotated_2.ht",
#     {
#         "variants_path": pipeline.get_task("annotate_autism_crc_variants"),
#         "mnvs_path": pipeline.get_task("prepare_gnomad_v2_mnvs"),
#     },
# )

pipeline.add_task(
    "annotate_autism_crc_transcript_consequences",
    annotate_transcript_consequences,
    "/autism_crc/data-prep/autism_crc_variants_annotated_3.ht",
    {
        # "variants_path": pipeline.get_task("annotate_gnomad_v2_variants_with_mnvs"),
        "variants_path": pipeline.get_task("annotate_autism_crc_variants"),
        "transcripts_path": genes_pipeline.get_output("base_transcripts_grch37"),
    },
)

###############################################
# Outputs
###############################################

pipeline.set_outputs(
    {
        # "multinucleotide_variants": "prepare_gnomad_v2_mnvs",
        "variants": "annotate_autism_crc_transcript_consequences"}
)

###############################################
# Run
###############################################

if __name__ == "__main__":
    run_pipeline(pipeline)
