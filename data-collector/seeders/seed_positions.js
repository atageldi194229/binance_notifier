const { Position } = require("../models");
const fs = require("fs");
const path = require("path");

let backtest_dir = process.argv[2];

(async () => {
  console.log(process.argv);
  console.log(backtest_dir);

  let files = fs.readdirSync(backtest_dir).filter((e) => e.endsWith(".json"));

  console.log(files);

  for (let i = 0; i < files.length; i++) {
    let file = files[i];
    let data = JSON.parse(fs.readFileSync(path.join(backtest_dir, file)));

    try {
      await Position.bulkCreate(data);
    } catch (err) {
      for (let row of data) {
        await Position.create(row).catch(console.error);
      }
    }
  }

  // end process
  console.log("Setup done.");
  process.exit();
})();
