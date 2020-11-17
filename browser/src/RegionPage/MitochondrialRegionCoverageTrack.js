import PropTypes from 'prop-types'
import React from 'react'

import { referenceGenomeForDataset } from '../datasets'
import Query from '../Query'
import CoverageTrack from '../CoverageTrack'

const query = `
query MitochondrialCoverageInRegion($start: Int!, $stop: Int!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
  region(chrom: "M", start: $start, stop: $stop, reference_genome: $referenceGenome) {
    mitochondrial_coverage(dataset: $datasetId) {
      pos
      mean
      median
      over_100
      over_1000
    }
  }
}
`

const MitochondrialRegionCoverageTrack = ({ datasetId, start, stop }) => {
  return (
    <Query
      query={query}
      variables={{ datasetId, start, stop, referenceGenome: referenceGenomeForDataset(datasetId) }}
      loadingMessage="Loading coverage"
      errorMessage="Unable to load coverage"
      success={data => data.region && data.region.mitochondrial_coverage}
    >
      {({ data }) => {
        const coverage = [
          {
            color: 'rgb(115, 171, 61)',
            buckets: data.region.mitochondrial_coverage,
            name: 'mitochondrial genome',
            opacity: 0.7,
          },
        ]

        return (
          <CoverageTrack
            coverageOverThresholds={[100, 1000]}
            datasets={coverage}
            filenameForExport={() => `M-${start}-${stop}_coverage`}
            height={190}
            maxCoverage={3000}
          />
        )
      }}
    </Query>
  )
}

MitochondrialRegionCoverageTrack.propTypes = {
  datasetId: PropTypes.string.isRequired,
  start: PropTypes.number.isRequired,
  stop: PropTypes.number.isRequired,
}

export default MitochondrialRegionCoverageTrack
