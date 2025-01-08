FROM golang:1.23.1

# Setup the app
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .

# Build the Go app
RUN go build -o main ./cmd/lauchServer

EXPOSE 8000
# Run the binary
CMD ["./main"]