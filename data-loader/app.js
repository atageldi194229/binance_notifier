const { spawn } = require("child_process");
const { USDMClient } = require("binance");
const { load_insufficient_data, make_file_path } = require("./db");
const path = require("path");

require("dotenv").config();

const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;
const PYTHON_COMMAND = process.env.PYTHON_COMMAND || "python3";

const client = new USDMClient({
  api_key: API_KEY,
  api_secret: API_SECRET,
});

// optionally override the logger
// const logger = {
//   ...DefaultLogger,
//   silly: (...params) => {},
// };

// const wsClient = new WebsocketClient(
//   {
//     api_key: API_KEY,
//     api_secret: API_SECRET,
//     beautify: true,
//     // Disable ping/pong ws heartbeat mechanism (not recommended)
//     // disableHeartbeat: true
//   },
//   logger
// );

// // receive raw events
// wsClient.on("message", (data) => {
//   save_message(data);
//   //   console.log("raw message received ", JSON.stringify(data, null, 2));
// });

// // notification when a connection is opened
// wsClient.on("open", (data) => {
//   // console.log("connection opened open:", data.wsKey, data.ws.target.url);
// });

// // receive formatted events with beautified keys. Any "known" floats stored in strings as parsed as floats.
// wsClient.on("formattedMessage", (data) => {
//   //   console.log("formattedMessage: ", data);
// });

// // read response to command sent via WS stream (e.g LIST_SUBSCRIPTIONS)
// wsClient.on("reply", (data) => {
//   // console.log("log reply: ", JSON.stringify(data, null, 2));
// });

// // receive notification when a ws connection is reconnecting automatically
// wsClient.on("reconnecting", (data) => {
//   // console.log("ws automatically reconnecting.... ", data?.wsKey);
// });

// // receive notification that a reconnection completed successfully (e.g use REST to check for missing data)
// wsClient.on("reconnected", (data) => {
//   // console.log("ws has reconnected ", data?.wsKey);
// });

// // Recommended: receive error events (e.g. first reconnection failed)
// wsClient.on("error", (data) => {
//   // console.log("ws saw error ", data?.wsKey);
// });

const getUsdtSymbols = async () => {
  const { symbols } = await client.getExchangeInfo();
  return symbols.map((e) => e.symbol).filter((e) => e.endsWith("USDT"));
};

const runRsiStrategy = (symbol) => {
  const interval = "5m";

  const pyprog = spawn(PYTHON_COMMAND, [
    path.join(__dirname, "../tickers_2/rsi_calc_2.py"),
    make_file_path(symbol, interval),
    symbol,
    14,
    70,
    30,
    `\U2197 ${symbol} ${interval} RSI BIGGER THAN 70`,
    `\U2198 ${symbol} ${interval} RSI LESS   THAN 30`,
  ]);

  pyprog.stdout.on("data", (data) => console.log(data.toString()));
  pyprog.stderr.on("data", (data) => console.log(data.toString()));
};

const runTrendMacdBullStrategy = (symbol, interval_in_minutes) => {
  // trend_macd_bull.py

  const interval = interval_in_minutes + "m";

  const pyprog = spawn(PYTHON_COMMAND, [
    path.join(__dirname, "../tickers_2/trend_macd_bull.py"),
    make_file_path(symbol, interval),
    symbol,
    interval,
  ]);

  pyprog.stdout.on("data", (data) => console.log(data.toString()));
  pyprog.stderr.on("data", (data) => console.log(data.toString()));
};

// const runStrategies = (symbol) => {
//   runRsiStrategy(symbol);
// };

let running = 0;
let max_run = 10;
let runs = [];

const check_runs = () => {
  if (running >= max_run) return;

  if (runs.length) {
    runs.shift()();
    running++;

    // console.log(running, max_run, runs.length);
  }
};

const add_run = (f) => {
  const ff = async () => {
    try {
      await f();
    } catch (err) {
      console.log(err);
    }

    running--;
    check_runs();
  };

  runs.push(ff);
  check_runs();
};

const loadData = (symbols, interval_in_minutes) => {
  for (let symbol of symbols) {
    add_run(() =>
      load_insufficient_data(symbol, interval_in_minutes)
        .then(() => {
          if (interval_in_minutes === 5) {
            // runRsiStrategy(symbol);
            runTrendMacdBullStrategy(symbol, interval_in_minutes);
          } else if (interval_in_minutes === 15) {
            // runRsiStrategy(symbol);
          }
        })
        .catch(console.error)
    );
  }
};

const sleep = (ms) => new Promise((f) => setTimeout(f, ms));

const startProcess = async (symbols, interval_in_minutes = 5) => {
  while (true) {
    loadData(symbols, interval_in_minutes);
    const now = new Date();
    const m = now.getMinutes() % interval_in_minutes;
    const s = now.getSeconds();

    // timeout in seconds
    let timeout = interval_in_minutes * 60 - (m * 60 + s) + 3;
    // console.log(timeout);
    await sleep(timeout * 1000);
  }
};

(async () => {
  const symbols = await getUsdtSymbols();

  startProcess(symbols, 5);
  startProcess(symbols, 15);
})();

// client.getExchangeInfo().then((data) => {
//   const symbols = data.symbols
//     .map((e) => e.symbol)
//     .filter((e) => e.endsWith("USDT"));

//   for (let symbol of symbols) {
//     load_insufficient_data(symbol)
//       .then(() => {
//         wsClient.subscribeKlines(symbol, "5m", "usdm");
//       })
//       .catch(console.error);
//   }
//   //   wsClient.subscribeKlines("BCHUSDT", "1m", "usdm");
//   //   wsClient.subscribeKlines("KLAYUSDT", "1m", "usdm");
// });

// Call methods to subcribe to as many websockets as you want.
// Each method spawns a new connection, unless a websocket already exists for that particular request topic.
// wsClient.subscribeSpotAggregateTrades(market);
// wsClient.subscribeSpotTrades(market);
// wsClient.subscribeSpotKline("ETHUSDT", "1m");
// wsClient.subscribeSpotSymbolMini24hrTicker(market);
// wsClient.subscribeSpotAllMini24hrTickers();
// wsClient.subscribeSpotSymbol24hrTicker(market);
// wsClient.subscribeSpotAll24hrTickers();
// wsClient.subscribeSpotSymbolBookTicker(market);
// wsClient.subscribeSpotAllBookTickers();
// wsClient.subscribeSpotPartialBookDepth(market, 5);
// wsClient.subscribeSpotDiffBookDepth(market);

// wsClient.subscribeSpotUserDataStream();
// wsClient.subscribeMarginUserDataStream();
// wsClient.subscribeIsolatedMarginUserDataStream("BTCUSDT");

// wsClient.subscribeUsdFuturesUserDataStream();

// each method also restores the WebSocket object, which can be interacted with for more control
// const ws1 = wsClient.subscribeSpotSymbolBookTicker(market);
// const ws2 = wsClient.subscribeSpotAllBookTickers();
// const ws3 = wsClient.subscribeSpotUserDataStream(listenKey);

// optionally directly open a connection to a URL. Not recommended for production use.
// const ws4 = wsClient.connectToWsUrl(`wss://stream.binance.com:9443/ws/${listenKey}`, 'customDirectWsConnection1');
