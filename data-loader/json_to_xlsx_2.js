const json2xls = require("json2xls");
const fs = require("fs");
const path = require("path");

exports.jsonFilesToOneExcelFile = (json_files, xlsx_file) => {
  let data = [];

  console.log("started processing");

  for (let file of json_files) {
    console.log(file);
    data = [...data, ...JSON.parse(fs.readFileSync(file))];
  }

  const xls = json2xls(data);

  fs.writeFileSync(xlsx_file, xls, "binary");

  console.log("WORK DONE MY FRIEND");
};

exports.jsonFilesToExcelFiles = (json_files, dir) => {
  console.log("started processing");

  for (let file of json_files) {
    console.log(file);
    let data = JSON.parse(fs.readFileSync(file));

    const xls = json2xls(data);

    let xlsx_file =
      file.split("/").pop().split(".").slice(0, -1).join(".") + ".xlsx";
    console.log(dir, xlsx_file);
    fs.writeFileSync(path.join(dir, xlsx_file), xls, "binary");

    console.log("Created: ", xlsx_file);
  }

  console.log("WORK DONE MY FRIEND");
};

let dir = path.join(__dirname, "backtest");
let files = fs
  .readdirSync(dir)
  .filter((e) => e.endsWith(".json"))
  .map((e) => path.join(dir, e));

console.log(process.argv);
exports.jsonFilesToExcelFiles(files, process.argv[2]);
