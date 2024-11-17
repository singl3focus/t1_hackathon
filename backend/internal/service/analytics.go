package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/singl3focus/t1_hackathon/backend/internal/models"
)

const (
	SubpathCheckSprintHealth = "/health/check"
)

type CheckSprintHealthResponse struct {
	IsHealth bool `json:"is_health"`
}

func (s *Service) CheckSprintHealth(sprintId int) (models.AnalyticsSprint, error) {
	var result models.AnalyticsSprint

	sprintInfo, err := s.repo.GetSprint(sprintId)
	if err != nil {
		return result, err
	}

	tasksInfo, err := s.repo.GetAllSprintTasks(sprintId)
	if err != nil {
		return result, err
	}

	chagesInfo, err := s.repo.GetAllSprintChanges(tasksInfo)
	if err != nil {
		return result, err
	}

	data := struct {
		Sprints  []models.Sprint     `json:"sprints"`
		Entities []models.Task       `json:"entities"`
		History  []models.TaskChange `json:"history"`
	}{
		Sprints: []models.Sprint{sprintInfo},
		Entities: tasksInfo,
		History: chagesInfo,
	}

	jsonData, err := json.Marshal(data)
	if err != nil {
		return result, fmt.Errorf("failed to marshal tasks: %v", err)
	}

	addr := s.addrs[AnalyticsKey] + SubpathCheckSprintHealth

	client := &http.Client{}
	req, err := http.NewRequest("GET", addr, bytes.NewBuffer(jsonData))
	resp, err := client.Do(req)
	if err != nil {
		return result, err
	}
	defer resp.Body.Close()

	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return result, err
	}

	return result, nil
}
