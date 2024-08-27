import argparse
import sys

from gnomad_qc.v2.resources import *


def import_vcf(vcf,
               min_block_size: int = 1536,
               force_bgz: bool = True,
               header=None):

    hl.init(min_block_size=min_block_size)

    mt = hl.import_vcf(
        vcf,
        force_bgz=force_bgz,
        call_fields=["GT", "PGT"],
        header_file=header if header else None,
    )

    mt = mt.key_rows_by(**hl.min_rep(mt.locus, mt.alleles))

    #mt.write(output_file, overwrite=overwrite)
    return mt


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--exomes", help="Input VCFs are exomes", action="store_true")
#     parser.add_argument("--genomes", help="Input VCFs are genomes", action="store_true")
#     parser.add_argument("--vcf", help="Location of VCF files.")
#     parser.add_argument("--header", help="Header file if not using VCF header.")
#     parser.add_argument(
#         "--min_block_size",
#         help="Minimum file split size in MB.",
#         type=int,
#         default=1536,
#     )
#     parser.add_argument(
#         "--force_bgz",
#         help="Forces BGZ decoding for VCF files with .gz extension.",
#         action="store_true",
#     )
#     parser.add_argument(
#         "--overwrite", help="Overwrite if MT exists already.", action="store_true"
#     )
#     parser.add_argument(
#         "--slack_channel", help="Slack channel to post results and notifications to."
#     )

#     args = parser.parse_args()
#     if int(args.exomes) + int(args.genomes) != 1:
#         sys.exit("Error: One and only one of --exomes or --genomes must be specified.")

#     if args.exomes:
#         sys.exit("Exome VCFs aren't cloudable :(")

#     if args.slack_channel:
#         with slack_notifications(slack_token, args.slack_channel):
#             main(args)
#     else:
#         main(args)
