require("dotenv").config();
const { USDMClient } = require("binance");
const { load_symbol_history } = require("./load_symbol_history");
const { TaskManager } = require("./task_manager");

const client = new USDMClient({
  api_key: process.env.API_KEY,
  api_secret: process.env.API_SECRET,
});

const getUsdtSymbols = async () => {
  const { symbols } = await client.getExchangeInfo();
  return symbols.map((e) => e.symbol).filter((e) => e.endsWith("USDT"));
};

const taskManager = new TaskManager(3, () => {
  console.log("Task manager is empty, all tasks are done");
  process.exit();
});

getUsdtSymbols()
  .then((symbols) => {
    console.log(symbols);
    for (let symbol of symbols) {
      taskManager.addTask(() => load_symbol_history(symbol, "5m"));
      taskManager.addTask(() => load_symbol_history(symbol, "15m"));
      taskManager.addTask(() => load_symbol_history(symbol, "1h"));
    }
  })
  .catch(console.error);
