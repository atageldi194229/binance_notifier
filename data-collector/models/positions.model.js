"use strict";

module.exports = (sequelize, DataTypes) => {
  let Position = sequelize.define(
    "Position",
    {
      trade_symbol: { type: DataTypes.STRING(40) },
      trade_interval: { type: DataTypes.STRING(3) },
      strategy: { type: DataTypes.STRING },
      takeprofit: { type: DataTypes.FLOAT },
      stoploss: { type: DataTypes.FLOAT },
      entry_price: { type: DataTypes.FLOAT },
      entry_time: { type: DataTypes.DATE },
      close_price: { type: DataTypes.FLOAT },
      close_time: { type: DataTypes.DATE },
      win: { type: DataTypes.INTEGER },
      win_percentage: { type: DataTypes.FLOAT },
    },
    {
      charset: "utf8",
      collate: "utf8_general_ci",
      timestamps: false,
    }
  );

  Position.associate = function (models) {
    // associations there
  };

  return Position;
};
