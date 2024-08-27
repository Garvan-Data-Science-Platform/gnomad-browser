# Pipeline to subset Autism CRC dataset to just Chromosome 22 for easy development of pipelines.

import hail as hl

from data_pipeline.pipeline import Pipeline, run_pipeline

INPUT_DATA_URL = "gs://autism-crc-input-data/autism-crc-original/AutismCRC.vcf.gz"
V4_SITES_DATA_URL = "gs://gcp-public-data--gnomad/release/4.0/ht/genomes/gnomad.genomes.v4.0.sites.ht"
V2_SITES_DATA_URL = "gs://gcp-public-data--gnomad/release/2.1.1/ht/genomes/gnomad.genomes.r2.1.1.sites.ht"
V3_COVERAGE_DATA_URL = "gs://gcp-public-data--gnomad/release/3.0.1/coverage/genomes/gnomad.genomes.r3.0.1.coverage.ht"

pipeline = Pipeline()


def convert_vcf_to_ht(vcf_path):
    input_ht = hl.import_vcf(vcf_path, force_bgz=True, min_partitions=32)
    return input_ht

def subset_grch37_matrix_table_data(input_ht):
    input_data = hl.read_matrix_table(input_ht)
    input_data_filtered = input_data.filter_rows(input_data.locus.contig == "22")
    print(input_data_filtered.count_rows() / input_data.count_rows())
    return input_data_filtered

def subset_grch38_table_data(input_ht):
    input_data = hl.read_table(input_ht)
    input_data_filtered = input_data.filter(input_data.locus.contig == "chr22")
    print(input_data_filtered.count() / input_data.count())
    return input_data_filtered

def subset_grch37_table_data(input_ht):
    input_data = hl.read_table(input_ht)
    input_data_filtered = input_data.filter(input_data.locus.contig == "22")
    print(input_data_filtered.count() / input_data.count())
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
    subset_grch37_matrix_table_data,
    "/autism_crc/subsetted_autism_crc.ht",
    {"input_ht": pipeline.get_task("convert_autism_crc")},
)

pipeline.add_task(
    "subset_v4_sites_data",
    subset_grch38_table_data,
    "/autism_crc/subsetted_v4_sites_data.ht",
    {"input_ht": V4_SITES_DATA_URL}
)

pipeline.add_task(
    "subset_v3_coverage_data",
    subset_grch38_table_data,
    "/autism_crc/subsetted_v3_coverage_data.ht",
    {"input_ht": V3_COVERAGE_DATA_URL}
)

pipeline.add_task(
    "subset_v2_sites_data",
    subset_grch37_table_data,
    "/autism_crc/subsetted_v2_genome_sites_data.ht",
    {"input_ht": V2_SITES_DATA_URL}
)

###############################################
# Run
###############################################

if __name__ == "__main__":
    run_pipeline(pipeline)
