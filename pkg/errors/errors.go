package errors

import (
	"errors"
	"fmt"
)

var (
	// HTTP Server Errors
	ErrMethodNotFound   = errors.New("resource not found")
	ErrMethodNotAllowed = errors.New("method not allowed")

	// Development errors
	ErrUnknown        = errors.New("an unknown error occurred")
	ErrNotImplemented = errors.New("this operation is not implemented")
)

// In is a helper function to check if an error is in a list of errors.
func In(err error, targets ...error) bool {
	for _, target := range targets {
		if errors.Is(err, target) {
			return true
		}
	}
	return false
}

// Reduce namespacing conflicts by adding error functions from the errors package.
var (
	New    = errors.New
	Fmt    = fmt.Errorf
	Is     = errors.Is
	As     = errors.As
	Join   = errors.Join
	Unwrap = errors.Unwrap
)
