const { spawn } = require("child_process");
const path = require("path");

const pyprog = spawn("python3", [
  path.join(__dirname, "../tickers_2/rsi_calc_2.py"),
  path.join(__dirname, "db/ETHUSDT_5m.json"),
  "ETHUSDT",
  14,
  70,
  30,
  "U2197	RSI BIGGER THAN 70",
  "U2198 RSI LESS THAN 30",
]);

pyprog.stdout.on("data", (data) => console.log(data.toString()));
pyprog.stderr.on("data", (data) => console.log(data.toString()));
