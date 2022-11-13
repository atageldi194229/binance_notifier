const expressAsyncHandler = require("express-async-handler");
const { addToDB } = require("../../utils/db");

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
      datetime: date + " " + time,
      stoploss: Number(stoploss),
    });
  }

  return { symbol, interval, strategies };
};

exports.create = expressAsyncHandler(async (req, res) => {
  const { message } = req.params;
  addToDB(parseMessage(message));
  res.sendStatus(200);
});
