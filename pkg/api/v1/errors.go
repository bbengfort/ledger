package api

import (
	"fmt"
	"net/http"

	"go.bengfort.dev/ledger/pkg/errors"
)

//=============================================================================
// Error Replies
//=============================================================================

var (
	NotFound      = Reply{Success: false, Error: "resource not found"}
	NotAllowed    = Reply{Success: false, Error: "method not allowed"}
	InternalError = Reply{Success: false, Error: "an internal error occurred"}
)

// Error constructs a new reply for an error value.
func Error(status int, err error, msg string) *errors.HTTPError {
	if err == nil {
		return &errors.HTTPError{
			Status: status,
			Err:    errors.ErrUnknown,
			Reply:  Reply{Success: false, Error: errors.ErrUnknown.Error()},
		}
	}

	if msg == "" {
		msg = err.Error()
	}

	herr := &errors.HTTPError{
		Status: status,
		Err:    err,
		Reply:  Reply{Success: false, Error: msg},
	}

	if verr, ok := err.(errors.ValidationErrors); ok {
		herr.Reply = validationReply(verr)
	}

	return herr
}

//=============================================================================
// HTTP Status Errors
//=============================================================================

// StatusError decodes an APIv2 error response.
type StatusError struct {
	StatusCode int
	Reply      Reply
}

// Error returns a string representation of the status error.
func (e *StatusError) Error() string {
	return fmt.Sprintf("[%d] %s", e.StatusCode, e.Reply.Error)
}

// ErrorStatus returns the HTTP status code from an error.
func ErrorStatus(err error) int {
	if err == nil {
		return http.StatusOK
	}

	if e, ok := err.(*StatusError); ok && (e.StatusCode >= 100 && e.StatusCode < 600) {
		return e.StatusCode
	}

	return http.StatusInternalServerError
}

//=============================================================================
// Error Detail
//=============================================================================

// ErrorDetail is a list of per-field validation errors.
type ErrorDetail []*DetailError

// DetailError describes a specific invalid field in a request payload.
type DetailError struct {
	Field string `json:"field"`
	Error string `json:"error"`
}

//=============================================================================
// Helpers
//=============================================================================

// validationReply converts validation errors to a structured error reply.
func validationReply(errs errors.ValidationErrors) Reply {
	rep := Reply{Success: false}
	if len(errs) == 1 {
		rep.Error = errs.Error()
		return rep
	}

	rep.Error = fmt.Sprintf("%d validation errors occurred", len(errs))
	rep.ErrorDetail = make(ErrorDetail, 0, len(errs))
	for _, verr := range errs {
		rep.ErrorDetail = append(rep.ErrorDetail, &DetailError{
			Field: verr.Field(),
			Error: verr.Error(),
		})
	}
	return rep
}
