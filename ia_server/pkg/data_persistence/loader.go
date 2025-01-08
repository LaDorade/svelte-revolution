package data_persistence

import (
	"TestNLP/pkg/censorship"
	"TestNLP/pkg/libs"
)

func LoadSessions(data *libs.SessionsData) (map[string]*censorship.Session, error) {
	res := make(map[string]*censorship.Session)
	for _, sd := range data.Sessions {
		s, err := censorship.LoadSession(*sd)
		if err != nil {
			return nil, err
		}
		res[sd.ID] = s
	}
	return res, nil
}

func SaveSessions(data map[string]*censorship.Session) *libs.SessionsData {
	sessionMap := make(map[string]*libs.SessionData)
	for _, s := range data {
		censor := libs.CensorshipData{
			BannedWords:    s.Censorship.BannedWords,
			Corpus:         s.Censorship.Corpus,
			Actions:        s.Censorship.Actions,
			ActionKeyWords: s.Censorship.ActionKeyWords,
		}
		session := libs.SessionData{
			Censorship:   &censor,
			ID:           s.Id,
			Step:         s.Step,
			ScenarioFile: s.ScenarioFile,
			IdTerrain:    s.IdTerrain,
			IdGoodEnd:    s.IdGoodEnd,
			IdBadEnd:     s.IdBadEnd,
		}
		sessionMap[s.Id] = &session
	}
	res := libs.SessionsData{Sessions: sessionMap}

	return &res
}
