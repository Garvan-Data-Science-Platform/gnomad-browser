import hail as hl
import os

# requires adding the gnomad_methods library to your python env
from gnomad.utils.reference_genome import get_reference_ht
from gnomad.utils.sparse_mt import compute_coverage_stats


def prepare_autism_crc_coverage(path):
    ref = get_reference_ht(hl.get_reference("GRCh37"))
    ds = hl.read_matrix_table(path)
    ht_with_stats = compute_coverage_stats(ds, ref)
    ht_with_stats = ht_with_stats.naive_coalesce(5000)
    return ht_with_stats
