# Pipeline to create sites Autism CRC dataset as precursor for coverage pipeline

from data_pipeline.pipeline import Pipeline, run_pipeline
from data_pipeline.datasets.generic_grch37.load_data.import_vcf import import_vcf
from data_pipeline.datasets.generic_grch37.load_data.import_resources import (import_clinvar, import_de_novos, import_methylation, import_exac_data)
from data_pipeline.datasets.generic_grch37.sample_qc.apply_hard_filters import (annotate_sex, apply_filters, export_annotations, import_metadata, filter_for_qc)


BUCKET = "gs://gnomad-dev-data-pipeline"
INPUT_DATA_URL = f"{BUCKET}/autism_crc/AutismCRC.chr22XY.6samples.vcf.gz"

pipeline = Pipeline()


###############################################
# load_data
###############################################

# import_vcf

pipeline.add_task(
    "import_autism_vcf",
    import_vcf,
    "/autism_crc/autism_crc_sites_qc.ht",
    {
        "vcf": INPUT_DATA_URL,
    },
)

# import resources

# pipeline.add_task(
#     "import_clinvar",
#     import_clinvar,
#     "/autism_crc/resources_clinvar.ht",
#     {
#         "clinvar_vcf_path": "gs://gnomad-dev-data-pipeline/autism_crc/clinvar.2024-06-24.22XY.vcf.gz",
#         "vep_config": "gs://gnomad-dev-data-pipeline/autism_crc/vep85-loftee-gcloud.json"
#     },
# )

# pipeline.add_task(
#     "import_de_novos",
#     import_de_novos,
#     "/autism_crc/resources_de_novos.ht",
#     {
#         "de_novos_path": "gs://gnomad/resources/validated_de_novos.bgz",
#     },
# )

# pipeline.add_task(
#     "import_methylation",
#     import_methylation,
#     "/autism_crc/resources_methylation.ht",
#     {
#         "all_methylation_path": "gs://gcp-public-data--gnomad/resources/methylation/cpg.vcf.bgz",
#     },
# )

# vcf_path = "gs://gcp-public-data--gnomad/legacy/exac_browser/ExAC.r1.sites.vep.vcf.gz"
pipeline.add_task(
    "import_exac_data",
    import_exac_data,
    "/autism_crc/resources_exac_data.ht",
    {
        "exac_path": "gs://gcp-public-data--gnomad/legacy/exac_browser/ExAC.r1.sites.vep.vcf.gz",
    },
)

###############################################
# load_data
###############################################

# apply_hard_filters

pipeline.add_task(
    "filter_for_qc",
    filter_for_qc,
    "/autism_crc/autism_crc_filtered_sites_qc.ht",
    {
        "mt": f"{BUCKET}/autism_crc/autism_crc_sites_qc.ht",
    },
)

pipeline.add_task(
    "import_metadata",
    import_metadata,
    "/autism_crc/autism_crc_meta_sites_qc.ht",
    {
        "qc_mt": f"{BUCKET}/autism_crc/autism_crc_sites_qc.ht",
        "meta_ht": f"{BUCKET}/autism_crc/placeholder_subset_metadata.tsv",

    },
)

pipeline.add_task(
    "annotate_sex",
    annotate_sex,
    "/autism_crc/autism_crc_annotate_sex.ht",
    {
        "mt": f"{BUCKET}/autism_crc/autism_crc_meta_sites_qc.ht",
    },
)

pipeline.add_task(
    "apply_filters",
    apply_filters,
    "/autism_crc/autism_crc_filtered.ht",
    {
        "mt": f"{BUCKET}/autism_crc/autism_crc_annotate_sex.ht",
    },
)

pipeline.add_task(
    "export_annotations",
    export_annotations,
    "/autism_crc/autism_crc_rank_annotations.ht",
    {
        "ht": f"{BUCKET}/autism_crc/autism_crc_filtered.ht",
    },
)

###############################################
# Outputs
###############################################

pipeline.set_outputs({
                     "vcf": "import_autism_vcf",
                     # "clinvar": "import_clinvar",
                     "exac_data": "import_exac_data",
                     # "de_novos": "import_de_novos",
                     # "methylation": "import_methylation"
                     "filter_for_qc": "filter_for_qc",
                     "import_metadata": "import_metadata",
                     "annotate_sex": "annotate_sex",
                     "apply_filters": "apply_filters",
                     "export_annotations": "export_annotations",
                 })
###############################################
# Run
###############################################

if __name__ == "__main__":
    run_pipeline(pipeline)
