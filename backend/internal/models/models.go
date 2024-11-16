package models

import "time"

// ADD SPRINT - все поля, кроме sprint_id 
// GET SPRINT - все поля, кроме entity_ids
type Sprint struct {
	SprintId        int       `json:"sprint_id"`
	SprintName      string    `json:"sprint_name"`
	SprintStatus    string    `json:"sprint_status"`
	SprintStartDate time.Time `json:"sprint_start_date"`
	SprintEndDate   time.Time `json:"sprint_end_date"`
	EntityIDs       []int     `json:"entity_ids"`
}

type Task struct {
	EntityID       int        `json:"entity_id"`
	Area           string     `json:"area"`
	Type           string     `json:"type"`
	Status         string     `json:"status"`
	State          string     `json:"state"`
	Priority       string     `json:"priority"`
	TicketNumber   string     `json:"ticket_number"`
	Name           string     `json:"name"`
	CreateDate     time.Time  `json:"create_date"`
	CreatedBy      string     `json:"created_by"`
	UpdateDate     time.Time  `json:"update_date"`
	UpdatedBy      string     `json:"updated_by"`
	ParentTicketID *int       `json:"parent_ticket_id"` // может быть NULL
	Assignee       *string    `json:"assignee"`         // может быть NULL
	Owner          string     `json:"owner"`
	DueDate        *time.Time `json:"due_date"` // может быть NULL
	Rank           string     `json:"rank"`
	Estimation     *float64   `json:"estimation"` // может быть NULL
	Spent          *float64   `json:"spent"`      // может быть NULL
	Resolution     *string    `json:"resolution"` // может быть NULL
}

type TaskHistory struct {
	EntityID            int       `json:"entity_id"`
	HistoryPropertyName string    `json:"history_property_name"`
	HistoryDate         time.Time `json:"history_date"`
	HistoryVersion      float64   `json:"history_version"`
	HistoryChangeType   string    `json:"history_change_type"`
	HistoryChange       string    `json:"history_change"`
}
