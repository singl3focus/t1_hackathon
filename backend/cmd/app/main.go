package main

import (
	"log"
	"time"

	c "github.com/singl3focus/t1_hackathon/backend/config"
	h "github.com/singl3focus/t1_hackathon/backend/internal/adapter/http"
	r "github.com/singl3focus/t1_hackathon/backend/internal/adapter/repo/postgres"
	s "github.com/singl3focus/t1_hackathon/backend/internal/service"
	"github.com/singl3focus/t1_hackathon/backend/pkg/logging"
)

func main() {
	// Init config and logger
	cfg := c.GetConfig()

	loggingCfg := logging.NewLoggingConfig(
		cfg.Logger.Enable, cfg.Logger.Level, cfg.Logger.Format, cfg.Logger.SavingDays)
	baseLogger := logging.NewBaseLogger(cfg.Logger.LogsDirPath, "BASE:LOGGER", loggingCfg)

	baseLogger.InvokeLogging()
	baseLogger.DeleteLogDaily()

	time.Sleep(1)

	// App
	repoLogger := logging.NewModuleLogger("REPO", "POSTGRES", baseLogger)
	handlerLogger := logging.NewModuleLogger("HANDLER", "ROUTER", baseLogger)

	repo, err := r.NewPostgresDB(
			cfg.Database.Host, 
			cfg.Database.Port,
			cfg.Database.Username,
			cfg.Database.Password,
			cfg.Database.DBName,
			cfg.Database.SSLMode,
			repoLogger,
		)
	if err != nil {
		log.Fatal(err)
	}

	addrs := map[string]string{
		"analytics": cfg.External.AnalyticsService,
		"ml": cfg.External.MlService,
	}

	service := s.NewService(repo, addrs)
	handler := h.NewHandler(service, handlerLogger)
	server := h.NewServer(cfg.Server.Port, handler.Router())

	server.Start()
}