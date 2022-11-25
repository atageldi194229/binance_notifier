const fs = require("fs");
const path = require("path");

const { USDMClient } = require("binance");
require("dotenv").config();

const client = new USDMClient({
  api_key: process.env.API_KEY,
  api_secret: process.env.API_SECRET,
});

const db_dir = path.join(__dirname, "history");

const readFileData = (file, defaultValue) => {
  if (!fs.existsSync(file)) return defaultValue;
  return JSON.parse(fs.readFileSync(file).toString());
};

const writeFileData = (file, value) => {
  fs.writeFileSync(file, JSON.stringify(value));
  return;
};

const build_file_name = (symbol, interval) => symbol + "_" + interval + ".json";

const make_file_path = (symbol, interval) =>
  path.join(db_dir, build_file_name(symbol, interval));

exports.load_symbol_history = async (
  symbol,
  interval,
  interval_in_minutes = 5
) => {
  // get old time
  console.log(symbol, interval, "history load started");

  const limit = 1000;
  const file = make_file_path(symbol, interval);

  let data = readFileData(file, []);
  let time = data.length ? data[0][0] : new Date().getTime();
  data = [];

  while (true) {
    try {
      let list = await client.getKlines({
        symbol,
        interval,
        endTime: time,
        limit,
      });

      if (!list.length) break;

      time = list[0][0] - 1;

      data = [...list, ...data];

      if (data.length > 8000) {
        writeFileData(file, [...data, ...readFileData(file, [])]);
        data = [];
      }
    } catch (err) {
      console.log(err);
    }
  }

  if (data.length) {
    writeFileData(file, [...data, ...readFileData(file, [])]);
    data = [];
  }

  console.log(symbol, interval, "history load completed");
  return;
};

// exports
//   .load_symbol_history("BTCUSDT", "5m")
//   .then(() => process.exit())
//   .catch(console.error);
