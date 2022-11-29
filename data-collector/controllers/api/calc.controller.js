const expressAsyncHandler = require("express-async-handler");

const fs = require("fs");
const path = require("path");

exports.getData = expressAsyncHandler(async (req, res) => {
  let dir = path.join(__dirname, "../../../data-loader/backtest");
  let files = fs
    .readdirSync(dir)
    .filter((e) => e.endsWith(".json"))
    .map((e) => path.join(dir, e));

  const result = {};

  for (let file of files) {
    console.log(file);
    let data = JSON.parse(fs.readFileSync(file));

    if (!data.length) continue;

    const key = data[0].trade_symbol + data[0].trade_interval;

    result[key] = {
      profit: 0,
      win_count: 0,
      loss_count: 0,
      win_percentage: 0,
      loss_percentage: 0,
    };

    for (let e of data) {
      if (e.win) {
        result[key].win_count++;
        result[key].win_percentage += e.win_percentage;
      } else {
        result[key].loss_count++;
        result[key].loss_percentage += e.win_percentage;
      }
    }
  }

  res.status(200).json(result);
});

/*
{
  trade_symbol: "BTCUSDT",
  trade_interval: "5m",
  strategy: "bullish_divergence",
  takeprofit: 4,
  stoploss: 0.56,
  entry_price: 10263.95,
  entry_time: 1568108699999,
  close_price: 10176.69,
  close_time: 1568125499999,
  win: 0,
  win_percentage: -0.56,
};

*/
