package webservice

import (
	"TestNLP/pkg/censorship"
	"TestNLP/pkg/data_persistence"
	"TestNLP/pkg/libs"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

type ServerAgent struct {
	sync.Mutex
	id       string
	addr     string
	Sessions map[string]*censorship.Session
	Saver    *data_persistence.PersistenceHandler
}

func NewServerAgent(addr string) *ServerAgent {
	saver := data_persistence.NewPersistenceHandler("data.json")
	sessionsData, ok, err := saver.LoadSessionData()

	//si une sauvegarde existe, la charger
	if ok {
		sessions, err := data_persistence.LoadSessions(sessionsData)
		if err != nil {
			fmt.Println("[Warning] Impossible de charger les données de sauvegarde :", err)
		}
		return &ServerAgent{sync.Mutex{}, addr, addr, sessions, saver}
	} else {
		if err != nil {
			fmt.Println("[Warning] Fichier de sauvegarde inexistant", err)
		}
		return &ServerAgent{sync.Mutex{}, addr, addr, map[string]*censorship.Session{}, saver}
	}

}

// Test de la méthode
func (rsa *ServerAgent) checkMethod(method string, w http.ResponseWriter, r *http.Request) bool {
	if r.Method != method {
		w.WriteHeader(http.StatusMethodNotAllowed)
		fmt.Fprintf(w, "method %q not allowed", r.Method)
		return false
	}
	return true
}

// do a decoderequest factory
func decodeRequest[Req libs.Request](r *http.Request) (req Req, err error) {
	buf := new(bytes.Buffer)
	buf.ReadFrom(r.Body)
	err = json.Unmarshal(buf.Bytes(), &req)
	return
}

func (rsa *ServerAgent) Start() {
	// création du multiplexer
	mux := http.NewServeMux()
	mux.HandleFunc("POST /api/checkMsg", rsa.DoIsCensored)
	mux.HandleFunc("POST /api/newSession", rsa.DoNewSession)
	mux.HandleFunc("GET /api/health", rsa.Health)

	// création du serveur http
	server := &http.Server{
		Addr:           rsa.addr,
		Handler:        mux,
		ReadTimeout:    10 * time.Second,
		WriteTimeout:   10 * time.Second,
		MaxHeaderBytes: 1 << 20}

	// lancement du serveur
	log.Println("IA_Server running on http://localhost" + rsa.addr)
	go log.Fatal(server.ListenAndServe())
}

func (rsa *ServerAgent) Health(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
}
