import PropTypes from 'prop-types'
import React, { useState } from 'react'
import styled from 'styled-components'

import { Button, ExternalLink, List, Modal, PrimaryButton, TextButton } from '@gnomad/ui'

import { withAnchor } from '../AnchorLink'

export const FileList = styled(List)`
  li {
    line-height: 1.25;
  }
`

const BaseSectionTitle = styled.h2``
export const SectionTitle = withAnchor(BaseSectionTitle)

export const ColumnsWrapper = styled.div`
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
`

export const Column = styled.div`
  flex-basis: calc(50% - 25px);

  @media (max-width: 900px) {
    flex-basis: 100%;
  }

  > h3 {
    margin-top: 0;
  }
`

const ShowURLButton = ({ label, url, ...otherProps }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  return (
    <>
      <TextButton
        {...otherProps}
        onClick={() => {
          setIsExpanded(true)
        }}
      />
      {isExpanded && (
        <Modal
          size="large"
          title={label}
          footer={
            <>
              <Button
                onClick={() => {
                  setIsExpanded(false)
                }}
              >
                Ok
              </Button>
              {navigator.clipboard && navigator.clipboard.writeText && (
                <PrimaryButton
                  onClick={() => {
                    navigator.clipboard.writeText(url)
                  }}
                  style={{ marginLeft: '1em' }}
                >
                  Copy URL
                </PrimaryButton>
              )}
            </>
          }
          onRequestClose={() => {
            setIsExpanded(false)
          }}
        >
          {url}
        </Modal>
      )}
    </>
  )
}

ShowURLButton.propTypes = {
  label: PropTypes.string.isRequired,
  url: PropTypes.string.isRequired,
}

export const GetUrlButtons = ({ gcsBucket, label, path, includeAzure }) => {
  return (
    <>
      <span>{label}</span>
      <br />
      Show URL for{' '}
      <ShowURLButton
        aria-label={`Show Google URL for ${label}`}
        label={label}
        url={`gs://${gcsBucket}${path}`}
      >
        Google
      </ShowURLButton>{' '}
      /{' '}
      <ShowURLButton
        aria-label={`Show Amazon URL for ${label}`}
        label={label}
        url={`s3://gnomad-public-us-east-1${path}`}
      >
        Amazon
      </ShowURLButton>
      {includeAzure && (
        <>
          {' '}
          /{' '}
          <ShowURLButton
            aria-label={`Show Microsoft URL for ${label}`}
            label={label}
            url={`https://azureopendatastorage.blob.core.windows.net/gnomad${path}`}
          >
            Microsoft
          </ShowURLButton>
        </>
      )}
      {navigator.clipboard && navigator.clipboard.writeText && (
        <>
          <br />
          Copy URL for{' '}
          <TextButton
            aria-label={`Copy Google URL for ${label}`}
            onClick={() => {
              navigator.clipboard.writeText(`gs://${gcsBucket}${path}`)
            }}
          >
            Google
          </TextButton>{' '}
          /{' '}
          <TextButton
            aria-label={`Copy Amazon URL for ${label}`}
            onClick={() => {
              navigator.clipboard.writeText(`s3://gnomad-public-us-east-1${path}`)
            }}
          >
            Amazon
          </TextButton>
          {includeAzure && (
            <>
              {' '}
              /{' '}
              <TextButton
                aria-label={`Copy Microsoft URL for ${label}`}
                onClick={() => {
                  navigator.clipboard.writeText(
                    `https://azureopendatastorage.blob.core.windows.net/gnomad${path}`
                  )
                }}
              >
                Microsoft
              </TextButton>
            </>
          )}
        </>
      )}
    </>
  )
}

GetUrlButtons.propTypes = {
  gcsBucket: PropTypes.string,
  label: PropTypes.string.isRequired,
  path: PropTypes.string.isRequired,
  includeAzure: PropTypes.bool,
}

