import PropTypes from 'prop-types'
import React from 'react'

import { referenceGenomeForDataset } from '../datasets'
import Query from '../Query'
import MitochondrialVariants from '../MitochondrialVariantList/MitochondrialVariants'

const query = `
query MitochondrialVariantsInTranscript($transcriptId: String!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
  transcript(transcript_id: $transcriptId, reference_genome: $referenceGenome) {
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

const MitochondrialVariantsInTranscript = ({ datasetId, transcript, ...rest }) => {
  return (
    <Query
      query={query}
      variables={{
        datasetId,
        transcriptId: transcript.transcript_id,
        referenceGenome: referenceGenomeForDataset(datasetId),
      }}
      loadingMessage="Loading variants"
      errorMessage="Unable to load variants"
      success={data => data.transcript && data.transcript.mitochondrial_variants}
    >
      {({ data }) => {
        data.transcript.mitochondrial_variants.forEach(v => {
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
            exportFileName={`gnomad_mitochondrial_variants_${transcript.transcript_id}`}
            variants={data.transcript.mitochondrial_variants}
          />
        )
      }}
    </Query>
  )
}

MitochondrialVariantsInTranscript.propTypes = {
  datasetId: PropTypes.string.isRequired,
  transcript: PropTypes.shape({
    transcript_id: PropTypes.string.isRequired,
  }).isRequired,
}

export default MitochondrialVariantsInTranscript
