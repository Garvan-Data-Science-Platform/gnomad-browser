# Pipeline to subset Autism CRC dataset to just Chromosome 22 for easy development of pipelines.

import hail as hl

from data_pipeline.pipeline import Pipeline, run_pipeline

INPUT_DATA_URL = "gs://autism-crc-input-data/autism-crc-original/AutismCRC.vcf.gz"

pipeline = Pipeline()


def convert_vcf_to_ht(vcf_path):
    input_ht = hl.import_vcf(vcf_path, force_bgz=True, min_partitions=32)
    return input_ht


def subset_data(input_ht):
    input_data = hl.read_matrix_table(input_ht)
    input_data_filtered = input_data.filter_rows(input_data.locus.contig == "22")
    print(input_data_filtered.count_rows() / input_data.count_rows())
    return input_data_filtered


###############################################
# Subset dataset to chromosome 22
###############################################

pipeline.add_task(
    "convert_autism_crc",
    convert_vcf_to_ht,
    "/autism_crc/autism_crc.ht",
    {"vcf_path": INPUT_DATA_URL},
)

pipeline.add_task(
    "subset_autism_crc",
    subset_data,
    "/autism_crc/subsetted_autism_crc.ht",
    {"input_ht": pipeline.get_task("convert_autism_crc")},
)

###############################################
# Run
###############################################

if __name__ == "__main__":
    run_pipeline(pipeline)
