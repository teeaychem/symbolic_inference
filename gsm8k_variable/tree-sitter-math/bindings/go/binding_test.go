package tree_sitter_math_test

import (
	"testing"

	tree_sitter "github.com/tree-sitter/go-tree-sitter"
	tree_sitter_math "github.com/tree-sitter/tree-sitter-math/bindings/go"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_math.Language())
	if language == nil {
		t.Errorf("Error loading Math grammar")
	}
}
