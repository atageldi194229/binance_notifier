"use strict";

const router = require("express").Router();

const controller = require("../../controllers/api/data_entry.controller");

router.get("/:message", controller.create);

module.exports = router;
