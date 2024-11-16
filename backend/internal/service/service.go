package service

import (
	"github.com/singl3focus/t1_hackathon/backend/internal/interfaces"
	"github.com/singl3focus/t1_hackathon/backend/internal/models"
)

type Service struct {
	repo interfaces.Repository
}

func NewService(repo interfaces.Repository) interfaces.Service {
	return &Service{
		repo: repo,
	}
}

func (s *Service) AddSprint(model models.Sprint) error {
	return s.repo.AddSprint(model)
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

func (s *Service) UpdateTaskStatus(entityID int, newStatus string) error {
	return s.repo.UpdateTaskStatus(entityID, newStatus)
}

func (s *Service) UpdateTaskState(entityID int, newState string) error {
	return s.repo.UpdateTaskState(entityID, newState)
}

func (s *Service) GetAllSprintTasks(sprintID int) ([]models.Task, error) {
	return s.repo.GetAllSprintTasks(sprintID)
}

func (s *Service) GetTaskByTicketNumber(ticketNumber string) (models.Task, error) {
	return s.repo.GetTaskByTicketNumber(ticketNumber)
}