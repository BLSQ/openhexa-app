import { getPublicEnv } from "core/helpers/runtimeConfig";
import BaseDocument, { Html, Head, Main, NextScript } from "next/document";

class Document extends BaseDocument {
  render() {
    return (
      <Html className="bg-gray-100">
        <Head>
          <link rel="icon" href="/static/img/favicon.png" />
          <script
            dangerouslySetInnerHTML={{
              __html: `window.__ENV__ = ${JSON.stringify(getPublicEnv())};`,
            }}
          />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default Document;
