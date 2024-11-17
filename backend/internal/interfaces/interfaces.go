package interfaces

import (
	"github.com/singl3focus/t1_hackathon/backend/internal/models"
)

type Service interface {
	AddSprint(models.Sprint) error
	AddSprints(sprints []models.Sprint) error
	GetAllSprints() ([]models.Sprint, error)
	UpdateSprintStatus(sprintId int, newStatus string) error

	CheckSprintHealth(sprintId int) (models.AnalyticsSprint, error)

	AddTask(task models.Task) error
	AddTasks(task []models.Task) error
	UpdateTaskStatus(entityID int, newStatus string) error
	UpdateTaskState(entityID int, newState string) error
	GetAllSprintTasks(sprintID int) ([]models.Task, error)
	GetTaskByTicketNumber(ticketNumber string) (models.Task, error)

	AddTasksChanges(changes []models.TaskChange) error
	GetTaskChanges(entityID int) ([]models.TaskChange, error)
}

type Repository interface {
	AddSprint(models.Sprint) error
	AddSprints(sprints []models.Sprint) error
	GetSprint(sprintId int) (models.Sprint, error)
	GetAllSprints() ([]models.Sprint, error)
	UpdateSprintStatus(sprintId int, newStatus string) error

	AddSprintHealth(sprintId int, isHealth bool) error
	CheckSprintHealth(sprintId int) (bool, bool, error)

	AddTask(task models.Task) error
	AddTasks(task []models.Task) error
	UpdateTaskStatus(entityID int, newStatus string) error
	UpdateTaskState(entityID int, newState string) error
	GetAllSprintTasks(sprintID int) ([]models.Task, error)
	GetTaskByTicketNumber(ticketNumber string) (models.Task, error)

	AddTasksChanges(changes []models.TaskChange) error
	GetTaskChanges(entityID int) ([]models.TaskChange, error)
	GetAllSprintChanges(tasks []models.Task) ([]models.TaskChange, error)
}
