package db

import (
	"context"
	"fmt"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"log"
)

type Database struct {
	Client *sqlx.DB
}

// NewDatabase - returns a pointer to a database object
func NewDatabase() (*Database, error) {
	log.Println("Setting up new database connection")

	connectionString := "host=db port=5432 sslmode=disable user=postgres dbname=api_demo_db password=postgres"
	//connectionString := "host=127.0.0.1 port=5432 sslmode=disable user=postgres dbname=api_demo_db password=postgres"

	db, err := sqlx.Connect("postgres", connectionString)
	if err != nil {
		return &Database{}, fmt.Errorf("could not connect to database: %w", err)
	}

	return &Database{
		Client: db,
	}, nil
}

func (d *Database) Ping(ctx context.Context) error {
	return d.Client.DB.PingContext(ctx)
}
