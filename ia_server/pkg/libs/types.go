package libs

// Données des sessions
type SessionsData struct {
	Sessions map[string]*SessionData `json:"sessions"`
}

// Données de la session à sauvegarder
type SessionData struct {
	Censorship   *CensorshipData `json:"censorship"`
	ID           string          `json:"id"`
	Step         int             `json:"step"`
	ScenarioFile string          `json:"scenarioFile"`
	IdTerrain    string          `json:"idTerrain"`
	IdGoodEnd    string          `json:"idGoodEnd"`
	IdBadEnd     string          `json:"idBadEnd"`
}

// Données de la censure à sauvegarder
type CensorshipData struct {
	BannedWords    []string `json:"banned_words"`
	Corpus         []string `json:"corpus"`
	Actions        []string `json:"actions"`
	ActionKeyWords []string `json:"action_keywords"`
}

type MessageRequest struct {
	Message string `json:"text"`
	Title   string `json:"title"`
	Author  string `json:"author"`
	Parent  string `json:"parent"`
	Session string `json:"session"`
	Side    string `json:"side"`
}

type MessageResponse struct {
	Message         string `json:"text"`
	Title           string `json:"title"`
	Author          string `json:"author"`
	Parent          string `json:"parent"`
	Session         string `json:"session"`
	Side            string `json:"side"`
	IsCensored      bool   `json:"isCensored"`
	TriggerNewEvent bool   `json:"triggerNewEvent"`
	Events          Events `json:"events"`
	TriggerEnd      string `json:"triggerEnd"`
}

type Request interface {
	MessageRequest | NewSessionRequest
}

type NewSessionRequest struct {
	SessionID string    `json:"session"`
	Sides     []SideReq `json:"sides"`
	Ends      []EndReq  `json:"ends"`
}

type NewSessionResponse struct {
	Session string `json:"session"`
}

type SideReq struct {
	Id   string `json:"id"`
	Name string `json:"name"`
}

type EndReq struct {
	Id    string `json:"id"`
	Title string `json:"titles"`
}

type Step struct {
	Events          Events   `json:"events"`
	BannedWords     []string `json:"BannedWords"`
	ActionToPerform []string `json:"ActionToPerform"`
	ActionKeyWords  []string `json:"KeyWords"`
}

type Events struct {
	EventQG      Node `json:"qg"`
	EventTerrain Node `json:"terrain"`
}

type Node struct {
	Titre   string `json:"title"`
	Message string `json:"text"`
	Auteur  string `json:"author"`
}
