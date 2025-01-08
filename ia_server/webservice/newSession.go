package webservice

import (
	"TestNLP/pkg/censorship"
	"TestNLP/pkg/libs"
	"encoding/json"
	"fmt"
	"net/http"
)

func (rsa *ServerAgent) DoNewSession(w http.ResponseWriter, r *http.Request) {
	rsa.Lock()
	defer rsa.Unlock()

	// vérification de la méthode de la requête
	if !rsa.checkMethod("POST", w, r) {
		return
	}

	// décodage de la requête
	req, err := decodeRequest[libs.NewSessionRequest](r)

	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprint(w, err.Error())
		return
	}

	_, exists := rsa.Sessions[req.SessionID]

	if exists {
		w.WriteHeader(http.StatusBadRequest)
		msg := "This session already exists."
		w.Write([]byte(msg))
		return
	}

<<<<<<< HEAD
	new_session, err := censorship.NewSession(req, libs.ScenarioFile)
=======
	new_session, err := NewSession(req.Session, scenarioFile)
	rsa.Sessions[req.Session] = *new_session

>>>>>>> parent of 15af0df (IA server)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprint(w, err.Error())
		return
	}

<<<<<<< HEAD
	rsa.Sessions[req.SessionID] = new_session

	//sauvegarder la nouvelle sessions
	rsa.Saver.SaveSessionData(rsa.Sessions)

	var resp libs.NewSessionResponse
	resp.Session = req.SessionID
=======
	var resp NewSessionResponse
	resp.Session = req.Session
>>>>>>> parent of 15af0df (IA server)

	w.WriteHeader(http.StatusOK)
	serial, _ := json.Marshal(resp)
	w.Write(serial)
}
