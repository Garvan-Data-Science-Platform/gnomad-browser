import PropTypes from 'prop-types'
import React from 'react'

import { referenceGenomeForDataset } from '../datasets'
import Query from '../Query'
import MitochondrialVariants from '../MitochondrialVariantList/MitochondrialVariants'

const query = `
query MitochondrialVariantsInRegion($start: Int!, $stop: Int!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
  region(chrom: "M", start: $start, stop: $stop, reference_genome: $referenceGenome) {
    mitochondrial_variants(dataset: $datasetId) {
      ac_het
      ac_hom
      an
      consequence
      filters
      flags
      gene_id
      gene_symbol
      transcript_id
      hgvsc
      hgvsp
      lof
      lof_filter
      lof_flags
      max_heteroplasmy
      pos
      reference_genome
      rsid
      variant_id
    }
  }
}
`

const MitochondrialVariantsInRegion = ({ datasetId, region, ...rest }) => {
  return (
    <Query
      query={query}
      variables={{
        datasetId,
        start: region.start,
        stop: region.stop,
        referenceGenome: referenceGenomeForDataset(datasetId),
      }}
      loadingMessage="Loading variants"
      errorMessage="Unable to load variants"
      success={data => data.region && data.region.mitochondrial_variants}
    >
      {({ data }) => {
        const regionId = `${region.chrom}-${region.start}-${region.stop}`

        data.region.mitochondrial_variants.forEach(v => {
          /* eslint-disable no-param-reassign */
          if (v.an !== 0) {
            v.af = (v.ac_het + v.ac_hom) / v.an
            v.af_het = v.ac_het / v.an
            v.af_hom = v.ac_hom / v.an
          } else {
            v.af = 0
            v.af_het = 0
            v.af_hom = 0
          }
          v.hgvs = v.hgvsp || v.hgvsc
          /* eslint-enable no-param-reassign */
        })

        return (
          <MitochondrialVariants
            {...rest}
            chrom={region.chrom}
            exportFileName={`gnomad_mitochondrial_variants_${regionId}`}
            variants={data.region.mitochondrial_variants}
          />
        )
      }}
    </Query>
  )
}

MitochondrialVariantsInRegion.propTypes = {
  datasetId: PropTypes.string.isRequired,
  region: PropTypes.shape({
    chrom: PropTypes.string.isRequired,
    start: PropTypes.number.isRequired,
    stop: PropTypes.number.isRequired,
  }).isRequired,
}

export default MitochondrialVariantsInRegion
