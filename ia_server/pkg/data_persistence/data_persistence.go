package data_persistence

import (
	"TestNLP/pkg/censorship"
	"TestNLP/pkg/libs"
	"encoding/json"
	"fmt"
	"os"
)

type PersistenceHandler struct {
	filePath string
}

func NewPersistenceHandler(filePath string) *PersistenceHandler {
	return &PersistenceHandler{filePath: filePath}
}

// Sauvegarde
func (p *PersistenceHandler) SaveSessionData(data map[string]*censorship.Session) error {
	// Marshal the data into JSON
	jsonData, err := json.MarshalIndent(SaveSessions(data), "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal session data: %w", err)
	}

	// Write JSON data to file
	err = os.WriteFile(p.filePath, jsonData, 0644)
	if err != nil {
		return fmt.Errorf("failed to write session data to file: %w", err)
	}

	return nil
}

// Restauration
func (p *PersistenceHandler) LoadSessionData() (*libs.SessionsData, bool, error) {
	// Si la sauvegarde existe
	if _, err := os.Stat(p.filePath); os.IsNotExist(err) {
		return nil, false, fmt.Errorf("file does not exist: %s", p.filePath)
	}

	// Lire le ficher
	jsonData, err := os.ReadFile(p.filePath)
	if err != nil {
		return nil, true, fmt.Errorf("failed to read session data file: %w", err)
	}

	// Unmarshal le fichier
	var data libs.SessionsData
	err = json.Unmarshal(jsonData, &data)
	if err != nil {
		return nil, true, fmt.Errorf("failed to unmarshal session data: %w", err)
	}

	return &data, true, nil
}

// Suppression
func (p *PersistenceHandler) DeleteSessionData() error {
	// Si le fichier existe
	if _, err := os.Stat(p.filePath); os.IsNotExist(err) {
		return fmt.Errorf("file does not exist: %s", p.filePath)
	}

	// Supprimer le fichier
	err := os.Remove(p.filePath)
	if err != nil {
		return fmt.Errorf("failed to delete session data file: %w", err)
	}

	return nil
}
