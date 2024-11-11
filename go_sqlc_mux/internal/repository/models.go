// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.25.0

package repository

import (
	"time"
)

type CarRegistryCar struct {
	ID        int64     `json:"id"`
	Vin       string    `json:"vin"`
	Owner     string    `json:"owner"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	ModelID   int64     `json:"model_id"`
}

type CarRegistryCarmodel struct {
	ID        int64     `json:"id"`
	Name      string    `json:"name"`
	Make      string    `json:"make"`
	Year      int32     `json:"year"`
	Color     string    `json:"color"`
	Price     string    `json:"price"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}
