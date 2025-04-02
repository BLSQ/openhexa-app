import fs from "fs";
import path from "path";
import chalk from "chalk";
import pkg from "../next-i18next.config.js";

const { i18n } = pkg;

const missingValues = [];

console.log("Validating translations...");
i18n.locales.forEach((lang) => {
  let isOk = true;
  const filePath = path.join("public/locales", lang, "messages.json");

  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, "utf-8");
    const messages = JSON.parse(content);

    Object.keys(messages).forEach((key) => {
      if (!messages[key]) {
        isOk = false;
        missingValues.push(
          `Value missing for key '${chalk.bold(key)}' in ${chalk.bold(lang)}`,
        );
      }
    });

    console.log(
      `- ${lang} ${isOk ? chalk.bold.green("✓") : chalk.bold.red("✗")}`,
    );
  } else {
    console.error(`File '${filePath}' does not exist`);
    process.exit(1);
  }
});

if (missingValues.length > 0) {
  console.error(chalk.bold("Missing values found:"));
  console.error(missingValues.join("\n"));
  process.exit(1);
}
