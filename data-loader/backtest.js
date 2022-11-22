const fs = require("fs");
const path = require("path");
const { USDMClient } = require("binance");
require("dotenv").config();

const client = new USDMClient({
  api_key: process.env.API_KEY,
  api_secret: process.env.API_SECRET,
});

/*
{
    'BTCUSDT_5m': { 
        time_interval: {
            min: 123,
            max: 123,
        }
    }
}
*/
const input_file = process.argv[2];
const input_data = JSON.parse(fs.readFileSync(input_file));
const metadata = {};

// // init metadata
// for (let mess of input_data) {
//   const {
//     symbol,
//     interval,
//     str: { unixtime },
//   } = mess;

//   if (!metadata[symbol + "_" + interval]) {
//     metadata[symbol + "_" + interval] = {
//       time_interval: {
//         min: unixtime,
//         max: unixtime,
//       },
//     };
//   } else {
//     metadata[symbol + "_" + interval] = {
//       time_interval: {
//         min: Math.min(
//           metadata[symbol + "_" + interval].time_interval.min,
//           unixtime
//         ),
//         max: Math.max(
//           metadata[symbol + "_" + interval].time_interval.max,
//           unixtime
//         ),
//       },
//     };
//   }
// }

// const stoploss = 0.5;
const takeprofit = 1.95;

let wins = 0;
let win_p = 0;
let losses = 0;
let loss_p = 0;

(async () => {
  for (let mess of input_data) {
    const {
      symbol,
      interval,
      str: { name, unixtime, stoploss },
    } = mess;

    if (name !== "bearish_divergence_1-3" && stoploss > 2) {
      continue;
    }

    const startTime = unixtime;
    const endTime = unixtime + 12 * 60 * 60 * 1000;

    console.log(symbol, interval, new Date(startTime));

    await client
      .getKlines({
        symbol,
        interval,
        startTime: startTime,
        endTime: endTime,
        // limit: 10,
      })
      .then((list) => {
        list = list.filter((e) => e[0] >= unixtime);

        if (list[0][0] !== unixtime) {
          console.log("WTF");
          process.exit();
        }

        const start_value = list[0][4];

        for (let i = 1; i < list.length; i++) {
          let row = list[i].map((e) => Number(e));
          let min = 100 - (row[3] / start_value) * 100;
          let max = 100 - (start_value / row[2]) * 100;

          if (min > takeprofit) {
            wins++;
            win_p += takeprofit;
            return;
          }

          if (max > stoploss) {
            losses++;
            loss_p += stoploss;
            return;
          }
        }
      })
      .catch(console.error)
      .finally(() => {
        console.log("win: %d, loss: %d", wins, losses);
        console.log("win: %d%, loss: %d%", win_p, loss_p);
      });
  }
})();
