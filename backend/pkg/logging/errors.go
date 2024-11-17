package logging

// [ERRORS]

// [STRING ERRORS]
const (
	ErrNotSpecifiedCfg = "logging config is not specified"

	ErrInvalidLogLevel = "logging level is invalid, avalible: DEBUG, INFO, WARNING, ERROR"
	ErrInvalidLogFormat = "logging format is invalid, avalible: TXT, JSON, LOG"

	ErrOpenDir = "failed to open logs dir"
	ErrRemoveLastLogs = "failed to remove last logs"
	ErrCreateLogFile = "failed to create log file"
	ErrOpenLogFile = "failed to open log file"
	ErrCloseLogFile = "failed to close logging file"
)

// [STRINGF ERRORS]
const (
)