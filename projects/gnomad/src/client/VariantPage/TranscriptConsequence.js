import PropTypes from 'prop-types'
import React from 'react'
import styled from 'styled-components'

import { getCategoryFromConsequence } from '@broad/utilities'

import Link from '../Link'
import { LofteeFilter, LofteeFlag } from './Loftee'
import TranscriptConsequencePropType from './TranscriptConsequencePropType'

const AttributeName = styled.dt`
  display: inline;

  ::after {
    content: ': ';
  }
`

const AttributeValue = styled.dd`
  display: inline;
  margin: 0;
`

const AttributeList = styled.dl`
  display: flex;
  flex-direction: column;
  margin: 0;
`

const Attribute = ({ children, name }) => (
  <div style={{ marginTop: '0.25em' }}>
    <AttributeName>{name}</AttributeName>
    <AttributeValue>{children}</AttributeValue>
  </div>
)

Attribute.propTypes = {
  children: PropTypes.node.isRequired,
  name: PropTypes.string.isRequired,
}

const Marker = styled.span`
  display: inline-block;
  width: 10px;
  height: 10px;

  &::before {
    content: '';
    display: inline-block;
    box-sizing: border-box;
    width: 10px;
    height: 10px;
    border: 1px solid #000;
    border-radius: 5px;
    background: ${props => props.color};
  }
`

const colors = {
  red: '#FF583F',
  yellow: '#F0C94D',
  green: 'green',
}

const lofteeAnnotationMarker = consequence => {
  switch (consequence.lof) {
    case 'HC':
      return <Marker color={colors.green} />
    case 'OS':
      return null
    case 'LC':
    default:
      return <Marker color={colors.red} />
  }
}

const lofteeAnnotationDescription = consequence => {
  switch (consequence.lof) {
    case 'HC':
      return 'High-confidence'
    case 'OS':
      return 'Other splice (beta)'
    case 'LC':
      return (
        <span>
          Low-confidence (
          {consequence.lof_filter
            .split(',')
            .map(filter => <LofteeFilter key={filter} filter={filter} />)
            .reduce((acc, el, i) => (i === 0 ? [...acc, el] : [...acc, ' ', el]), [])}
          )
        </span>
      )
    default:
      return consequence.lof
  }
}

const TranscriptConsequenceDetails = ({ consequence }) => {
  const category = getCategoryFromConsequence(consequence.major_consequence)

  if (category === 'missense') {
    const polyphenColor =
      {
        benign: colors.green,
        possibly_damaging: colors.yellow,
      }[consequence.polyphen_prediction] || colors.red

    const siftColor = consequence.sift_prediction === 'tolerated' ? colors.green : colors.red

    return (
      <AttributeList>
        <Attribute name="HGVSp">{consequence.hgvs}</Attribute>
        {consequence.polyphen_prediction && (
          <Attribute name="Polyphen">
            <Marker color={polyphenColor} /> {consequence.polyphen_prediction}
          </Attribute>
        )}
        {consequence.sift_prediction && (
          <Attribute name="SIFT">
            <Marker color={siftColor} /> {consequence.sift_prediction}
          </Attribute>
        )}
      </AttributeList>
    )
  }

  if (
    // "NC" annotations were removed from the data pipeline some time ago.
    // Some ExAC variants still have them.
    consequence.lof === 'NC' ||
    (category === 'lof' && !consequence.lof) // See gnomadjs#364.
  ) {
    return (
      <AttributeList>
        <Attribute name="HGVSp">{consequence.hgvs}</Attribute>
        <Attribute name="pLoF">
          <Marker color={colors.red} /> Low-confidence (Non-protein-coding transcript)
        </Attribute>
      </AttributeList>
    )
  }

  if (consequence.lof) {
    return (
      <AttributeList>
        <Attribute name="HGVSp">{consequence.hgvs}</Attribute>
        <Attribute name="pLoF">
          {lofteeAnnotationMarker(consequence)} {lofteeAnnotationDescription(consequence)}
        </Attribute>
        {consequence.lof_flags && (
          <Attribute name="Flag">
            <Marker color={colors.yellow} />{' '}
            {consequence.lof_flags
              .split(',')
              .map(flag => <LofteeFlag key={flag} flag={flag} />)
              .reduce((acc, el, i) => (i === 0 ? [...acc, el] : [...acc, ' ', el]), [])}
          </Attribute>
        )}
      </AttributeList>
    )
  }

  return null
}

TranscriptConsequenceDetails.propTypes = {
  consequence: TranscriptConsequencePropType.isRequired,
}

const TranscriptConsequence = ({ consequence }) => (
  <div>
    <Link to={`/gene/${consequence.gene_id}/transcript/${consequence.transcript_id}`}>
      {consequence.transcript_id}
      {consequence.canonical && ' *'}
    </Link>
    <TranscriptConsequenceDetails consequence={consequence} />
  </div>
)

TranscriptConsequence.propTypes = {
  consequence: TranscriptConsequencePropType.isRequired,
}

export default TranscriptConsequence
