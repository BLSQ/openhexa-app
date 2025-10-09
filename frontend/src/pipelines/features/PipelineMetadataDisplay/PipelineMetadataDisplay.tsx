import { gql } from "@apollo/client";
import Badge from "core/components/Badge";
import Tag from "core/features/Tag";
import { useTranslation } from "next-i18next";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";
import {
  PipelineMetadataDisplay_PipelineFragment,
  PipelineMetadataDisplay_TemplateFragment,
} from "./PipelineMetadataDisplay.generated";

type PipelineMetadataDisplayProps = {
  metadata:
    | PipelineMetadataDisplay_PipelineFragment
    | PipelineMetadataDisplay_TemplateFragment;
  showLabels?: boolean;
  size?: "sm" | "md";
  className?: string;
};

const PipelineMetadataDisplay = ({
  metadata,
  showLabels = true,
  size = "md",
  className = "",
}: PipelineMetadataDisplayProps) => {
  const { t } = useTranslation();
  const textSize = size === "sm" ? "text-xs" : "text-sm";

  return (
    <div className={`space-y-2 ${className}`}>
      {metadata.functionalType && (
        <div className="flex items-center gap-2">
          {showLabels && (
            <span className={`${textSize} text-gray-500`}>{t("Type")}:</span>
          )}
          <Badge className={textSize}>
            {formatPipelineFunctionalType(metadata.functionalType)}
          </Badge>
        </div>
      )}
      {metadata.tags && metadata.tags.length > 0 && (
        <div className="flex items-start gap-2">
          {showLabels && (
            <span className={`${textSize} text-gray-500 mt-0.5`}>
              {t("Tags")}:
            </span>
          )}
          <div className="flex flex-wrap gap-1">
            {metadata.tags.map((tag) => (
              <Tag key={tag.id} tag={tag} className={textSize} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

PipelineMetadataDisplay.fragments = {
  pipeline: gql`
    fragment PipelineMetadataDisplay_pipeline on Pipeline {
      functionalType
      tags {
        ...Tag_tag
      }
    }
    ${Tag.fragments.tag}
  `,
  template: gql`
    fragment PipelineMetadataDisplay_template on PipelineTemplate {
      functionalType
      tags {
        ...Tag_tag
      }
    }
    ${Tag.fragments.tag}
  `,
};

export default PipelineMetadataDisplay;
