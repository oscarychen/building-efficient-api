// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.25.0
// source: car_registry.sql

package repository

import (
	"context"
	"time"
)

const getAllCars = `-- name: GetAllCars :many
SELECT "car_registry_car"."id", "car_registry_car"."vin", "car_registry_car"."owner", "car_registry_car"."created_at", "car_registry_car"."updated_at", "car_registry_car"."model_id" AS "car_model_id", "car_registry_carmodel"."name" AS "car_model_name", "car_registry_carmodel"."year" AS "car_model_year", "car_registry_carmodel"."color" AS "color" FROM "car_registry_car" INNER JOIN "car_registry_carmodel" ON ("car_registry_car"."model_id" = "car_registry_carmodel"."id")
`

type GetAllCarsRow struct {
	ID           int64     `json:"id"`
	Vin          string    `json:"vin"`
	Owner        string    `json:"owner"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	CarModelID   int64     `json:"car_model_id"`
	CarModelName string    `json:"car_model_name"`
	CarModelYear int32     `json:"car_model_year"`
	Color        string    `json:"color"`
}

func (q *Queries) GetAllCars(ctx context.Context) ([]GetAllCarsRow, error) {
	rows, err := q.db.QueryContext(ctx, getAllCars)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var items []GetAllCarsRow
	for rows.Next() {
		var i GetAllCarsRow
		if err := rows.Scan(
			&i.ID,
			&i.Vin,
			&i.Owner,
			&i.CreatedAt,
			&i.UpdatedAt,
			&i.CarModelID,
			&i.CarModelName,
			&i.CarModelYear,
			&i.Color,
		); err != nil {
			return nil, err
		}
		items = append(items, i)
	}
	if err := rows.Close(); err != nil {
		return nil, err
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return items, nil
}
