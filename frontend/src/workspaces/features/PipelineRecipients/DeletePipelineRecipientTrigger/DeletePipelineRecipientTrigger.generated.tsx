import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
export type DeletePipelineRecipientTrigger_RecipientFragment = { __typename?: 'PipelineRecipient', id: string, user: { __typename?: 'User', displayName: string } };

export type DeletePipelineRecipientTrigger_PipelineFragment = { __typename?: 'Pipeline', permissions: { __typename?: 'PipelinePermissions', update: boolean } };

export const DeletePipelineRecipientTrigger_RecipientFragmentDoc = gql`
    fragment DeletePipelineRecipientTrigger_recipient on PipelineRecipient {
  id
  user {
    displayName
  }
}
    `;
export const DeletePipelineRecipientTrigger_PipelineFragmentDoc = gql`
    fragment DeletePipelineRecipientTrigger_pipeline on Pipeline {
  permissions {
    update
  }
}
    `;