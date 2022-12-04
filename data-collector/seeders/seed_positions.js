const { Position } = require("../models");
const fs = require("fs");
const path = require("path");

let backtest_dir = process.argv[2];

(async () => {
  let files = fs.readdirSync(backtest_dir).filter((e) => e.endsWith(".json"));

  for (let file of files) {
    let data = JSON.parse(fs.readFileSync(path.join(backtest_dir, file)));

    await Position.bulkCreate(data);
  }

  // end process
  console.log("Setup done.");
  process.exit();
})();