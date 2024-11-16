package logging

const (
	JSON = "json"
	TXT = "txt"
	LOG = "log"
)

// [LOG FUNCTIONS]
const (
	serviceModuleName  = "SERVICE"
	serviceModuleValue = "BASE"
)

// [LOG KEYWORDS]
const (
	path     = "(path)"
	errorKey = "(error)"
)

// [LOG MESSAGES]
const (
	MsgMainKeyword = "SERVER"

	MsgDeleteLastLogs = "Deleted last log file has been successful"

	MsgStateStart         = "START"
	MsgStateEnd           = "END"
	MsgAutoDeleteActivate = "AUTO DELETE ACTIVATE"
)
