import PropTypes from 'prop-types'
import React from 'react'

import { referenceGenomeForDataset } from '../datasets'
import Query from '../Query'
import StructuralVariants from '../StructuralVariantList/StructuralVariants'

const StructuralVariantsInRegion = ({ datasetId, region, ...rest }) => {
  const query = `
    query StructuralVariantsInRegion($datasetId: StructuralVariantDatasetId!, $chrom: String!, $start: Int!, $stop: Int!, $referenceGenome: ReferenceGenomeId!) {
      region(chrom: $chrom, start: $start, stop: $stop, reference_genome: $referenceGenome) {
        structural_variants(dataset: $datasetId) {
          ac
          ac_hom
          an
          af
          chrom
          chrom2
          end
          end2
          consequence
          filters
          length
          pos
          pos2
          type
          variant_id
        }
      }
    }
  `

  return (
    <Query
      query={query}
      variables={{
        datasetId,
        chrom: region.chrom,
        start: region.start,
        stop: region.stop,
        referenceGenome: referenceGenomeForDataset(datasetId),
      }}
      loadingMessage="Loading variants"
      errorMessage="Unable to load variants"
      success={data => data.region && data.region.structural_variants}
    >
      {({ data }) => {
        const regionId = `${region.chrom}-${region.start}-${region.stop}`

        return (
          <StructuralVariants
            {...rest}
            chrom={region.chrom}
            exportFileName={`gnomad_structural_variants_${regionId}`}
            variants={data.region.structural_variants}
          />
        )
      }}
    </Query>
  )
}

StructuralVariantsInRegion.propTypes = {
  datasetId: PropTypes.string.isRequired,
  region: PropTypes.shape({
    chrom: PropTypes.string.isRequired,
    start: PropTypes.number.isRequired,
    stop: PropTypes.number.isRequired,
  }).isRequired,
}

export default StructuralVariantsInRegion
