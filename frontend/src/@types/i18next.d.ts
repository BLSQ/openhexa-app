// import the original type declarations
import "i18next";

declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: "messages";
    returnNull: false;
  }
}
