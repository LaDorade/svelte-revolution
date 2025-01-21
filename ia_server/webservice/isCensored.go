package webservice

import (
	"TestNLP/pkg/libs"
	"encoding/json"
	"fmt"
	"net/http"
)

func (rsa *ServerAgent) DoIsCensored(w http.ResponseWriter, r *http.Request) {
	// mise à jour du nombre de requêtes
	rsa.Lock()
	defer rsa.Unlock()

	// vérification de la méthode de la requête
	if !rsa.checkMethod("POST", w, r) {
		return
	}

	// décodage de la requête
	req, err := decodeRequest[libs.MessageRequest](r)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprint(w, err.Error())
		return
	}

	//récupration de la session
	session, ok := rsa.Sessions[req.Session]

	if !ok {
		w.WriteHeader(http.StatusConflict)
		msg := "The session " + req.Session + " doesn't exists. Please create a session first"
		fmt.Println(msg)
		w.Write([]byte(msg))
		return
	}

	censor := session.Censorship

	//ajout du message au corpus
	censor.Corpus = append(censor.Corpus, req.Message)

	// traitement de la requête
	var resp libs.MessageResponse = libs.MessageResponse{
		Message:         req.Message,
		Title:           req.Title,
		Author:          req.Author,
		Parent:          req.Parent,
		Session:         req.Session,
		Side:            req.Side,
		IsCensored:      false,
		TriggerNewEvent: false,
		Events:          libs.Events{},
		TriggerEnd:      ""}

	fmt.Println(req.Side)
	fmt.Println(session.IdTerrain)
	//if req.Side == session.IdTerrain {
	is_message_performative := censor.IsActionPerformed(req.Title)

	if is_message_performative || session.Step == 0 {
		//déclencer evt
		fmt.Println("triggered")
		resp.TriggerNewEvent = true

		next := session.NextStep()

		if next {
			resp.Events = session.Scenario.Steps[session.Step].Events

			//Sauvegarde de l'état de la session
			rsa.Saver.SaveSessionData(rsa.Sessions)
		} else {
			resp.TriggerEnd = session.IdGoodEnd
		}
	}

	//}
	if !resp.TriggerNewEvent {
		is_message_censored, censored_message, err := censor.CensordMessage(req.Message)
		is_title_censored, censored_title, err1 := censor.CensordMessage(req.Title)

		resp.IsCensored = (is_message_censored || is_title_censored)
		resp.Title = censored_title
		resp.Message = censored_message

		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			msg := fmt.Sprintf("An error occured : '%s'.", err.Error())
			w.Write([]byte(msg))
			return
		}

		if err1 != nil {
			w.WriteHeader(http.StatusInternalServerError)
			msg := fmt.Sprintf("An error occured : '%s'.", err1.Error())
			w.Write([]byte(msg))
			return
		}

	}

	w.WriteHeader(http.StatusOK)
	serial, _ := json.Marshal(resp)
	w.Write(serial)
}
