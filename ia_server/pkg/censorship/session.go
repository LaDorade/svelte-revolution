package censorship

import (
	"TestNLP/pkg/libs"
)

type Session struct {
	Censorship   *Censorship
	Id           string
	Scenario     Scenario
	Step         int
	MaxStep      int
	ScenarioFile string

	IdTerrain string
	IdGoodEnd string
	IdBadEnd  string
}

func NewSession(req libs.NewSessionRequest, scenarioFile string) (*Session, error) {
	scenario, err := LoadScenario(scenarioFile)

	if err != nil {
		return nil, err
	}

	IdTerrain := ""
	for _, s := range req.Sides {
		if s.Name == libs.Terrain {
			IdTerrain = s.Id
		}
	}

	IdGoodEnd := ""
	IdBadEnd := ""
	for _, e := range req.Ends {
		if e.Title == scenario.Ends[0] {
			IdGoodEnd = e.Id
		} else {
			IdBadEnd = e.Id
		}
	}

	step := 0
	return &Session{NewCensorship(scenario.Steps[step].BannedWords, scenario.Steps[step].ActionToPerform, scenario.Steps[step].ActionKeyWords), req.SessionID, scenario, step, len(scenario.Steps), scenarioFile, IdTerrain, IdGoodEnd, IdBadEnd}, err
}

func LoadSession(sd libs.SessionData) (*Session, error) {
	scenario, err := LoadScenario(sd.ScenarioFile)

	if err != nil {
		return nil, err
	}

	censorship := LoadCensorship(*sd.Censorship)
	return &Session{censorship, sd.ID, scenario, sd.Step, len(scenario.Steps), sd.ScenarioFile, sd.IdTerrain, sd.IdGoodEnd, sd.IdBadEnd}, err
}

func (s *Session) NextStep() bool {
	if s.Step <= s.MaxStep {
		s.Step++
		s.Censorship.NextStep(s.Scenario.Steps[s.Step].BannedWords, s.Scenario.Steps[s.Step].ActionToPerform, s.Scenario.Steps[s.Step].ActionKeyWords)
		return true
	}
	return false

}
