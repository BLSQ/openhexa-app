import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import {
  GetFileDownloadUrlMutation,
  GetFileDownloadUrlMutationVariables,
  DeleteBucketObjectMutation,
  DeleteBucketObjectMutationVariables,
  GetBucketUploadUrlMutation,
  GetBucketUploadUrlMutationVariables,
} from "./bucket.generated";

export async function getBucketObjectDownloadUrl(
  workspaceSlug: string,
  objectKey: string,
): Promise<string> {
  const client = getApolloClient();
  const { data } = await client.mutate<
    GetFileDownloadUrlMutation,
    GetFileDownloadUrlMutationVariables
  >({
    mutation: gql`
      mutation GetFileDownloadUrl($input: PrepareObjectDownloadInput!) {
        prepareObjectDownload(input: $input) {
          success
          downloadUrl
        }
      }
    `,
    variables: {
      input: {
        workspaceSlug,
        objectKey,
      },
    },
  });

  if (data?.prepareObjectDownload?.success) {
    return data.prepareObjectDownload.downloadUrl as string;
  } else {
    throw new Error("Object cannot be downloaded");
  }
}

export async function downloadURL(url: string, target: string = "") {
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.target = target;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
}

export async function deleteBucketObject(
  workspaceSlug: string,
  objectKey: string,
) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    DeleteBucketObjectMutation,
    DeleteBucketObjectMutationVariables
  >({
    mutation: gql`
      mutation deleteBucketObject($input: DeleteBucketObjectInput!) {
        deleteBucketObject(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { workspaceSlug, objectKey } },
    update(cache) {
      const normalizedId = cache.identify({
        key: objectKey,
        __typename: "BucketObject",
      });

      cache.evict({ id: normalizedId });
      cache.gc();
    },
  });

  if (!data?.deleteBucketObject.success) {
    throw new Error("Unexpected error.");
  }
}

export async function getBucketObjectUploadUrl(
  workspaceSlug: string,
  key: string,
  contentType: string,
) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    GetBucketUploadUrlMutation,
    GetBucketUploadUrlMutationVariables
  >({
    mutation: gql`
      mutation GetBucketUploadUrl($input: PrepareObjectUploadInput!) {
        prepareObjectUpload(input: $input) {
          success
          uploadUrl
        }
      }
    `,
    variables: {
      input: {
        workspaceSlug,
        objectKey: key,
        contentType,
      },
    },
  });

  if (data?.prepareObjectUpload?.success) {
    return data.prepareObjectUpload.uploadUrl as string;
  } else {
    throw new Error("Object cannot be uploaded");
  }
}

export async function createBucketFolder(
  workspaceSlug: string,
  folderKey: string,
) {
  const client = getApolloClient();
  const { data } = await client.mutate({
    mutation: gql`
      mutation CreateBucketFolder($input: CreateBucketFolderInput!) {
        createBucketFolder(input: $input) {
          success
          errors
          folder {
            key
            name
            type
          }
        }
      }
    `,
    variables: {
      input: {
        workspaceSlug,
        folderKey,
      },
    },
  });

  if (!data?.createBucketFolder.success) {
    throw new Error("Unexpected error.");
  }

  return data.createBucketFolder.folder;
}
