package http

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/singl3focus/t1_hackathon/backend/internal/interfaces"
	"github.com/singl3focus/t1_hackathon/backend/internal/models"
	"github.com/singl3focus/t1_hackathon/backend/pkg/logging"
)

type Handler struct {
	logger  *logging.ModuleLogger
	service interfaces.Service
}

func NewHandler(service interfaces.Service, logger *logging.ModuleLogger) *Handler {
	return &Handler{
		service: service,
		logger:  logger,
	}
}

func (h *Handler) Healthy(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
}

/*____________________________[SPRINT]____________________________*/

func (h *Handler) AddSprint(w http.ResponseWriter, r *http.Request) {
	var dto models.Sprint

	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.AddSprint(dto)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Sprint was successfully added")
}

func (h *Handler) GetAllSprints(w http.ResponseWriter, r *http.Request) {
	answer, err := h.service.GetAllSprints()
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(answer); err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
	}
}

type UpdateSprintStatusRequest struct {
	SprintId  int    `json:"sprint_id"`
	NewStatus string `json:"new_status"`
}

func (h *Handler) UpdateSprintStatus(w http.ResponseWriter, r *http.Request) {
	var dto UpdateSprintStatusRequest

	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.UpdateSprintStatus(dto.SprintId, dto.NewStatus)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Sprint status was successfully updated")
}

type CheckSprintHealthResponse struct {
	IsHealth bool `json:"is_health"`
}

func (h *Handler) CheckSprintHealth(w http.ResponseWriter, r *http.Request) {
	sprintIDstr := r.URL.Query().Get("sprint_id")
	if sprintIDstr == "" {
		h.NewErrorResponse(w, http.StatusInternalServerError, "'sprint_id' is empty", "")
		return
	}
	sprintID, err := strconv.Atoi(sprintIDstr)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "'sprint_id' is not integer", err.Error())
		return
	}

	is_health, err := h.service.CheckSprintHealth(sprintID)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	answer := CheckSprintHealthResponse{IsHealth: is_health}
	
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(answer); err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
	}
}


/*____________________________[TASK]____________________________*/

func (h *Handler) AddTask(w http.ResponseWriter, r *http.Request) {
	var dto models.Task

	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.AddTask(dto)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Task was successfully added")
}

func (h *Handler) AddTasks(w http.ResponseWriter, r *http.Request) {
	var tasks []models.Task

	if err := json.NewDecoder(r.Body).Decode(&tasks); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.AddTasks(tasks)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Tasks were successfully added")
}


type UpdateTaskStatusRequest struct {
	EntityId  int    `json:"entity_id"`
	NewStatus string `json:"new_status"`
}

func (h *Handler) UpdateTaskStatus(w http.ResponseWriter, r *http.Request) {
	var dto UpdateTaskStatusRequest

	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.UpdateTaskStatus(dto.EntityId, dto.NewStatus)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Task status was successfully updated")
}

type UpdateTaskStatesRequest struct {
	EntityId int    `json:"entity_id"`
	NewState string `json:"new_state"`
}

func (h *Handler) UpdateTaskState(w http.ResponseWriter, r *http.Request) {
	var dto UpdateTaskStatesRequest

	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.UpdateTaskState(dto.EntityId, dto.NewState)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Task state was successfully updated")
}

func (h *Handler) GetAllSprintTasks(w http.ResponseWriter, r *http.Request) {
	sprintIDstr := r.URL.Query().Get("sprint_id")
	if sprintIDstr == "" {
		h.NewErrorResponse(w, http.StatusInternalServerError, "'sprint_id' is empty", "")
		return
	}
	sprintID, err := strconv.Atoi(sprintIDstr)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "'sprint_id' is not integer", err.Error())
		return
	}
	
	answer, err := h.service.GetAllSprintTasks(sprintID)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(answer); err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
	}
}

func (h *Handler) GetTaskByTicketNumber(w http.ResponseWriter, r *http.Request) {
	ticketNumber := r.URL.Query().Get("ticket_number")
	if ticketNumber == "" {
		h.NewErrorResponse(w, http.StatusInternalServerError, "'ticket_number' is empty", "")
		return
	}

	answer, err := h.service.GetTaskByTicketNumber(ticketNumber)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(answer); err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
	}
}


/*____________________________[TASK HISTORY]____________________________*/

func (h *Handler) AddTasksChanges(w http.ResponseWriter, r *http.Request) {
	var tasksChanges []models.TaskChange

	if err := json.NewDecoder(r.Body).Decode(&tasksChanges); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.AddTasksChanges(tasksChanges)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Tasks changes were successfully added")
}