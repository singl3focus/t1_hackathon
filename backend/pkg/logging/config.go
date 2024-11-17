package logging

import (
	"log/slog"
	"strings"
)

type LoggingConfig struct {
	Enable     bool
	Level      slog.Level
	Format     string
	SavingDays int
}

func NewLoggingConfig(enable bool, lvl string, format string, savedays int) *LoggingConfig {
	return &LoggingConfig{
		Enable:     enable,
		Level:      determineSlogLevel(lvl),
		Format:     validationLoggingFormat(format),
		SavingDays: savedays,
	}
}

func determineSlogLevel(level string) slog.Level {
	var levels = map[string]slog.Level{
		"DEBUG":   slog.LevelDebug,
		"INFO":    slog.LevelInfo,
		"WARNING": slog.LevelWarn,
		"ERROR":   slog.LevelError,
	}

	slogLevelUpper := strings.ToUpper(level)
	slogLevel, ok := levels[slogLevelUpper]
	if !ok {
		panic(ErrInvalidLogLevel)
	}

	return slogLevel
}

func validationLoggingFormat(format string) string {
	format = strings.ToUpper(format)
	if (format != "TXT") && (format != "JSON") && (format != "LOG") {
		panic(ErrInvalidLogFormat)
	}

	return format
}
