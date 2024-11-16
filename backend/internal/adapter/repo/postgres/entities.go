package postgres

import (
	"fmt"
	"time"
    "strings"
    "strconv"
	"database/sql"

	"github.com/lib/pq"

	"github.com/singl3focus/t1_hackathon/backend/internal/models"
)    

func (r *Repository) AddTask(task models.Task) error {
    query := `
        INSERT INTO data_entities (
            entity_id, area, type, status, state, priority, ticket_number, name, create_date, created_by, 
            update_date, updated_by, assignee, owner, rank, estimation, spent)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)`

    _, err := r.db.Exec(query, task.EntityID, task.Area, task.Type, task.Status, task.State, task.Priority, 
        task.TicketNumber, task.Name, task.CreateDate, task.CreatedBy, task.UpdateDate, task.UpdatedBy, 
        task.Assignee, task.Owner, task.Rank, task.Estimation, task.Spent)
    if err != nil {
        return fmt.Errorf("error inserting data_entity: %v", err)
    }
    return nil
}

func (r *Repository) UpdateTaskStatus(entityID int, newStatus string) error {
    query := `UPDATE data_entities SET status = $1 WHERE entity_id = $2`
    _, err := r.db.Exec(query, newStatus, entityID)
    if err != nil {
        return fmt.Errorf("error updating task status: %v", err)
    }
    return nil
}

func (r *Repository) UpdateTaskState(entityID int, newState string) error {
    query := `UPDATE data_entities SET state = $1 WHERE entity_id = $2`
    _, err := r.db.Exec(query, newState, entityID)
    if err != nil {
        return fmt.Errorf("error updating task status: %v", err)
    }
    return nil
}

// GetAllSprintTasks получает все задачи, связанные с указанным спринтом
func (r *Repository) GetAllSprintTasks(sprintID int) ([]models.Task, error) {
    querySprint := `SELECT entity_ids FROM data_sprints WHERE sprint_id = $1`
    
    row := r.db.QueryRow(querySprint, sprintID)

    var rawEntityIDs string
    err := row.Scan(&rawEntityIDs)
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("no sprint found with id %d", sprintID)
        }
        return nil, fmt.Errorf("error fetching sprint data: %v", err)
    }

    // Преобразуем строку в []int
    entityIDs := r.parseEntityIDs(rawEntityIDs)

    queryTasks := `
        SELECT entity_id, area, type, status, state, priority, ticket_number, name, create_date, created_by, 
               update_date, updated_by, assignee, owner, due_date, rank, estimation, spent, resolution
        FROM data_entities 
        WHERE entity_id = ANY($1)
    `
    
    rows, err := r.db.Query(queryTasks, pq.Array(entityIDs))
    if err != nil {
        return nil, fmt.Errorf("error fetching tasks: %v", err)
    }
    defer rows.Close()

    tasks := make([]models.Task, 0, 1)
    for rows.Next() {
        var task models.Task

        err := rows.Scan(
            &task.EntityID, &task.Area, &task.Type, &task.Status, &task.State, &task.Priority,
            &task.TicketNumber, &task.Name, &task.CreateDate, &task.CreatedBy, &task.UpdateDate, 
            &task.UpdatedBy, &task.Assignee, &task.Owner, &task.DueDate, &task.Rank,
            &task.Estimation, &task.Spent, &task.Resolution)
        if err != nil {
            return nil, fmt.Errorf("error scanning task row: %v", err)
        }

        tasks = append(tasks, task)
    }

    if err = rows.Err(); err != nil {
        return nil, fmt.Errorf("error reading rows: %v", err)
    }

    return tasks, nil
}

func (r *Repository) parseEntityIDs(s string) []int {
    s = strings.Trim(s, "{}")           // Убираем фигурные скобки
    strIDs := strings.Split(s, ",")     // Разбиваем по запятой
    ids := make([]int, len(strIDs))     // Инициализируем слайс для целых чисел

    for i, strID := range strIDs {
        num, err := strconv.Atoi(strings.TrimSpace(strID)) // Преобразуем в int
        if err != nil {
            r.logger.Error("Error parsing entity ID '%s': %v", strID, err)
            continue
        }
        ids[i] = num
    }

    return ids
}



func (r *Repository) GetTaskByTicketNumber(ticketNumber string) (models.Task, error) {
    query := `SELECT entity_id, area, type, status, state, priority, ticket_number, name, create_date, created_by, update_date, 
                     updated_by, parent_ticket_id, assignee, owner, due_date, rank, estimation, spent, resolution
              FROM data_entities WHERE ticket_number = $1`
    
    row := r.db.QueryRow(query, ticketNumber)

    var task models.Task
    var dueDate *time.Time
    var estimation, spent *float64
    var resolution *string

    err := row.Scan(
        &task.EntityID, &task.Area, &task.Type, &task.Status, &task.State, &task.Priority,
        &task.TicketNumber, &task.Name, &task.CreateDate, &task.CreatedBy, &task.UpdateDate,
        &task.UpdatedBy, &task.ParentTicketID, &task.Assignee, &task.Owner, &dueDate,
        &task.Rank, &estimation, &spent, &resolution)

    if err != nil {
        if err == sql.ErrNoRows {
            return task, fmt.Errorf("no task found with ticket number %s", ticketNumber)
        }
        return task, fmt.Errorf("error scanning task: %v", err)
    }

    // Присваиваем значения для optional полей
    task.DueDate = dueDate
    task.Estimation = estimation
    task.Spent = spent
    task.Resolution = resolution

    return task, nil
}