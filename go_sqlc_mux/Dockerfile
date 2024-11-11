FROM golang:1.23-alpine

WORKDIR /usr/src/app

COPY ./go_sqlc_mux /usr/src/app

RUN go mod download
RUN go build -o main ./cmd/server/main.go

EXPOSE 8080
CMD ["./main"]