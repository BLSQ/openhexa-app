import BaseDocument, { Html, Head, Main, NextScript } from "next/document";
import Script from "next/script";

class Document extends BaseDocument {
  render() {
    return (
      <Html className="h-full bg-gray-100">
        <Head>
          <link rel="icon" href="/static/img/favicon.png" />
          {process.env.TELEMETRY_ID && (
            <Script
              src="https://plausible.io/js/script.js"
              strategy="lazyOnload"
              data-domain={process.env.TELEMETRY_ID}
            />
          )}
        </Head>
        <body className="h-full">
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default Document;
