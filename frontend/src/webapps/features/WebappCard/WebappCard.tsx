import { gql } from "@apollo/client";
import Card from "core/components/Card";
import { WebappCard_WebappFragment } from "./WebappCard.generated";
import React from "react";
import { PlayIcon } from "@heroicons/react/24/outline";

type WebappCardProps = {
  webapp: WebappCard_WebappFragment;
};

const WebappCard = ({ webapp }: WebappCardProps) => {
  const { workspace, slug, name, icon } = webapp;
  return (
    <Card
      href={{
        pathname: "/workspaces/[workspaceSlug]/webapps/[webappSlug]/play",
        query: { workspaceSlug: workspace.slug, webappSlug: slug },
      }}
      title={
        <div className={"flex items-center"}>
          {icon && (
            <img src={icon} className="h-8 w-8 rounded mr-3" alt={"Icon"} />
          )}
          <h3 className="text-lg font-semibold">{name}</h3>
        </div>
      }
    >
      <div className={"flex items-center justify-end"}>
        <div
          className={
            "flex items-center justify-center bg-blue-500 rounded-full h-8 w-8 hover:bg-blue-600 cursor-pointer hover:scale-110"
          }
        >
          <PlayIcon className="h-4 w-4 text-white fill-white translate-x-0.25" />
        </div>
      </div>
    </Card>
  );
};

WebappCard.fragments = {
  webapp: gql`
    fragment WebappCard_webapp on Webapp {
      id
      slug
      icon
      name
      workspace {
        slug
        name
      }
    }
  `,
};

export default WebappCard;
