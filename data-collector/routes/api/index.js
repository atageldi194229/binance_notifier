"use strict";
const router = require("express").Router();

router.use("/data-entries", require("./data_entry.router"));

module.exports = router;
