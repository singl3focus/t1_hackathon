package http

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type Error struct {
	Error string `json:"error"`
}

func (h *Handler) NewErrorResponse(w http.ResponseWriter, statusCode int, clientMessage, devMessage string) {
	h.logger.Warn(fmt.Sprintf("Client: %s | Dev: %s", clientMessage, devMessage))

    errorResponse := Error{Error: clientMessage}
    jsonResponse, _ := json.Marshal(errorResponse)

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(statusCode)
    w.Write(jsonResponse)
}

type Result struct {
	Message string `json:"message"`
}

func (h *Handler) NewTextResponse(w http.ResponseWriter, clientMessage string) {
    errorResponse := Result{Message: clientMessage}
    jsonResponse, _ := json.Marshal(errorResponse)

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    if _, err := w.Write(jsonResponse); err != nil {
		h.NewErrorResponse(w, http.StatusInternalServerError, "Server error", err.Error())
	}
}