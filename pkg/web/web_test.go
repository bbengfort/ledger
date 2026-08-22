package web

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestJoin(t *testing.T) {
	tests := []struct {
		values    []string
		separator string
		expected  string
	}{
		{values: []string{}, separator: ",", expected: ""},
		{values: []string{"apple"}, separator: ", ", expected: "apple"},
		{values: []string{"apple", "banana", "cherry"}, separator: ", ", expected: "apple, banana, cherry"},
		{values: []string{"apple", "banana", "cherry"}, separator: "-", expected: "apple-banana-cherry"},
	}
	for i, tc := range tests {
		require.Equal(t, tc.expected, join(tc.values, tc.separator), "unexpected result for test case %d", i)
	}
}
