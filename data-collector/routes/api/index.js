"use strict";
const router = require("express").Router();

router.use("/message", require("./data_entry.router"));

module.exports = router;
