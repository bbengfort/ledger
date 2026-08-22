package errors

import (
	"fmt"
	"strings"
)

//=============================================================================
// Field Error Types
//=============================================================================

// FieldError represents a single validation issue for one field.
type FieldError struct {
	verb  string
	field string
	issue string
}

//=============================================================================
// Field Error Methods
//=============================================================================

// Error returns the rendered field error string.
func (e *FieldError) Error() string {
	return fmt.Sprintf("%s %s: %s", e.verb, e.field, e.issue)
}

// Field returns the field path associated with the error.
func (e *FieldError) Field() string {
	return e.field
}

func (e *FieldError) Equal(o *FieldError) bool {
	return e.verb == o.verb && e.field == o.field && e.issue == o.issue
}

// Subfield prefixes the current field name with a parent field.
func (e *FieldError) Subfield(parent string) *FieldError {
	e.field = fmt.Sprintf("%s.%s", parent, e.field)
	return e
}

// SubfieldArray prefixes the field name with a parent array element path.
func (e *FieldError) SubfieldArray(parent string, index int) *FieldError {
	e.field = fmt.Sprintf("%s[%d].%s", parent, index, e.field)
	return e
}

//=============================================================================
// Field Error Constructors
//=============================================================================

// MissingField returns a field error indicating a required field is absent.
func MissingField(field string) *FieldError {
	return &FieldError{verb: "missing", field: field, issue: "this field is required"}
}

// IncorrectField returns a field error indicating the value is invalid.
func IncorrectField(field, issue string) *FieldError {
	return &FieldError{verb: "invalid field", field: field, issue: issue}
}

// IncorrectFieldAtIndex returns a field error for an indexed collection element.
func IncorrectFieldAtIndex(field string, index int, issue string) *FieldError {
	return &FieldError{verb: "invalid field", field: fmt.Sprintf("%s[%d]", field, index), issue: issue}
}

// ReadOnlyField returns a field error indicating the field cannot be user-written.
func ReadOnlyField(field string) *FieldError {
	return &FieldError{verb: "read-only field", field: field, issue: "this field cannot be written by the user"}
}

// DuplicateField returns a field error for values that must be unique.
func DuplicateField(field, value string) *FieldError {
	return &FieldError{verb: "duplicate field", field: field, issue: fmt.Sprintf("the value '%s' is already present for this field", value)}
}

// OneOfMissing returns a field error indicating one of the fields is required.
func OneOfMissing(fields ...string) *FieldError {
	var fieldstr string
	switch len(fields) {
	case 0:
		panic("no fields specified for one of")
	case 1:
		return MissingField(fields[0])
	default:
		fieldstr = fieldList(fields...)
	}

	return &FieldError{verb: "missing one of", field: fieldstr, issue: "at most one of these fields is required"}
}

// OneOfTooMany returns a field error indicating only one field can be set.
func OneOfTooMany(fields ...string) *FieldError {
	if len(fields) < 2 {
		panic("must specify at least two fields for one of too many")
	}

	return &FieldError{verb: "specify only one of", field: fieldList(fields...), issue: "at most one of these fields may be specified"}
}

//=============================================================================
// Validation Error Types
//=============================================================================

// ValidationErrors aggregates field-level validation issues.
type ValidationErrors []*FieldError

//=============================================================================
// Validation Error Methods
//=============================================================================

// Prefix prepends a path segment to every validation field name.
func (e ValidationErrors) Prefix(prefix string) ValidationErrors {
	if prefix == "" {
		return e
	}

	for _, err := range e {
		err.field = fmt.Sprintf("%s.%s", prefix, err.field)
	}
	return e
}

// Error renders all validation errors as one string.
func (e ValidationErrors) Error() string {
	if len(e) == 1 {
		return e[0].Error()
	}

	errs := make([]string, 0, len(e))
	for _, err := range e {
		errs = append(errs, err.Error())
	}

	return fmt.Sprintf("%d validation errors occurred:\n  %s", len(e), strings.Join(errs, "\n  "))
}

// Map converts validation errors to a map of field path to error string.
func (e ValidationErrors) Map() map[string]string {
	errs := make(map[string]string, len(e))
	for _, err := range e {
		errs[err.field] = err.Error()
	}
	return errs
}

//=============================================================================
// Validation Error Constructors
//=============================================================================

// ValidationError appends field validation errors into a single error chain.
func ValidationError(err error, errs ...*FieldError) error {
	var verr ValidationErrors
	if err == nil {
		verr = make(ValidationErrors, 0, len(errs))
	} else {
		var ok bool
		if verr, ok = err.(ValidationErrors); !ok {
			verr = make(ValidationErrors, 0, len(errs)+1)
			verr = append(verr, &FieldError{verb: "invalid", field: "input", issue: err.Error()})
		}
	}

	for _, e := range errs {
		if e != nil {
			verr = append(verr, e)
		}
	}

	if len(verr) == 0 {
		return nil
	}

	return verr
}

// If you have a child field that returns validation errors, then this method will join
// the child errors into a single validation error for the parent field. It will also
// ensure that the errors are prefixed with the chield field's name. E.g. if the child
// fields are "name" and "description", then the errors will be "child.name" and
// "child.description", there is no need for the child to know what the parent field is.
func SubfieldValidationError(err, suberr error, field string) error {
	// If no suberr occurred then do not modify the parent error.
	if suberr == nil {
		return err
	}

	// Check the type of the suberr
	switch child := suberr.(type) {
	case *FieldError:
		// Convert the field error to a subfield error and append to the validation errors.
		return ValidationError(err, child.Subfield(field))
	case ValidationErrors:
		// Convert all of the field errors to subfield errors and append to the validation errors.
		for _, fieldError := range child {
			err = ValidationError(err, fieldError.Subfield(field))
		}
		return err
	default:
		// Otherwise this is simply an incorrect field
		return ValidationError(err, IncorrectField(field, suberr.Error()))
	}

}

//=============================================================================
// Validation Helpers
//=============================================================================

// fieldList joins field names for one-of style validation messages.
func fieldList(fields ...string) string {
	switch len(fields) {
	case 0:
		return ""
	case 1:
		return fields[0]
	case 2:
		return fmt.Sprintf("%s or %s", fields[0], fields[1])
	default:
		last := len(fields) - 1
		return fmt.Sprintf("%s, or %s", strings.Join(fields[0:last], ", "), fields[last])
	}
}
