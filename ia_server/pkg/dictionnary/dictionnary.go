package dictionnary

import (
	"code.sajari.com/word2vec"
	"github.com/agnivade/levenshtein"
)

type Dictionnary struct {
	Entries       []string
	Word2VecModel *word2vec.Model
}

func NewDictionnary(model *word2vec.Model) *Dictionnary {

	return &Dictionnary{model.Vocab(), model}
}

func (d *Dictionnary) nearest(word string) string {
	nearest := d.Entries[0]
	min_distance := levenshtein.ComputeDistance(word, d.Entries[0])
	for _, entry := range d.Entries {
		distance := levenshtein.ComputeDistance(word, entry)
		if distance < min_distance {
			nearest = entry
			min_distance = distance
		}
	}
	return nearest
}

func (d *Dictionnary) IsInDict(word string) bool {
	res := false
	if word != "" {
		if len(d.Word2VecModel.Map([]string{word})) != 0 {
			res = true
		}
	}
	return res
}

func (d *Dictionnary) AutoCorrect(word string) string {
	if !d.IsInDict(word) {
		return d.nearest(word)
	} else {
		return word
	}
}
