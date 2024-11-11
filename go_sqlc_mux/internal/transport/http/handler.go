package http

import (
	"context"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"
)

type Handler struct {
	Router             *mux.Router
	ProtectedRouter    *mux.Router
	CarRegistryService CarRegistryService
	Server             *http.Server
}

func NewHandler(carRegistryService CarRegistryService) *Handler {
	h := &Handler{
		CarRegistryService: carRegistryService,
	}
	h.Router = mux.NewRouter()

	h.mapRoutes()
	//h.Router.Use(middleware.JSONMiddleware)

	h.Server = &http.Server{
		Addr:    "0.0.0.0:8080",
		Handler: h.Router,
	}
	return h
}

func (h *Handler) mapRoutes() {

	h.Router.HandleFunc("/cars/", h.GetAllCars).Methods("GET")
}

func (h *Handler) Serve() error {
	go func() {
		if err := h.Server.ListenAndServe(); err != nil {
			log.Println(err.Error())
		}
	}()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	<-c

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	h.Server.Shutdown(ctx)

	log.Println("shut down gracefully")
	return nil
}
