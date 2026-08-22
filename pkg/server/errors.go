package server

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/binding"
	"go.bengfort.dev/ledger/pkg/api/v1"
	"go.bengfort.dev/ledger/pkg/errors"
	"go.bengfort.dev/ledger/pkg/web/scene"
)

// Render the not found error page
func (s *Server) NotFound(c *gin.Context) {
	c.Negotiate(http.StatusNotFound, gin.Negotiate{
		Offered:  []string{binding.MIMEJSON, binding.MIMEHTML},
		HTMLName: "errors/status/404.html",
		HTMLData: scene.New(c).Error(errors.ErrMethodNotFound),
		JSONData: api.NotFound,
	})
}

// Render the not allowed error page
func (s *Server) NotAllowed(c *gin.Context) {
	c.Negotiate(http.StatusMethodNotAllowed, gin.Negotiate{
		Offered:  []string{binding.MIMEJSON, binding.MIMEHTML},
		HTMLName: "errors/status/405.html",
		HTMLData: scene.New(c).Error(errors.ErrMethodNotAllowed),
		JSONData: api.NotAllowed,
	})
}

// Render the internal server error page
func (s *Server) InternalError(c *gin.Context) {
	c.Negotiate(http.StatusInternalServerError, gin.Negotiate{
		Offered:  []string{binding.MIMEJSON, binding.MIMEHTML},
		HTMLName: "errors/status/500.html",
		HTMLData: scene.New(c).Error(nil),
		JSONData: api.InternalError,
	})
}
