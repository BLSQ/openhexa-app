module.exports = {
  i18n: {
    defaultNS: "messages",
    defaultLocale: "en",
    fallbackLng: "en",
    locales: ["en", "fr"],
    pluralSeparator: "___",
    // This option will reload your translations whenever serverSideTranslations is called
    reloadOnPrerender: true,

    // allow an empty value to count as invalid (by default is true)
    returnEmptyString: false,

    react: {
      // Which nodes are allowed to be kept in translations during defaultValue generation of <Trans>
      transKeepBasicHtmlNodesFor: ["b", "br", "strong", "i", "p"],
    },
  },
};
