package scene

type Error struct {
	Scene
	Error string
}

// Create an error that includes the Scene with the error message.
func (s Scene) Error(err error) *Error {
	e := &Error{
		Scene: s,
	}

	if err != nil {
		e.Error = err.Error()
	}

	return e
}
