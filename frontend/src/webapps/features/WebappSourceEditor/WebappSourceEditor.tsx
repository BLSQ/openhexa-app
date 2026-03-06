import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import Tabs from "core/components/Tabs";
import CodeEditor from "core/components/CodeEditor";
import Dropzone from "core/components/Dropzone";
import { WebappFileInput, WebappType } from "graphql/types";
import { DEFAULT_HTML_TEMPLATE } from "webapps/helpers/templates";

type WebappSourceEditorProps = {
  type: WebappType;
  onChange: (files: WebappFileInput[]) => void;
};

const WebappSourceEditor = ({ type, onChange }: WebappSourceEditorProps) => {
  const { t } = useTranslation();
  const [templateContent, setTemplateContent] = useState(DEFAULT_HTML_TEMPLATE);

  useEffect(() => {
    if (type === WebappType.Html) {
      onChange([{ path: "index.html", content: DEFAULT_HTML_TEMPLATE }]);
    }
  }, []);

  const handleTemplateChange = useCallback(
    (value: string) => {
      setTemplateContent(value);
      onChange([{ path: "index.html", content: value }]);
    },
    [onChange],
  );

  const handleFileDrop = useCallback(
    async (acceptedFiles: readonly File[]) => {
      onChange(
        await Promise.all(
          acceptedFiles.map(async (file) => ({
            path: file.name,
            content: await file.text(),
          })),
        ),
      );
    },
    [onChange],
  );

  const defaultIndex = type === WebappType.Bundle ? 1 : 0;

  return (
    <Tabs defaultIndex={defaultIndex}>
      <Tabs.Tab label={t("Template")}>
        <div className="pt-4">
          <CodeEditor
            lang="xml"
            value={templateContent}
            onChange={handleTemplateChange}
            minHeight="300px"
          />
        </div>
      </Tabs.Tab>
      <Tabs.Tab label={t("Upload Files")}>
        <div className="pt-4">
          <Dropzone
            className="h-48"
            label={t("Drop your files here")}
            onChange={handleFileDrop}
          />
        </div>
      </Tabs.Tab>
    </Tabs>
  );
};

export default WebappSourceEditor;
