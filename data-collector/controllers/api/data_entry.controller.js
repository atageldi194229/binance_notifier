const expressAsyncHandler = require("express-async-handler");
const fs = require("fs");
const path = require("path");

const parseMessage = (mess) => {
  const arr = mess.split("\n").map((e) => e.trim());

  const [symbol, interval] = arr[0].split("_").map((e) => e.trim());

  const strategies = [];

  for (let i = 1; i < arr.length; i++) {
    let [date, time, strategy, stoploss] = arr[i]
      .split(" ")
      .map((e) => e.trim());
    strategies.push({
      name: strategy,
      date,
      time,
      stoploss: Number(stoploss),
    });
  }

  return { symbol, interval, strategies };
};

exports.create = expressAsyncHandler(async (req, res) => {
  const { message } = req.params;

  res.sendStatus(200);
});
