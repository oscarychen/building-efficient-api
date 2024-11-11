BEGIN;
--
-- Create model CarModel
--
CREATE TABLE "car_registry_carmodel" ("id" bigint NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, "name" varchar(100) NOT NULL, "make" varchar(100) NOT NULL, "year" integer NOT NULL, "color" varchar(100) NOT NULL, "price" numeric(10, 2) NOT NULL, "created_at" timestamp with time zone NOT NULL, "updated_at" timestamp with time zone NOT NULL);
--
-- Create model Car
--
CREATE TABLE "car_registry_car" ("id" bigint NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, "vin" varchar(17) NOT NULL, "owner" varchar(100) NOT NULL, "created_at" timestamp with time zone NOT NULL, "updated_at" timestamp with time zone NOT NULL, "model_id" bigint NOT NULL);
ALTER TABLE "car_registry_car" ADD CONSTRAINT "car_registry_car_model_id_e7a8fb5f_fk_car_registry_carmodel_id" FOREIGN KEY ("model_id") REFERENCES "car_registry_carmodel" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "car_registry_car_model_id_e7a8fb5f" ON "car_registry_car" ("model_id");
COMMIT;
