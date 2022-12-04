const fs = require("fs");
const path = require("path");

const backtest_dir = path.join(__dirname, "../backtest");
const position_dir = path.join(__dirname, "positions");

let files = fs.readdirSync(backtest_dir).filter((e) => e.endsWith(".json"));
