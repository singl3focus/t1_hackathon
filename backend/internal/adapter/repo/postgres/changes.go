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

func (r *Repository) GetTaskChanges(entityID int) ([]models.TaskChange, error) {
    query := `SELECT * FROM data_history WHERE entity_id = $1`

    rows, err := r.db.Query(query, entityID)
    if err != nil {
        return nil, fmt.Errorf("error getting data_history: %v", err)
    }
    defer rows.Close()

    changes := make([]models.TaskChange, 0, 1)
    for rows.Next() {
        var change models.TaskChange

        err := rows.Scan(&change.EntityID, &change.HistoryPropertyName,
            &change.HistoryDate, &change.HistoryVersion,
            &change.HistoryChangeType, &change.HistoryChange)
        if err != nil {
            return nil, fmt.Errorf("error scanning task row: %v", err)
        }

        changes = append(changes, change)
    }

    if err = rows.Err(); err != nil {
        return nil, fmt.Errorf("error reading rows: %v", err)
    }

    return changes, nil
}

func (r *Repository) GetAllSprintChanges(tasks []models.Task) ([]models.TaskChange, error) {
    tx, err := r.db.Beginx()
	if err != nil {
		return nil, fmt.Errorf("failed to start transaction: %w", err)
	}

    query := `SELECT * FROM data_history WHERE entity_id = &1`

    changes := make([]models.TaskChange, 0, 1)
    for _, task := range tasks {
        var change models.TaskChange
        err := tx.Get(&change, query, task.EntityID)
        if err != nil {
            tx.Rollback()
            
            return nil, fmt.Errorf("error getting data_history: %v", err)
        }

        changes = append(changes, change)
    }

    if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

    return changes, nil
}