package main

import (
	"go_sqlc_mux/internal/db"
	"go_sqlc_mux/internal/repository"
	"go_sqlc_mux/internal/service"
	"go_sqlc_mux/internal/transport/http"
	"log"
)

func Run() error {
	log.Println("Setting Up Our APP")

	database, err := db.NewDatabase()
	if err != nil {
		log.Println("failed to setup connection to the database")
		return err
	}
	log.Println(database)

	// database.Ping(context.Background())

	queries := repository.New(database.Client)
	carRegistryService := service.NewCarRegistryService(queries)
	handler := http.NewHandler(carRegistryService)

	if err := handler.Serve(); err != nil {
		log.Println("failed to gracefully serve our application")
		return err
	}

	return nil
}

func main() {
	if err := Run(); err != nil {
		log.Println(err)
		log.Fatal("Error starting up our REST API")
	}
}
