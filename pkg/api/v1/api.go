package api

import (
	"time"

	"go.bengfort.dev/ledger/pkg/errors"
	"go.rtnl.ai/ulid"
)

// Reply contains standard fields for generic API replies.
type Reply struct {
	Success     bool        `json:"success"`
	Error       string      `json:"error,omitempty"`
	ErrorDetail ErrorDetail `json:"error_detail,omitempty"`
}

// StatusReply is returned on status requests.
type StatusReply struct {
	Status  string `json:"status"`
	Uptime  string `json:"uptime,omitempty"`
	Version string `json:"version,omitempty"`
}

type DTO struct {
	ID       ulid.ULID `json:"id,omitzero,omitempty"`       // readonly field
	Created  time.Time `json:"created,omitzero,omitempty"`  // readonly field
	Modified time.Time `json:"modified,omitzero,omitempty"` // readonly field
}

func (d *DTO) Validate(method string) (err error) {
	if !d.ID.IsZero() {
		err = errors.ValidationError(err, errors.ReadOnlyField("id"))
	}
	if !d.Created.IsZero() {
		err = errors.ValidationError(err, errors.ReadOnlyField("created"))
	}
	if !d.Modified.IsZero() {
		err = errors.ValidationError(err, errors.ReadOnlyField("modified"))
	}
	return err
}

func (d *DTO) IsZero() bool {
	return d == nil || (d.ID.IsZero() && d.Created.IsZero() && d.Modified.IsZero())
}
