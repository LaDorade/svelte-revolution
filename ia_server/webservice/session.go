package webservice

import "TestNLP/pkg/censorship"

type Session struct {
	censorship *censorship.Censorship
	id         string
	Scenario   censorship.Scenario
	step       int
	maxStep    int
}

func NewSession(id string, scenarioFile string) (*Session, error) {
	scenario, err := censorship.LoadScenario(scenarioFile)
	step := 0
	return &Session{censorship.NewCensorship(scenario.Steps[step].BannedWords, scenario.Steps[step].ActionToPerform, scenario.Steps[step].ActionKeyWords), id, scenario, step, len(scenario.Steps)}, err
}

func (s *Session) NextStep() {
	if s.step < s.maxStep {
		s.step++
		s.censorship.NextStep(s.Scenario.Steps[s.step].BannedWords, s.Scenario.Steps[s.step].ActionToPerform, s.Scenario.Steps[s.step].ActionKeyWords)
	}

}
