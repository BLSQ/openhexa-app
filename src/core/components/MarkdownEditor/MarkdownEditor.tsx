import {
  BlockTypeSelect,
  BoldItalicUnderlineToggles,
  ChangeAdmonitionType,
  ChangeCodeMirrorLanguage,
  codeBlockPlugin,
  codeMirrorPlugin,
  CodeToggle,
  ConditionalContents,
  EditorInFocus,
  headingsPlugin,
  imagePlugin,
  InsertCodeBlock,
  InsertImage,
  InsertThematicBreak,
  linkDialogPlugin,
  linkPlugin,
  listsPlugin,
  ListsToggle,
  markdownShortcutPlugin,
  MDXEditor,
  MDXEditorProps,
  quotePlugin,
  Separator,
  StrikeThroughSupSubToggles,
  thematicBreakPlugin,
  toolbarPlugin,
  UndoRedo,
} from "@mdxeditor/editor";
import "@mdxeditor/editor/style.css";
import clsx from "clsx";
import styles from "./MarkdownEditor.module.css";
import { useMemo } from "react";

export type MarkdownEditorProps = MDXEditorProps & {
  sm?: boolean;
};

function whenInAdmonition(editorInFocus: EditorInFocus | null) {
  const node = editorInFocus?.rootNode;
  if (!node || node.getType() !== "directive") {
    return false;
  }

  return true;
}

const MarkdownEditor = ({
  className,
  markdown,
  sm,
  readOnly,
  ...delegated
}: MarkdownEditorProps) => {
  const plugins = useMemo(() => {
    const basePlugins = [
      headingsPlugin(),
      quotePlugin(),
      listsPlugin(),
      codeBlockPlugin({ defaultCodeBlockLanguage: "txt" }),
      codeMirrorPlugin({
        codeBlockLanguages: {
          python: "Python",
          js: "JavaScript",
          css: "CSS",
          txt: "text",
        },
      }),
      thematicBreakPlugin(),
      linkPlugin(),
      linkDialogPlugin(),
      markdownShortcutPlugin(),
      imagePlugin({ disableImageResize: readOnly }),
    ];

    if (!readOnly) {
      basePlugins.push(
        toolbarPlugin({
          toolbarClassName: styles.toolbar,
          toolbarContents: () => (
            <ConditionalContents
              options={[
                {
                  when: (editor) => editor?.editorType === "codeblock",
                  contents: () => <ChangeCodeMirrorLanguage />,
                },
                {
                  fallback: () => (
                    <>
                      <UndoRedo />
                      <Separator />
                      <BoldItalicUnderlineToggles />
                      <CodeToggle />
                      <Separator />
                      <StrikeThroughSupSubToggles />
                      <Separator />
                      <ListsToggle options={["bullet", "number"]} />
                      <Separator />
                      <ConditionalContents
                        options={[
                          {
                            when: whenInAdmonition,
                            contents: () => <ChangeAdmonitionType />,
                          },
                          { fallback: () => <BlockTypeSelect /> },
                        ]}
                      />
                      <Separator />
                      <InsertThematicBreak />
                      <Separator />
                      <InsertCodeBlock />
                      <InsertImage />
                    </>
                  ),
                },
              ]}
            />
          ),
        }),
      );
    }
    return basePlugins;
  }, [readOnly]);

  return (
    <div
      className={clsx(
        "rounded-md overflow-y-auto",
        !readOnly && "border border-gray-300",
        className,
      )}
    >
      <MDXEditor
        data-testid="markdown-editor"
        markdown={markdown}
        contentEditableClassName={clsx(
          "max-w-none p-2 ring-none outline-none",
          // Standard styles
          "prose prose-headings:font-medium prose-h1:font-medium",
          // Small styles
          sm &&
            "prose-sm prose-h1:text-xl prose-h2:text-lg prose-h3:text-md prose-h2:mt-0",
          styles.editor,
        )}
        plugins={plugins}
        readOnly={readOnly}
        {...delegated}
      />
    </div>
  );
};

export default MarkdownEditor;
