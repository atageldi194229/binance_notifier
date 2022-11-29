"use strict";
const router = require("express").Router();

router.use("/message", require("./data_entry.router"));
router.use("/calc", require("./calc.router"));

module.exports = router;
