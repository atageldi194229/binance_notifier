class ServerError extends Error {
  constructor(message, originalName) {
    super(message);
    this.name = this.constructor.name;
    this.mess = message;
    this.originalName = originalName;
  }
}

class DatabaseError extends ServerError {
  constructor(message) {
    super(message);
  }
}

class DatabaseValidationError extends ServerError {
  constructor(message) {
    super(message);
  }
}

class IncorrectPasswordError extends ServerError {
  constructor() {
    super("incorrect password bro");
  }
}

class UnimplementedError extends ServerError {
  constructor() {
    super("Unimplemented error");
  }
}

class UserNotFound extends ServerError {
  constructor() {
    super("User not found");
  }
}

class UserExists extends ServerError {
  constructor() {
    super("User already exists");
  }
}

class TokenNotFound extends ServerError {
  constructor() {
    super("Token not found, please check logged devices for security purposes");
  }
}

class UserNotVerified extends ServerError {
  constructor() {
    super("User not verified");
  }
}

class EmailNotConfirmed extends ServerError {
  constructor() {
    super("Email not confirmed");
  }
}

class UserBlockedError extends ServerError {
  constructor() {
    super("User is blocked");
  }
}

class UserDeletedError extends ServerError {
  constructor() {
    super("User is deleted");
  }
}

class Unauthorized extends ServerError {
  constructor() {
    super("User not authorized");
  }
}

class TokenExpired extends ServerError {
  constructor() {
    super(
      "The JWT token is expired, please check logged devices for security purposes"
    );
  }
}

class TokenDecodeError extends ServerError {
  constructor() {
    super("Could not decode token");
  }
}

class PermissionDenied extends ServerError {
  constructor() {
    super("Permission denied");
  }
}

class ConfirmationTimeExpired extends ServerError {
  constructor() {
    super("Sorry, but your confirmation time is expired");
  }
}

class NotFoundError extends ServerError {
  constructor() {
    super("Not found");
  }
}

exports.ServerError = ServerError;
exports.DatabaseError = DatabaseError;
exports.IncorrectPasswordError = IncorrectPasswordError;
exports.UnimplementedError = UnimplementedError;
exports.UserNotFound = UserNotFound;
exports.UserExists = UserExists;
exports.TokenNotFound = TokenNotFound;
exports.UserNotVerified = UserNotVerified;
exports.EmailNotConfirmed = EmailNotConfirmed;
exports.UserBlockedError = UserBlockedError;
exports.UserDeletedError = UserDeletedError;
exports.Unauthorized = Unauthorized;
exports.TokenExpired = TokenExpired;
exports.TokenDecodeError = TokenDecodeError;
exports.PermissionDenied = PermissionDenied;
exports.ConfirmationTimeExpired = ConfirmationTimeExpired;
exports.NotFoundError = NotFoundError;
