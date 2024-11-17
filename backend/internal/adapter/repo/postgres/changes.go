package postgres

import (
	"fmt"

	"github.com/singl3focus/t1_hackathon/backend/internal/models"
)   

func (r *Repository) AddTasksChanges(changes []models.TaskChange) error {
    tx, err := r.db.Beginx()
	if err != nil {
		return fmt.Errorf("failed to start transaction: %w", err)
	}

    query := `INSERT INTO data_history (entity_id, history_property_name, history_date, history_version, history_change_type, history_change)
VALUES ($1, $2, $3, $4, $5, $6)`

    for _, change := range changes {
        _, err := tx.Exec(query, &change.EntityID, &change.HistoryPropertyName, &change.HistoryDate,
			&change.HistoryVersion, &change.HistoryChangeType, &change.	HistoryChange)
        if err != nil {
            tx.Rollback()
            
            return fmt.Errorf("error inserting data_history: %v", err)
        }
    }

    if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

    return nil
}