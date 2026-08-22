package errors

// HTTPError is a custom error type that allows us to return an HTTP status code and
// a JSON reply from a function. This is useful for functions that need to indicate
// what to return in a gin handler without having to accept the gin context.
type HTTPError struct {
	Status int   // status code to return to the client
	Err    error // the original error
	Reply  any   // the output of api.Error() --> using any to avoid circular imports
}

func (e *HTTPError) Error() string {
	return e.Err.Error()
}

func (e *HTTPError) Unwrap() error {
	return e.Err
}
