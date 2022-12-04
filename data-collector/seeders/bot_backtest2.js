const {
  Position,
  Sequelize,
  Sequelize: { Op },
} = require("../models");

const fs = require("fs");

class TradeBot {
  constructor(cash = 10000, max_position_count = 10) {
    this.cash = cash;
    this.max_position_count = max_position_count;
    this.all = [];
    this.positions = [];
    this.percentage = 0;
    this.today_percentage = [0, new Date(2000, 0).getTime()];
  }

  addPosition(position) {
    // if (position.entry_time.getTime() <= this.today_percentage[1]) return;

    let available_position_count = this.max_position_count - this.positions;
    if (available_position_count > 0) {
      let amount = this.cash / available_position_count;
      this.positions.push([amount, position]);
    } else {
      let min_close_time = Math.min(
        ...this.positions.map(([, e]) => e.close_time.getTime())
      );

      if (position.close_time.getTime() < min_close_time) return;

      let found = this.positions.find(
        ([, e]) => e.close_time.getTime() === min_close_time
      );

      this.positions = this.positions.filter((e) => e !== found);
      this.all.push(found);

      //   this.cach +=
      //     found[0] * this.max_position_count * found[1].win_percentage + found[0];
      this.percentage += found[1].win_percentage;
      this.today_percentage[0] += found[1].win_percentage;

      if (this.today_percentage[0] >= -5) {
        let d = new Date(position.entry_time.getTime());
        d.setDate(d.getDate() + 1);
        d.setHours(5);
        d.setMinutes(0);
        d.setSeconds(0);

        this.today_percentage[1] = d.getTime();
      }

      // if (position.entry_time.getTime() <= this.today_percentage[1]) return;

      available_position_count = this.max_position_count - this.positions;
      let amount = this.cash / available_position_count;
      this.positions.push([amount, position]);
    }
  }

  closeAll() {
    for (let [amount, position] of this.positions) {
      //   this.cach +=
      //     amount * this.max_position_count * position.win_percentage + amount;
      this.all.push(position);
      this.percentage += position.win_percentage;
    }

    this.positions = [];
  }
}

(async () => {
  let bot = new TradeBot();

  const positions = await Position.findAll({
    // where: {},
  });

  console.log("Positions: ", positions.length);

  for (let p of positions) {
    bot.addPosition(p);
  }

  bot.closeAll();

  console.log("Percentage: ", bot.percentage);
  console.log("Opened pos: ", bot.all.count);
  process.exit();
})();
