import DeepL from "deepl-node";
import chalk from "chalk";
import fs from "fs";
import path from "path";

// Replace this with your DeepL API authentication key
if (!process.env.DEEPL_API_KEY) {
  console.error(
    "Please set the DEEPL_API_KEY environment variable to your DeepL API key.",
  );
  process.exit(1);
}
const translator = new DeepL.Translator(process.env.DEEPL_API_KEY);

async function translateText(text, sourceLanguage, targetLanguage) {
  const result = await translator.translateText(
    text,
    sourceLanguage,
    targetLanguage,
    { preserveFormatting: true, tagHandling: "html" },
  );
  if (Array.isArray(result)) {
    return result[0].text;
  } else {
    return result.text;
  }
}

function loadMessages(localesDirectory, language) {
  const contents = fs.readFileSync(
    path.join(localesDirectory, language, "messages.json"),
    "utf8",
  );
  return JSON.parse(contents);
}

async function translateFile(localesDirectory, targetLanguage, overwrite) {
  const notFounds = [];
  const errors = [];
  console.log(
    `Translating '${targetLanguage}' messages from '${localesDirectory}'`,
    overwrite ? chalk.bold(" with overwrite") : "",
  );
  try {
    const sourceMessages = loadMessages(localesDirectory, "en");
    const targetMessages = loadMessages(localesDirectory, targetLanguage);

    for (let key in targetMessages) {
      if (targetMessages[key] && !overwrite) {
        // Skip if the target message is already set and we don't want to overwrite
        continue;
      }
      if (!sourceMessages[key]) {
        // Skip if the source message is not found. Add it to the messages not found. This can happen if the target language has more complexity for plurality
        notFounds.push(key);
        continue;
      }
      try {
        const result = await translateText(
          sourceMessages[key],
          "en",
          targetLanguage,
        );
        console.log("Translating...");
        console.log("\t", key, "=>", chalk.bold.green(result));
        targetMessages[key] = result;
      } catch (err) {
        errors.push([key, err]);
      }
    }

    fs.writeFileSync(
      path.join(localesDirectory, targetLanguage, "messages.json"),
      JSON.stringify(targetMessages, null, 2),
    );
    if (notFounds.length > 0) {
      console.log(chalk.yellow("\nKeys not found:"));
      for (let key of notFounds) {
        console.log("- ", key);
      }
    }
    if (errors.length > 0) {
      console.log(chalk.red("\nErrors:"));
      for (let [key, err] of errors) {
        console.log("- ", key, "=>", err);
      }
    }
    console.log(
      chalk.green(`\nTranslation completed for '${targetLanguage}' and saved.`),
    );
  } catch (error) {
    console.error(chalk.red("Error in file processing:", error));
  }
}

const localesDirectory = process.argv[2]; // Path to the directory containing the JSON files
const targetLang = process.argv[3]; // Target language code (e.g., 'es')
const overwrite = process.argv.slice(2).includes("--overwrite");

translateFile(localesDirectory, targetLang, overwrite);
