const { ValidationError } = require("sequelize");
const { ServerError, DatabaseError } = require("../errors/server_errors");

/**
 * Express Error Handler
 * @function errorHandler
 * @param {Error} err - error for response
 * @param {RequestHandler} req
 * @param {ResponseHandler} res
 * @param {any} next
 */
exports.errorHandler = (err, req, res, next) => {
  let error = err;

  if (process.env.NODE_ENV === "development") {
    console.log(error);
  }

  // Sequelize Error
  if (err.name === "SequelizeDatabaseError") {
    error = new DatabaseError(error.message);
    // if (err.original.code === "ER_NO_SUCH_TABLE")
    //   error = new ServerError("Error no such table in db");
    // else error = new ServerError("DB Error");
  }

  if (
    err instanceof ValidationError ||
    err.name === "SequelizeUniqueConstraintError"
  ) {
    if (err.errors.length) {
      error = new ServerError(err.errors[0].message, "Validation error");
    }
  }

  if (!(error instanceof ServerError)) {
    error = new ServerError(error.message, error.name);
  }

  res.status(500).json({
    error: error,
  });
};
