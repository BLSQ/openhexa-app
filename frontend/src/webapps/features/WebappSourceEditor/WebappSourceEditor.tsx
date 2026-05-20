import { useCallback, useState } from "react";
import { useTranslation } from "next-i18next";
import type { FileWithPath } from "react-dropzone";
import Tabs from "core/components/Tabs";
import CodeEditor from "core/components/CodeEditor";
import Dropzone from "core/components/Dropzone";
import { FileEncoding, WebappFileInput } from "graphql/types";
import { fileToBase64 } from "core/helpers/fileEncoding";

type WebappSourceEditorProps = {
  initialTemplate: string;
  onChange: (files: WebappFileInput[]) => void;
};

const WebappSourceEditor = ({
  initialTemplate,
  onChange,
}: WebappSourceEditorProps) => {
  const { t } = useTranslation();
  const [templateContent, setTemplateContent] = useState(initialTemplate);

  const handleTemplateChange = useCallback(
    (value: string) => {
      setTemplateContent(value);
      onChange([
        { path: "index.html", content: value, encoding: FileEncoding.Text },
      ]);
    },
    [onChange],
  );

  const handleFileDrop = useCallback(
    async (acceptedFiles: readonly FileWithPath[]) => {
      onChange(
        await Promise.all(
          acceptedFiles.map(async (file) => ({
            path: (file.path || file.webkitRelativePath || file.name).replace(/^\//, ""),
            content: await fileToBase64(file),
            encoding: FileEncoding.Base64,
          })),
        ),
      );
    },
    [onChange],
  );

  return (
    <Tabs defaultIndex={0}>
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
