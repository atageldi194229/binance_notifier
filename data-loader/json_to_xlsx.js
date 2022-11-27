const excel = require("excel4node");
const fs = require("fs");
const path = require("path");

exports.jsonToXlsx = (json_file, xlsx_file) => {
  let data = JSON.parse(fs.readFileSync(json_file));

  // Create a new instance of a Workbook class
  var workbook = new excel.Workbook({
    dateFormat: "d/m/yy hh:mm:ss",
  });

  // Add Worksheets to the workbook
  var worksheet = workbook.addWorksheet("Sheet 1");

  const keys = Object.keys(data[0]);

  // col headers
  for (let i = 0; i < keys.length; i++) {
    worksheet.cell(1, i + 1).string(keys[i]);
  }

  // fill table
  for (let i = 0; i < data.length; i++) {
    for (let j = 0; j < keys.length; j++) {
      let value = data[i][keys[j]];
      worksheet.cell(i + 2, j + 1).string(value.toString());
      //   if (typeof value === "string") {
      //   } else {
      //    worksheet.cell(i + 2, j + 1).number(value);
      //   }
    }
  }

  workbook.write(xlsx_file);
};

exports.jsonFilesToOneExcelFile = (json_files, xlsx_file) => {
  let data = [];

  for (let file of json_files) {
    data = [...data, ...JSON.parse(fs.readFileSync(file))];
  }

  // Create a new instance of a Workbook class
  var workbook = new excel.Workbook({
    dateFormat: "d/m/yy hh:mm:ss",
  });

  // Add Worksheets to the workbook
  var worksheet = workbook.addWorksheet("Sheet 1");

  const keys = Object.keys(data[0]);

  // col headers
  for (let i = 0; i < keys.length; i++) {
    worksheet.cell(1, i + 1).string(keys[i]);
  }

  // fill table
  for (let i = 0; i < data.length; i++) {
    for (let j = 0; j < keys.length; j++) {
      worksheet.cell(i + 2, j + 1).string(data[i][keys[j]]);
    }
  }

  workbook.write(xlsx_file);
};

// let dir = path.join(__dirname, "backtest");
// let files = fs
//   .readdirSync(dir)
//   .filter((e) => e.endsWith(".json"))
//   .map((e) => path.join(dir, e));

// exports.jsonFilesToOneExcelFile(files, path.join(dir, "backtest_result.xlsx"));

exports.jsonFilesToOneJsonFile = (json_files, json_file) => {
  let data = [];

  for (let file of json_files) {
    data = [...data, ...JSON.parse(fs.readFileSync(file))];
  }

  fs.writeFileSync(json_file, JSON.stringify(data));
};

let dir = path.join(__dirname, "backtest");
let files = fs
  .readdirSync(dir)
  .filter((e) => e.endsWith(".json"))
  .map((e) => path.join(dir, e));

exports.jsonFilesToOneJsonFile(files, "~/backtest.json");
