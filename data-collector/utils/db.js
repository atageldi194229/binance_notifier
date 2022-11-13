const fs = require("fs");
const path = require("path");

const dbPath = path.join(__dirname, "../public");

const readFileData = (file, defaultValue) => {
  if (fs.existsSync(file)) {
    return JSON.parse(fs.readFileSync(file));
  }

  return defaultValue;
};

const saveFileData = (file, value) => {
  fs.writeFileSync(file, JSON.stringify(value));
};

exports.addToDB = ({ symbol, interval, strategies }) => {
  const file = path.join(dbPath, symbol + "_" + interval);

  let data = readFileData(file, []);

  let appendable = [];

  if (!data.length) {
    appendable = strategies;
  } else {
    let db_last = data[data.length - 1];
    let mess_last = strategies[strategies.length - 1];
    if (db_last.datetime !== mess_last.datetime) {
      appendable.push(mess_last);
    }
  }

  data = [...data, ...appendable];

  saveFileData(file, data);
};
