import dynamic from "next/dynamic";

const LazyMarkdownEditor = dynamic(() => import("./MarkdownEditor"), {
  ssr: false,
});

export default LazyMarkdownEditor;