GetUrlButtons.defaultProps = {
  gcsBucket: 'gcp-public-data--gnomad',
  includeAzure: true,
}

export const GenericDownloadLinks = ({ gcsBucket, label, path, size, md5 }) => {
  return (
    <>
      <span>{label}</span>
      <br />
      {size && md5 && (
        <>
          <span>
            {size}, MD5:&nbsp;{md5}
          </span>
          <br />
        </>
      )}
      <span>
        Download from{' '}
        <ExternalLink
          aria-label={`Download ${label} from Google`}
          href={`https://storage.googleapis.com/${gcsBucket}${path}`}
        >
          Google
        </ExternalLink>{' '}
        /{' '}
        <ExternalLink
          aria-label={`Download ${label} from Amazon`}
          href={`https://gnomad-public-us-east-1.s3.amazonaws.com${path}`}
        >
          Amazon
        </ExternalLink>{' '}
        /{' '}
        <ExternalLink
          aria-label={`Download ${label} from Microsoft`}
          href={`https://azureopendatastorage.blob.core.windows.net/gnomad${path}`}
        >
          Microsoft
        </ExternalLink>
      </span>
    </>
  )
}

GenericDownloadLinks.propTypes = {
  gcsBucket: PropTypes.string,
  label: PropTypes.string.isRequired,
  path: PropTypes.string.isRequired,
  size: PropTypes.string,
  md5: PropTypes.string,
}

GenericDownloadLinks.defaultProps = {
  gcsBucket: 'gcp-public-data--gnomad',
  size: undefined,
  md5: undefined,
}

export const IndexedFileDownloadLinks = ({ label, path, size, md5, includeAzure }) => {
  return (
    <>
      <span>{label}</span>
      <br />
      {size && md5 && (
        <>
          <span>
            {size}, MD5:&nbsp;{md5}
          </span>
          <br />
        </>
      )}
      <span>
        Download from{' '}
        <ExternalLink
          aria-label={`Download ${label} from Google`}
          href={`https://storage.googleapis.com/gcp-public-data--gnomad${path}`}
        >
          Google
        </ExternalLink>{' '}
        /{' '}
        <ExternalLink
          aria-label={`Download ${label} from Amazon`}
          href={`https://gnomad-public-us-east-1.s3.amazonaws.com${path}`}
        >
          Amazon
        </ExternalLink>
        {includeAzure && (
          <>
            {' '}
            /{' '}
            <ExternalLink
              aria-label={`Download ${label} from Microsoft`}
              href={`https://azureopendatastorage.blob.core.windows.net/gnomad${path}`}
            >
              Microsoft
            </ExternalLink>
          </>
        )}
      </span>
      <br />
      <span>
        Download TBI from{' '}
        <ExternalLink
          aria-label={`Download TBI file for ${label} from Google`}
          href={`https://storage.googleapis.com/gcp-public-data--gnomad${path}.tbi`}
        >
          Google
        </ExternalLink>{' '}
        /{' '}
        <ExternalLink
          aria-label={`Download TBI file for ${label} from Amazon`}
          href={`https://gnomad-public-us-east-1.s3.amazonaws.com${path}.tbi`}
        >
          Amazon
        </ExternalLink>
        {includeAzure && (
          <>
            {' '}
            /{' '}
            <ExternalLink
              aria-label={`Download TBI file for ${label} from Microsoft`}
              href={`https://azureopendatastorage.blob.core.windows.net/gnomad${path}.tbi`}
            >
              Microsoft
            </ExternalLink>
          </>
        )}
      </span>
    </>
  )
}

IndexedFileDownloadLinks.propTypes = {
  label: PropTypes.string.isRequired,
  path: PropTypes.string.isRequired,
  size: PropTypes.string,
  md5: PropTypes.string,
  includeAzure: PropTypes.bool,
}

IndexedFileDownloadLinks.defaultProps = {
  size: undefined,
  md5: undefined,
  includeAzure: true,
}
