package censorship

import (
	"TestNLP/pkg/libs"
	"encoding/json"
	"io"
	"os"
)

type Scenario struct {
	Ends  []string    `json:"ends"`
	Steps []libs.Step `json:"steps"`
}

func LoadScenario(file string) (Scenario, error) {
	jsonFile, err := os.Open(file)
	if err != nil {
		return Scenario{nil, nil}, err
	}
	defer jsonFile.Close()

	byteValue, _ := io.ReadAll(jsonFile)
	var scenario Scenario
	err = json.Unmarshal(byteValue, &scenario)
	if err != nil {
		return Scenario{nil, nil}, err
	}
	return scenario, nil
}
