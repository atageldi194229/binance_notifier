const { USDMClient } = require("binance");
const { load_symbol_history } = require("./load_symbol_history");
require("dotenv").config();

const client = new USDMClient({
  api_key: process.env.API_KEY,
  api_secret: process.env.API_SECRET,
});

const getUsdtSymbols = async () => {
  const { symbols } = await client.getExchangeInfo();
  return symbols.map((e) => e.symbol).filter((e) => e.endsWith("USDT"));
};

class TaskManager {
  constructor(max_task_count = 2, onDone) {
    this.max_task_count = max_task_count;
    this.running_count = 0;
    this.tasks = [];
    this.onDone = onDone;
  }

  check() {
    if (this.running_count >= this.max_task_count) return;

    if (this.tasks.length) {
      this.tasks.shift()();
      this.running_count++;
    }

    if (this.running_count === 0 && this.onDone) this.onDone();
  }

  addTask(f) {
    const task = async () => {
      await f().catch(console.error);
      this.running_count--;
      this.check();
    };

    this.tasks.push(task);
    this.check();
  }
}

const taskManager = new TaskManager(2, () => {
  console.log("Task manager is empty, all tasks are done");
  process.exit();
});

getUsdtSymbols().then((symbols) => {
  console.log(symbols);
  for (let symbol of symbols) {
    taskManager.addTask(() => load_symbol_history(symbol, "5m"));
    taskManager.addTask(() => load_symbol_history(symbol, "15m"));
  }
});
