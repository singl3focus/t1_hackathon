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

// AddSprint godoc
// @Summary Add single sprint
// @Tags sprint
// @Accept json
// @Produce json
// @Param sprint body models.Sprint  true "Sprint"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /sprint/add [post]
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

// AddSprints godoc
// @Summary Add array of sprints
// @Tags sprint
// @Accept json
// @Produce json
// @Param sprint body []models.Sprint true "Sprints"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /sprints/add [post]
func (h *Handler) AddSprints(w http.ResponseWriter, r *http.Request) {
	var dto []models.Sprint

	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		h.NewErrorResponse(w, http.StatusBadRequest, "Invalid request", err.Error())
		return
	}

	err := h.service.AddSprints(dto)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
		return
	}

	h.NewTextResponse(w, "Sprint was successfully added")
}

// GetAllSprints godoc
// @Summary Get array of sprints
// @Tags sprint
// @Produce json
// @Success 200 {array} models.Sprint
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /sprint/all [get]
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

// UpdateSprintStatus godoc
// @Summary Update status of sprint
// @Tags sprint
// @Accept json
// @Produce json
// @Param updatesprint body UpdateSprintStatusRequest true "UpdateSprintStatus"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /sprint/update-status [post]
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

	answer, err := h.service.CheckSprintHealth(sprintID)
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

/*____________________________[TASK]____________________________*/

// AddTask godoc
// @Summary Add single task
// @Tags task
// @Accept json
// @Produce json
// @Param task body models.Task true "AddTask"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /task/add [post]
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

// AddTasks godoc
// @Summary Add array of tasks
// @Tags task
// @Accept json
// @Produce json
// @Param task body []models.Task true "AddTasks"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /task/add [post]
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

// UpdateSprintStatus godoc
// @Summary Update status of task
// @Tags task
// @Accept json
// @Produce json
// @Param updatestatus body UpdateTaskStatusRequest true "UpdateSprintStatus"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /task/update-status [post]
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

// UpdateTaskState godoc
// @Summary Update state of task
// @Tags task
// @Accept json
// @Produce json
// @Param updatestate body UpdateTaskStatesRequest true "UpdateTaskState"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /task/update-state [post]
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

// GetAllSprintTasks godoc
// @Summary Get all sprint tasks
// @Tags sprint
// @Produce json
// @Param sprint_id query int true "GetAllSprintTasks"
// @Success 200 {array} models.Task
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /sprint/task/all [post]
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

// GetTaskByTicketNumber godoc
// @Summary Get task by TicketNumber
// @Tags task
// @Produce json
// @Param ticket_number query string true "GetTaskByTicketNumber"
// @Success 200 {object} models.Task
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /task/get-by-ticketnumber [get]
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

// AddTasksChanges godoc
// @Summary Add array of tasks changes
// @Tags changes
// @Accept json
// @Produce json
// @Param taskschanges body []models.TaskChange true "AddTasksChanges"
// @Success 200 {object} Result
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /tasks/changes/add [post]
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

// GetTaskChanges godoc
// @Summary Get task changes by entity_id(task_id)
// @Tags changes
// @Produce json
// @Param entity_id query int true "GetTaskChanges"
// @Success 200 {array} models.TaskChange
// @Failure 400 {object} Error
// @Failure 500 {object} Error
// @Router /task/changes/all [get]
func (h *Handler) GetTaskChanges(w http.ResponseWriter, r *http.Request) {
	entityIDstr := r.URL.Query().Get("entity_id")
	if entityIDstr == "" {
		h.NewErrorResponse(w, http.StatusInternalServerError, "'entity_id' is empty", "")
		return
	}
	entityID, err := strconv.Atoi(entityIDstr)
	if err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "'entity_id' is not integer", err.Error())
		return
	}

	answer, err := h.service.GetTaskChanges(entityID)
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
