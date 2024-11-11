package http

import (
	"context"
	"encoding/json"
	"go_sqlc_mux/internal/repository"
	"net/http"
)

type CarRegistryService interface {
	GetAllCars(ctx context.Context) ([]repository.GetAllCarsRow, error)
}

func (h *Handler) GetAllCars(w http.ResponseWriter, r *http.Request) {
	cars, err := h.CarRegistryService.GetAllCars(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	jsonData, err := json.Marshal(cars)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	_, err = w.Write(jsonData)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
}
