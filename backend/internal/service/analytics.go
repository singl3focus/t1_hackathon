package service

import (
	"fmt"
	"bytes"
	"net/http"
	"encoding/json"
)

const (
	SubpathCheckSprintHealth = "/health/check"
)

type CheckSprintHealthResponse struct {
	IsHealth bool `json:"is_health"`
}

func (s *Service) CheckSprintHealth(sprintId int) (bool, error) {
	is_health, ok, err := s.repo.CheckSprintHealth(sprintId)
	if err != nil {
		return false, err
	}
	if ok { // [Dev] Если данные о здоровье спринта есть, то возвращаем их 
		return is_health, nil
	}

	/* IF DATA NOT FOUND */

	tasks, err := s.repo.GetAllSprintTasks(sprintId)
	jsonData, err := json.Marshal(tasks)
    if err != nil {
        return false, fmt.Errorf("failed to marshal tasks: %v", err)
    }

	addr := s.addrs[AnalyticsKey] + SubpathCheckSprintHealth

	client := &http.Client{} 
    req, err := http.NewRequest("GET", addr, bytes.NewBuffer(jsonData)) 
    resp, err := client.Do(req) 
    if err != nil { 
        return false, err
    } 
    defer resp.Body.Close() 
    
	var dto CheckSprintHealthResponse
	err = json.NewDecoder(resp.Body).Decode(&dto)
	if err != nil {
		return false, err
	}

	err = s.repo.AddSprintHealth(sprintId, dto.IsHealth)
	if err != nil {
		s.logger.Error("invalid adding health status of sprint", "(error)", err.Error())
		// [Dev] Мы получили данные с сервиса, поэтому ошибку лишь логгируем
	}

	return dto.IsHealth, nil
} 