import { gql } from "@apollo/client";
import { GlobeAltIcon, LockClosedIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { toast } from "react-toastify";
import MakeWebappPrivateDialog from "webapps/features/MakeWebappPrivateDialog";
import MakeWebappPublicDialog from "webapps/features/MakeWebappPublicDialog";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { WebappVisibilityButton_WebappFragment } from "./WebappVisibilityButton.generated";

type WebappVisibilityButtonProps = {
  webapp: WebappVisibilityButton_WebappFragment;
};

const WebappVisibilityButton = ({ webapp }: WebappVisibilityButtonProps) => {
  const { t } = useTranslation();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [updateWebapp] = useUpdateWebappMutation();
  const clearCache = useCacheKey("webapps");

  if (!webapp.permissions.update) {
    return null;
  }

  const setVisibility = async (isPublic: boolean) => {
    const { data } = await updateWebapp({
      variables: { input: { id: webapp.id, isPublic } },
    });
    if (data?.updateWebapp?.errors?.length) {
      toast.error(t("An error occurred while updating the web app"));
      return;
    }
    setIsDialogOpen(false);
    clearCache();
  };

  return (
    <>
      <Button
        variant="white"
        onClick={() => setIsDialogOpen(true)}
        leadingIcon={
          webapp.isPublic ? (
            <LockClosedIcon className="h-4 w-4" />
          ) : (
            <GlobeAltIcon className="h-4 w-4" />
          )
        }
      >
        {webapp.isPublic ? t("Make private") : t("Make public")}
      </Button>
      {webapp.isPublic ? (
        <MakeWebappPrivateDialog
          open={isDialogOpen}
          onClose={() => setIsDialogOpen(false)}
          onConfirm={() => setVisibility(false)}
          webapp={webapp}
        />
      ) : (
        <MakeWebappPublicDialog
          open={isDialogOpen}
          onClose={() => setIsDialogOpen(false)}
          onConfirm={() => setVisibility(true)}
          webapp={webapp}
        />
      )}
    </>
  );
};

WebappVisibilityButton.fragments = {
  webapp: gql`
    fragment WebappVisibilityButton_webapp on Webapp {
      id
      type
      isPublic
      serveUrl
      permissions {
        update
      }
    }
  `,
};

export default WebappVisibilityButton;
