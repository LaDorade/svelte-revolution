package omwfr

import (
	"encoding/xml"
)

type Sense struct {
	ID     string `xml:"id,attr"`
	Synset string `xml:"synset,attr"`
}

type Lemma struct {
	WrittenForm  string `xml:"writtenForm,attr"`
	PartOfSpeech string `xml:"partOfSpeech,attr"`
}

type LexicalEntry struct {
	ID     string  `xml:"id,attr"`
	Lemma  Lemma   `xml:"Lemma"`
	Senses []Sense `xml:"Sense"`
}

type LexicalResource struct {
	XMLName xml.Name `xml:"LexicalResource"`
	Lexicon Lexicon  `xml:"Lexicon"`
}

type Lexicon struct {
	ID             string         `xml:"id,attr"`
	Label          string         `xml:"label,attr"`
	Lang           string         `xml:"language,attr"`
	LexicalEntries []LexicalEntry `xml:"LexicalEntry"`
}

type Keyword struct {
	Word  string
	Score float64
}
