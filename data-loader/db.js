const fs = require("fs");
const path = require("path");
const { USDMClient } = require("binance");
require("dotenv").config();

const client = new USDMClient({
  api_key: process.env.API_KEY,
  api_secret: process.env.API_SECRET,
});

const make_file_path = (symbol, interval) => {
  const dir = path.join(__dirname, "db");
  const file_name = symbol + "_" + interval + ".json";
  return path.join(dir, file_name);
};

exports.make_file_path = make_file_path;

const convert_to_mess_list = (e) => {
  // (Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore)
  return [
    e.k.t,
    e.k.o,
    e.k.h,
    e.k.l,
    e.k.c,
    e.k.v,
    e.k.T,
    e.k.q,
    e.k.n,
    e.k.V,
    e.k.Q,
    e.k.B,
  ];
};

const combine_kline_datas = (a_list, list, interval_in_minutes = 5) => {
  let data = [...a_list];

  const time_set = new Set(data.map((e) => e[0]));

  for (let el of list) {
    if (!time_set.has(el[0])) {
      if (!data.length) {
        data.push(el);
      }

      const last = data[data.length - 1];
      const _ms = el[0] - last[0];

      if (_ms === interval_in_minutes * 60 * 1000) {
        data.push(el);
      }
    }
  }

  return data;
};

exports.load_insufficient_data = (symbol, interval_in_minutes = 5) => {
  const max_elements = 300;
  const interval = interval_in_minutes + "m";
  const file_path = make_file_path(symbol, interval);

  let data = [];

  if (fs.existsSync(file_path)) {
    data = require(file_path);
  }

  let minutes = max_elements * interval; // in minutes

  if (data.length) {
    const last = data[data.length - 1];

    const ms = new Date().getTime() - last[0];

    minutes = parseInt(ms / 1000 / 60) + 2;
  }

  let tt = new Date();
  tt.setMinutes(tt.getMinutes() - minutes);

  return client
    .getKlines({
      symbol,
      interval,
      startTime: tt.getTime(),
      endTime: new Date().getTime(),
    })
    .then((list) => {
      console.log(
        "DOWNLOADED: ",
        symbol,
        list.length,
        (new Date().getTime() - tt.getTime()) / 1000 / 60
      );

      let new_data = combine_kline_datas(data, list, interval_in_minutes).slice(
        -max_elements
      );
      // .slice(0, -1);

      const last_open_time = new Date(new_data[new_data.length - 1][0]);
      const now = new Date();
      const diff = now.getTime() - last_open_time.getTime();

      if (diff < interval_in_minutes * 60 * 1000) {
        new_data = new_data.slice(0, -1);
      }

      fs.writeFileSync(file_path, JSON.stringify(new_data));

      return data[data.length - 1][0] !== new_data[new_data.length - 1][0];
    })
    .catch(console.error);
};
