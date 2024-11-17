package postgres

import (
    "fmt"
    "database/sql"

    "github.com/lib/pq"

    "github.com/singl3focus/t1_hackathon/backend/internal/models"
)    

func (r *Repository) AddSprint(sprint models.Sprint) error {
    query := `INSERT INTO data_sprints (sprint_name, sprint_status, sprint_start_date, sprint_end_date, entity_ids)
VALUES ($1, $2, $3, $4, $5)`

    _, err := r.db.Exec(query, sprint.SprintName, sprint.SprintStatus, sprint.SprintStartDate, sprint.SprintEndDate, pq.Array(sprint.EntityIDs))
    if err != nil {
        return fmt.Errorf("failed to insert sprint: %v", err)
    }
    return nil
}

func (r *Repository) GetSprint(sprintId int) (models.Sprint, error) {
    query := `SELECT * FROM data_sprints WHERE sprint_id = $1`
    
    var sprint models.Sprint
    err := r.db.Get(&sprint, query, sprintId)
    if err != nil {
        if err == sql.ErrNoRows {
            return sprint, fmt.Errorf("no sprint found with id %d", sprintId)
        }
        return sprint, fmt.Errorf("error getting sprint with id %d: %v", sprintId, err)
    }

    return sprint, nil
}

func (r *Repository) GetAllSprints() ([]models.Sprint, error) {
    query := `SELECT sprint_id,
sprint_name, sprint_status, sprint_start_date, sprint_end_date FROM data_sprints`
    
    rows, err := r.db.Query(query)
    if err != nil {
        return nil, fmt.Errorf("error getting all sprints: %v", err)
    }
    defer rows.Close()

    sprints := make([]models.Sprint, 0, 1)
    for rows.Next() {
        var sprint models.Sprint
        err := rows.Scan(&sprint.SprintId, &sprint.SprintName,
             &sprint.SprintStatus, &sprint.SprintStartDate, &sprint.SprintEndDate)
        if err != nil {
            return nil, fmt.Errorf("error scanning row: %v", err)
        }

        sprints = append(sprints,sprint)
    }

    return sprints, nil
}

func (r *Repository) UpdateSprintStatus(sprintId int, newStatus string) (error) {
    query := `UPDATE data_sprints SET sprint_status = $1 WHERE sprint_id = $2`
    
    _, err := r.db.Exec(query, newStatus, sprintId)
    if err != nil {
        return fmt.Errorf("error updating sprint status: %v", err)
    }

    return nil
}

/*_______________________________________________________________________________*/

func (r *Repository) AddSprintHealth(sprintId int, isHealth bool) error {
    query := `INSERT INTO sprint_health (sprint_id, is_health) VALUES ($1, $2)`

    _, err := r.db.Exec(query, sprintId, isHealth)
    if err != nil {
        return fmt.Errorf("error inserting sprint health: %v", err)
    }

    return nil
}


func (r *Repository) CheckSprintHealth(sprintId int) (bool, bool, error) {
    query := `SELECT is_health FROM sprint_health WHERE sprint_id = $1 LIMIT 1`

    var isHealth bool
    err := r.db.QueryRow(query, sprintId).Scan(&isHealth)
    if err != nil {
        if err == sql.ErrNoRows {
            return false, false, nil
        }
        return false, false, fmt.Errorf("error querying sprint health: %v", err)
    }

    return isHealth, true, nil
}
