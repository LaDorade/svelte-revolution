package main

import (
	"fmt"

	server "TestNLP/webservice"
)

var port = ":8000"

func main() {
	server := server.NewServerAgent(port)
	server.Start()
	fmt.Scanln()
}
