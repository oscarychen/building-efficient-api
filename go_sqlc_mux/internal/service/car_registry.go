package service

import (
	"context"
	"go_sqlc_mux/internal/repository"
)

type CarRegistryStore interface {
	GetAllCars(ctx context.Context) ([]repository.GetAllCarsRow, error)
}

type CarRegistryService struct {
	CarRegistryStore CarRegistryStore
}

func NewCarRegistryService(carRegistryStore CarRegistryStore) *CarRegistryService {
	return &CarRegistryService{
		CarRegistryStore: carRegistryStore,
	}
}

func (service *CarRegistryService) GetAllCars(ctx context.Context) ([]repository.GetAllCarsRow, error) {
	cars, err := service.CarRegistryStore.GetAllCars(ctx)
	if err != nil {
		return []repository.GetAllCarsRow{}, err
	}
	return cars, nil
}
