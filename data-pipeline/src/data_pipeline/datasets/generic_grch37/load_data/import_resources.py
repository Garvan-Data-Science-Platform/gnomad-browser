# import argparse

# from gnomad.utils.slack import slack_notifications

# from gnomad_qc.slack_creds import slack_token
from gnomad_qc.v2.resources import *


def import_clinvar(clinvar_vcf_path, vep_config):
    from datetime import datetime

    clinvar_ht = hl.import_vcf(
        clinvar_vcf_path, min_partitions=500, skip_invalid_loci=True, force_bgz=True
    ).rows()
    clinvar_ht = clinvar_ht.annotate_globals(
        imported_on=datetime.now().strftime("%Y-%m-%d")
    )
    clinvar_ht = hl.vep(clinvar_ht, vep_config)
    return clinvar_ht


# "gs://gnomad/resources/validated_de_novos.txt.bgz"
def import_de_novos(de_novos_path):
    denovo_ht = hl.import_table(
        de_novos_path, types={"pos": hl.tint32}
    )
    denovo_ht = denovo_ht.transmute(
        locus=hl.locus(hl.str(denovo_ht.chrom), denovo_ht.pos)
    )
    denovo_ht = denovo_ht.annotate(
        alleles=hl.min_rep(denovo_ht.locus, [denovo_ht.ref, denovo_ht.alt])[1]
    )
    denovo_ht = denovo_ht.drop("ref", "alt").key_by("locus", "alleles")
    return denovo_ht

# data_path = "gs://gnomad-resources/methylation/source/all_methylation.txt.bgz"
        # "gs://hail-common/references/grch37_to_grch38.over.chain.gz", ref_38
def import_methylation(all_methylation_path):
    kt = hl.import_table(all_methylation_path, impute=True, min_partitions=100)
    kt = kt.transmute(CHROM=hl.cond(kt["#CHROM"] == "M", "MT", kt["#CHROM"]))
    kt = kt.transmute(locus=hl.locus(kt.CHROM, kt.POS))
    ht = kt.key_by("locus")
    return ht


# vcf_path = "gs://gcp-public-data--gnomad/legacy/exac_browser/ExAC.r1.sites.vep.vcf.gz"
# input vcf looks like it already has VEP annotations
def import_exac_data(exac_path):
    vds = hl.import_vcf(exac_path, force_bgz=True, min_partitions=5000,array_elements_required=False).rows()
    vds = hl.split_multi_hts(vds)
    return vds

# "gs://gcp-public-data--gnomad/resources/methylation/cpg.vcf.bgz",
def import_cpgs(cpg_bgz_path, cpg_sites_ht_path, overwrite: bool = False):
    return hl.import_vcf(
        min_partitions=20,
    ).rows().write(cpg_sites_ht_path, overwrite)


# root = "gs://gcp-public-data--gnomad/truth-sets"
# root_out = "gs://gnomad-public-requester-pays/truth-sets"
# current_version (used to be hail version)
def import_truth_sets(root_path, root_out_path, current_version, overwrite: bool = False):
    truth_sets = [
        "1000G_omni2.5.b37.vcf.bgz",
        "hapmap_3.3.b37.vcf.bgz",
        "Mills_and_1000G_gold_standard.indels.b37.vcf.bgz",
        "NA12878_GIAB_highconf_CG-IllFB-IllGATKHC-Ion-Solid-10X_CHROM1-X_v3.3_highconf.vcf.bgz",
        "hybrid.m37m.vcf.bgz",
        "1000G_phase1.snps.high_confidence.b37.vcf.bgz",
    ]
    for truth_vcf in truth_sets:
        mt_path = truth_vcf.replace(".vcf.bgz", ".mt")
        mt = hl.import_vcf("{}/source/{}".format(root_path, truth_vcf), min_partitions=10)
        hl.split_multi_hts(mt).write(
            "{}/hail-{}/{}".format(root_out_path, current_version, mt_path), overwrite
        )


# def main(args):
#     hl.init(min_block_size=0)

#     if args.import_truth_sets:
#         import_truth_sets(args.overwrite)

#     if args.import_cpgs:
#         import_cpgs(args.overwrite)

#     if args.import_methylation:
#         import_methylation(args.overwrite)

#     if args.import_exac_data:
#         import_exac_data(args.overwrite)

#     if args.import_clinvar:
#         import_clinvar(args.overwrite)


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--slack_channel", help="Slack channel to post results and notifications to."
#     )
#     parser.add_argument(
#         "--import_truth_sets", help="Import truth data", action="store_true"
#     )
#     parser.add_argument("--import_cpgs", help="Import CpG data", action="store_true")
#     parser.add_argument(
#         "--import_methylation", help="Import methylation data", action="store_true"
#     )
#     parser.add_argument(
#         "--import_exac_data", help="Import ExAC data", action="store_true"
#     )
#     parser.add_argument(
#         "--import_clinvar", help="Import clinvar data", action="store_true"
#     )
#     parser.add_argument("--overwrite", help="Overwrite data", action="store_true")
#     args = parser.parse_args()

#     if args.slack_channel:
#         with slack_notifications(slack_token, args.slack_channel):
#             main(args)
#     else:
#         main(args)

# # v1
# hc = HailContext(min_block_size=32)
# hc.import_vcf('gs://exac2/ExAC.r1.sites.vep.vcf.gz', sites_only=True, force_bgz=True).vep(config=vep_config).write(final_exac_sites_vds)

# exac = hc.import_vcf("gs://gnomad/raw/hail-0.1/vds/exac/exac_all.vcf.gz", header_file="gs://gnomad/raw/hail-0.1/vds/exac/header.vcf", force_bgz=True).min_rep().write("gs://gnomad/raw/hail-0.1/vds/exac/exac.vds")

# Raw counts:
# print hc.import_vcf('gs://exac2/variantqc/ExAC.merged.sites_only.vcf.ICfiltered.recalibrated.vcf.bgz').query_variants('variants.count()')[0]  # 18444471 sites
# print
# hc.read('gs://exac2/variantqc/exac2_vqsr.vds').query_variants('variants.count()')[0]
# 21352671 variants
