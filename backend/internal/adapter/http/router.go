package http

import (
	"net/http"

	"github.com/gorilla/mux"
)

func (h *Handler) Router() http.Handler {
	public := mux.NewRouter()
	_ = public.PathPrefix("").Subrouter() // [UNUSED]

	// [Public router]
	public.HandleFunc("/healthy", h.Healthy).Methods(http.MethodGet)

	public.HandleFunc("/sprint/add", h.AddSprint).Methods(http.MethodPost)
	public.HandleFunc("/sprint/update-status", h.UpdateSprintStatus).Methods(http.MethodPost)
	public.HandleFunc("/sprint/all", h.GetAllSprints).Methods(http.MethodGet)

	public.HandleFunc("/sprint/task/all", h.GetAllSprintTasks).Methods(http.MethodGet)

	public.HandleFunc("/task/add", h.AddTask).Methods(http.MethodPost)
	public.HandleFunc("/task/update-status", h.UpdateTaskStatus).Methods(http.MethodPost)
	public.HandleFunc("/task/update-state", h.UpdateTaskState).Methods(http.MethodPost)
	public.HandleFunc("/task/get-by-ticketnumber", h.GetTaskByTicketNumber).Methods(http.MethodGet)

	return public
}
