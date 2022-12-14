const {
  Position,
  Sequelize,
  Sequelize: { Op },
} = require("../models");

const fs = require("fs");

class TradeBot {
  constructor(cash = 100, max_position_count = 10) {
    this.cash = cash;
    this.max_position_count = max_position_count;
    this.all = [];
    this.positions = [];
    this.percentage = 0;
    this.today_percentage = 0;
    this.last_day = 0;
    this.block_trading_until = new Date(1990, 0);
  }

  openPosition(position) {
    let empty = this.max_position_count - this.positions.length;

    if (empty > 0) {
      position.amount = 10;
      // position.amount = this.cash / empty;
      this.cash -= position.amount;
      this.positions.push(position);
      return true;
    }

    return false;
  }

  closePosition(position) {
    this.positions.splice(this.positions.indexOf(position), 1);
    this.all.push(position);

    this.cash += position.amount * (position.win_percentage / 10 + 1);
    console.log(
      this.cash,
      this.positions.length,
      this.positions
        .map((e) => e.amount * (e.win_percentage / 10 + 1))
        .reduce((p, c) => p + c, 0) + this.cash
    );
    this.percentage += position.win_percentage;
    this.today_percentage += position.win_percentage;
  }

  getPositionWithMinCloseTime() {
    let minTime = new Date(2222, 0).getTime();
    let minIndex = -1;

    for (let i = 0; i < this.positions.length; i++) {
      let time = this.positions[i].close_time;

      if (time < minTime) {
        minTime = time;
        minIndex = i;
      }
    }

    if (minIndex === -1) return null;
    return this.positions[minIndex];
  }

  addPosition(position) {
    let position_entry_time = new Date(position.entry_time);

    if (this.last_day !== position_entry_time.getDate()) {
      this.last_day = position_entry_time.getDate();
      this.today_percentage = 0;
    }

    if (position.entry_time <= this.block_trading_until.getTime()) {
      return;
    }

    if (!this.openPosition(position)) {
      let c_position = this.getPositionWithMinCloseTime();

      if (
        position_entry_time.getTime() <
        new Date(c_position.close_time).getTime()
      ) {
        return;
      }

      this.closePosition(c_position);

      if (this.today_percentage <= -5) {
        let d = new Date(position.entry_time);
        d.setDate(d.getDate() + 1);
        d.setHours(0);
        d.setMinutes(0);
        d.setSeconds(0);

        this.closeAllPositions();
        this.today_percentage = 0;
        this.block_trading_until = d;
      }

      if (position.entry_time <= this.block_trading_until.getTime()) {
        return;
      }

      this.openPosition(position);
    }
  }

  closeAllPositions() {
    for (let position of this.positions) {
      this.closePosition(position);
    }

    console.log("close_all, ", this.positions.length);
  }
}

Position.findAll({
  order: [
    ["id", "asc"],
    ["entry_time", "asc"],
  ],
  where: {
    [Op.and]: [
      {
        entry_time: {
          [Op.between]: [
            new Date(2021, 3).getTime(),
            new Date(2021, 4).getTime(),
          ],
        },
      },
      {
        strategy: "bearish_divergence",
        // strategy: "bearish_divergence_1-3",
        // strategy: ["bearish_divergence", "bullish_divergence"],
        //   strategy: "bullish_divergence",/
        trade_interval: "15m",
        stoploss: {
          [Op.between]: [1, 10],
        },
      },
    ],
  },
}).then((positions) => {
  console.log("Positions: ", positions.length);

  let bot = new TradeBot();

  for (let p of positions) {
    bot.addPosition(p.toJSON());
  }

  bot.closeAllPositions();
  bot.closeAllPositions();
  bot.closeAllPositions();
  bot.closeAllPositions();
  bot.closeAllPositions();
  bot.closeAllPositions();

  let rows = JSON.parse(JSON.stringify(bot.all));

  fs.writeFileSync(process.argv[2], JSON.stringify(rows));

  console.log("Percentage: ", bot.percentage);
  console.log("Cash: ", bot.cash);
  console.log("Opened pos: ", rows.length);
  process.exit();
});
