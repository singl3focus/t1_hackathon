package logging

import (
	"os"
	"io"
	"fmt"
	"time"
	"log/slog"
	"path/filepath"
)

func ErrAttr(err error) slog.Attr {
	return slog.Any(errorKey, err)
}

// GetDurationToNextDay returns the time remaining until the next day
func GetDurationToNextDay() time.Duration {
	currentTime := time.Now().Local()
	currentDay := time.Date(currentTime.Year(), currentTime.Month(), currentTime.Day(), 0, 0, 0, 0, time.Local)
	nextDay := currentDay.Add(24 * time.Hour)

	return nextDay.Sub(currentTime)
}

// DeleteLogDaily
func (bl *BaseLogger) DeleteLogDaily() {
	Notify(MsgAutoDeleteActivate)

	logger := NewModuleLogger(serviceModuleName, serviceModuleValue, bl)
	if bl.config.SavingDays < 1 {
		return
	}

	go func() {
		ticker := time.NewTicker(time.Hour * 23)

		for range ticker.C {
			DF, err := os.ReadDir(bl.logDirPath)
			if err != nil {
				logger.Critical(ErrOpenDir, ErrAttr(err))
			}

			if len(DF) > bl.config.SavingDays {
				filePath := filepath.Join(bl.logDirPath, DF[0].Name())

				err = os.Remove(filePath)
				if err != nil {
					logger.Error(ErrRemoveLastLogs, ErrAttr(err), slog.Any(path, filePath))
				}

				logger.Info(MsgDeleteLastLogs, slog.Any(path, filePath))
			}
		}
	}()
}

// OpenCurrentLog
func (bl *BaseLogger) OpenCurrentLog(ext string) *os.File {
	logger := NewModuleLogger(serviceModuleName, serviceModuleValue, bl)

	logFilePath := fmt.Sprintf("%s/%s.%s", bl.logDirPath, time.Now().Format("01022006"), ext)
	logFile, err := os.OpenFile(logFilePath, os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
	if os.IsNotExist(err) {
		logFile, err = os.Create(logFilePath)
		if err != nil {
			logger.Critical(ErrCreateLogFile, ErrAttr(err), slog.Any(path, logFilePath))
		}

	} else if err != nil {
		logger.Critical(ErrOpenLogFile, ErrAttr(err), slog.Any(path, logFilePath))
	}

	return logFile
}

func (bl *BaseLogger) InvokeLogging() {
	logger := NewModuleLogger(serviceModuleName, serviceModuleValue, bl)

	if !bl.config.Enable {
		logger := slog.New(slog.NewTextHandler(io.Discard, nil))
		slog.SetDefault(logger)

		return
	}

	t := time.NewTimer(GetDurationToNextDay())

	go func() {
		for {
			if _, err := os.Stat(bl.logDirPath); os.IsNotExist(err) {
				dirErr := os.Mkdir(bl.logDirPath, 0666)
				if dirErr != nil {
					logger.Critical(ErrOpenLogFile, ErrAttr(err), slog.Any(path, bl.logDirPath))
				}
			}

			// Validate format starting before and that's why we are guaranteed to receive txt or json
			var logFile *os.File
			switch bl.config.Format {
			case "JSON":
				logFile = bl.OpenCurrentLog(JSON)
				slog.SetDefault(slog.New(slog.NewJSONHandler(logFile, &slog.HandlerOptions{Level: bl.config.Level})))
			case "TXT":
				logFile = bl.OpenCurrentLog(TXT)
				slog.SetDefault(slog.New(slog.NewTextHandler(logFile, &slog.HandlerOptions{Level: bl.config.Level})))
			default:
				logFile = bl.OpenCurrentLog(LOG)
				slog.SetDefault(slog.New(slog.NewTextHandler(logFile, &slog.HandlerOptions{Level: bl.config.Level})))
			}

			<-t.C                           // Stopping and resetting current timer. Value returns at the moment when timer time has expired
			t.Reset(GetDurationToNextDay()) // Setup new timer duration

			if err := logFile.Close(); err != nil {
				logger.Critical(ErrCloseLogFile, ErrAttr(err), slog.Any(path, logFile.Name()))
			}
		}
	}()
	time.Sleep(3 * time.Second) // Wait while anonim gourutine starts

	bl.DeleteLogDaily()
}
