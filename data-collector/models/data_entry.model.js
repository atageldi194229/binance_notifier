"use strict";

module.exports = (sequelize, DataTypes) => {
  let DataEntry = sequelize.define(
    "DataEntry",
    {
      symbol: { type: DataTypes.STRING(40) },
      interval: { type: DataTypes.STRING(3) },
      time: { type: DataTypes.STRING },
      strategy: { type: DataTypes.STRING },
      stoploss: { type: DataTypes.FLOAT },
      percentages: { type: DataTypes.JSON, defaultValue: [] },
    },
    {
      charset: "utf8",
      collate: "utf8_general_ci",
    }
  );

  DataEntry.associate = function (models) {
    // associations there
  };

  return DataEntry;
};
