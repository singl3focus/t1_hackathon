package postgres

import (
	"fmt"

	_ "github.com/lib/pq"
	"github.com/jmoiron/sqlx"
	"github.com/pressly/goose"

	"github.com/singl3focus/t1_hackathon/backend/internal/interfaces"
	"github.com/singl3focus/t1_hackathon/backend/pkg/logging"
)

type Repository struct {
	logger *logging.ModuleLogger
	db *sqlx.DB
}

func NewPostgresDB(host, port, username, pass, dbname, sslmode string, logger *logging.ModuleLogger) (interfaces.Repository, error) {
	authData := fmt.Sprintf(
		"host=%s port=%s user=%s dbname=%s password=%s sslmode=%s",
		host, port, username, dbname, pass, sslmode)

	db, err := sqlx.Open("postgres", authData)
	if err != nil {
		return nil, err
	}

	err = db.Ping()
	if err != nil {
		return nil, err
	}

	dbMigrations := db.DB
	if err := goose.Run("up", dbMigrations, "migrations"); err != nil {
        return nil, err
    }

	return &Repository{
		db: db,
		logger: logger,
	}, nil
}