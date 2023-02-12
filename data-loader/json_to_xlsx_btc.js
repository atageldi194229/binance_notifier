const json2xls = require("json2xls");
const fs = require("fs");
const path = require("path");

exports.jsonToExcel = (json_file, xlsx_file) => {
  console.log("Converting started...");
  
  let data = JSON.parse(fs.readFileSync(json_file));

  const xls = json2xls(data);

  fs.writeFileSync(xlsx_file, xls, "binary");

  console.log("JSON successfully converted to excel.");
};

let dir = path.join(__dirname, "history");
let file = path.join(dir, "BTCUSDT_5m.json");
exports.jsonToExcel(file, process.argv[2]);
