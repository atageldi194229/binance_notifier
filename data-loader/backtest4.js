require("dotenv").config();
const { TaskManager } = require("./task_manager");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const PYTHON_COMMAND = process.env.PYTHON_COMMAND || "python3";

const run_backtest = (file, symbol, interval) => {
  return new Promise((resolve, reject) => {
    const pyprog = spawn(PYTHON_COMMAND, [
      path.join(__dirname, "../tickers_2/backtest5.py"),
      file,
      symbol,
      interval,
      path.join(__dirname, "backtest"),
    ]);

    pyprog.stdout.on("data", (data) => console.log(data.toString()));
    pyprog.stderr.on("data", (data) => console.log(data.toString()));
    pyprog.on("close", (code) => {
      console.log(`child process exited with code ${code}`);
      resolve();
    });
  });
};

const taskManager = new TaskManager(2, () => {
  console.log("Task manager is empty, all tasks are done");
  process.exit();
});

const files = fs
  .readdirSync(path.join(__dirname, "history"))
  .filter((e) => e.endsWith(".json"));

// const files = [""];

for (let file of files) {
  let [symbol, interval] = file.slice(0, -5).split("_");
  file = path.join(__dirname, "history", file);
  console.log(file);
  taskManager.addTask(() => run_backtest(file, symbol, interval));
}
