package wiktionnaire

import (
	"fmt"
	"net/http"
	"strings"

	"golang.org/x/net/html"
)

type Wiktionnaire struct {
	definitions map[string][]string
}

func NewWiktionnaire() *Wiktionnaire {
	return &Wiktionnaire{make(map[string][]string)}
}

// getDefinitions retourne les definitions d'un mot depuis le Wiktionnaire
func (w *Wiktionnaire) FindDefinitions(word string, n *html.Node) []string {
	var definitions []string

	var traverse func(*html.Node)
	traverse = func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "ol" {
			var olContent strings.Builder

			for c := n.FirstChild; c != nil; c = c.NextSibling {
				if c.Type == html.ElementNode && c.Data == "li" {
					var definitionText string

					// Récupération du contenu des <li>
					for t := c.FirstChild; t != nil; t = t.NextSibling {
						if t.Type == html.TextNode {
							definitionText += strings.TrimSpace(t.Data) + " "
						}
						if t.Type == html.ElementNode && t.Data == "a" {
							for a := t.FirstChild; a != nil; a = a.NextSibling {
								if a.Type == html.TextNode {
									definitionText += strings.TrimSpace(a.Data) + " "
								}
							}
						}
					}

					if len(definitionText) > 0 {
						definitions = append(definitions, strings.TrimSpace(definitionText))
					}
				}
			}

			//ajoute la def
			if olContent.String() != "" {
				definitions = append(definitions, olContent.String())

			}
		}

		// Traverse le reste de l'arborescence
		for c := n.FirstChild; c != nil; c = c.NextSibling {
			traverse(c)
		}
	}

	traverse(n)

	return definitions
}

func (w *Wiktionnaire) fetchHTML(word string) (*html.Node, error) {
	url := fmt.Sprintf("https://fr.wiktionary.org/wiki/%s", word)
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch page: %v", err)
	}
	defer resp.Body.Close()

	doc, err := html.Parse(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to parse HTML: %v", err)
	}

	return doc, nil
}

func (w *Wiktionnaire) GetDefinitions(word string) ([]string, error) {

	defs, ok := w.definitions[word]

	//la definition n'est pas dans les def sauvegardées
	if !ok {
		doc, err := w.fetchHTML(word)
		if err != nil {
			return nil, err
		}

		defs = w.FindDefinitions(word, doc)

		//sauvegarde de la def
		w.definitions[word] = defs
	}

	return defs, nil
}
