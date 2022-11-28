const json2xls = require("json2xls");
const fs = require("fs");
const path = require("path");

exports.jsonFilesToOneExcelFile = (json_files, xlsx_file) => {
  let data = [];

  for (let file of json_files) {
    data = [...data, ...JSON.parse(fs.readFileSync(file))];
  }

  data = data.map((e) => ({
    ...e,
    entry_time: new Date(e.entry_time),
    close_time: new Date(e.close_time),
  }));

  const xls = json2xls(data);

  fs.writeFileSync(xlsx_file, xls, "binary");

  console.log("WORK DONE MY FRIEND");
};

let dir = path.join(__dirname, "backtest");
let files = fs
  .readdirSync(dir)
  .filter((e) => e.endsWith(".json"))
  .map((e) => path.join(dir, e));

exports.jsonFilesToOneExcelFile(files, path.join(dir, "backtest_result.xlsx"));
