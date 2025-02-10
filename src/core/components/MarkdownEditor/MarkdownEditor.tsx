import {
  BlockTypeSelect,
  BoldItalicUnderlineToggles,
  ChangeAdmonitionType,
  ChangeCodeMirrorLanguage,
  CodeToggle,
  ConditionalContents,
  EditorInFocus,
  InsertCodeBlock,
  InsertThematicBreak,
  ListsToggle,
  MDXEditor,
  MDXEditorProps,
  Separator,
  StrikeThroughSupSubToggles,
  UndoRedo,
  codeBlockPlugin,
  codeMirrorPlugin,
  headingsPlugin,
  linkDialogPlugin,
  linkPlugin,
  listsPlugin,
  markdownShortcutPlugin,
  quotePlugin,
  thematicBreakPlugin,
  toolbarPlugin,
} from "@mdxeditor/editor";
import "@mdxeditor/editor/style.css";
import clsx from "clsx";
import styles from "./MarkdownEditor.module.css";

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
  ...delegated
}: MarkdownEditorProps) => {
  return (
    <div
      className={clsx(
        "rounded-md border border-gray-300 overflow-y-auto",
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
        plugins={[
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
                      </>
                    ),
                  },
                ]}
              />
            ),
          }),
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
        ]}
        {...delegated}
      />
    </div>
  );
};

export default MarkdownEditor;
