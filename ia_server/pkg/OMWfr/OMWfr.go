package omwfr

import (
	"TestNLP/pkg/libs"
	"encoding/xml"
	"fmt"
	"os"
)

type OMWfr struct {
	synonyms map[string][]string
	resource LexicalResource
}

func NewOMWfr() *OMWfr {
	resource, err := LoadOMWFR(libs.OmwfrFilePath)
	if err != nil {
		fmt.Printf("Chargement de la base de donnée de synonymes impossible : %s", err)
	}
	return &OMWfr{make(map[string][]string), resource}
}

func LoadOMWFR(filename string) (LexicalResource, error) {
	var resource LexicalResource
	file, err := os.Open(filename)
	if err != nil {
		return resource, err
	}
	defer file.Close()

	decoder := xml.NewDecoder(file)
	err = decoder.Decode(&resource)
	if err != nil {
		return resource, err
	}

	return resource, nil
}

func (o *OMWfr) FindSynonyms(target string) []string {
	syns, found := o.synonyms[target]

	if !found {
		synonyms := make(map[string]bool)

		for _, entry := range o.resource.Lexicon.LexicalEntries {
			if entry.Lemma.WrittenForm == target {

				for _, sense := range entry.Senses {
					for _, otherEntry := range o.resource.Lexicon.LexicalEntries {
						for _, otherSense := range otherEntry.Senses {

							if otherSense.Synset == sense.Synset && otherEntry.Lemma.WrittenForm != target {

								synonyms[otherEntry.Lemma.WrittenForm] = true
							}
						}
					}
				}
			}
		}

		result := make([]string, 0, len(synonyms))
		for synonym := range synonyms {
			result = append(result, synonym)

		}
		return result
	} else {
		return syns
	}

}
