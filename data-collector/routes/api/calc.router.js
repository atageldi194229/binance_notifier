"use strict";

const router = require("express").Router();

const controller = require("../../controllers/api/calc.controller");

router.get("/", controller.getData);

module.exports = router;
