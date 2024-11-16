package interfaces

import (
	"github.com/singl3focus/t1_hackathon/backend/internal/models"
)

type Service interface {
	AddSprint(models.Sprint) error
	GetAllSprints() ([]models.Sprint, error)
	UpdateSprintStatus(sprintId int, newStatus string) error

	AddTask(task models.Task) error
	UpdateTaskStatus(entityID int, newStatus string) error
	UpdateTaskState(entityID int, newState string) error
	GetAllSprintTasks(sprintID int) ([]models.Task, error)
	GetTaskByTicketNumber(ticketNumber string) (models.Task, error)
}	

type Repository interface {
	AddSprint(models.Sprint) error
	GetAllSprints() ([]models.Sprint, error)
	UpdateSprintStatus(sprintId int, newStatus string) error

	AddTask(task models.Task) error
	UpdateTaskStatus(entityID int, newStatus string) error
	UpdateTaskState(entityID int, newState string) error
	GetAllSprintTasks(sprintID int) ([]models.Task, error)
	GetTaskByTicketNumber(ticketNumber string) (models.Task, error)
}
