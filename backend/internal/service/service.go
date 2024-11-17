package service

import (
	"github.com/singl3focus/t1_hackathon/backend/internal/interfaces"
	"github.com/singl3focus/t1_hackathon/backend/internal/models"
	"github.com/singl3focus/t1_hackathon/backend/pkg/logging"
)

type Service struct {
	logger *logging.ModuleLogger
	repo interfaces.Repository
	addrs map[string]string
}

func NewService(repo interfaces.Repository, addrs map[string]string) interfaces.Service {
	return &Service{
		repo: repo,
		addrs: addrs,
	}
}

const (
	AnalyticsKey = "analytics"
	MlKey = "ml"
)

/* ________________[INTERNAL INTERACTION]________________*/

func (s *Service) AddSprint(model models.Sprint) error {
	return s.repo.AddSprint(model)
}

func (s *Service) AddSprints(sprints []models.Sprint) error {
	return s.repo.AddSprints(sprints)
}

func (s *Service) GetAllSprints() ([]models.Sprint, error) {
	return s.repo.GetAllSprints()
}

func (s *Service) UpdateSprintStatus(sprintId int, newStatus string) error {
	return s.repo.UpdateSprintStatus(sprintId, newStatus)
}

func (s *Service) AddTask(model models.Task) error {
	return s.repo.AddTask(model)
}

func (s *Service) AddTasks(models []models.Task) error {
	return s.repo.AddTasks(models)
}

func (s *Service) UpdateTaskStatus(entityID int, newStatus string) error {
	return s.repo.UpdateTaskStatus(entityID, newStatus)
}

func (s *Service) UpdateTaskState(entityID int, newState string) error {
	return s.repo.UpdateTaskState(entityID, newState)
}

func (s *Service) GetAllSprintTasks(sprintId int) ([]models.Task, error) {
	return s.repo.GetAllSprintTasks(sprintId)
}

func (s *Service) GetTaskByTicketNumber(ticketNumber string) (models.Task, error) {
	return s.repo.GetTaskByTicketNumber(ticketNumber)
}

func (s *Service) AddTasksChanges(models []models.TaskChange) error {
	return s.repo.AddTasksChanges(models)
}

func (s *Service) GetTaskChanges(entityID int) ([]models.TaskChange, error) {
	return s.repo.GetTaskChanges(entityID)
}
