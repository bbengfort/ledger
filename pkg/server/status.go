package server

import (
	"log/slog"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/binding"
	"go.bengfort.dev/ledger/pkg"
	"go.rtnl.ai/gimlet/logger"
	"go.rtnl.ai/x/api"
)

const (
	serverStatusOK          = "ok"
	serverStatusNotReady    = "not ready"
	serverStatusUnhealthy   = "unhealthy"
	serverStatusMaintenance = "maintenance"
)

// Status returns the status of the server.
func (s *Server) Status(c *gin.Context) {
	// Reduce logging verbosity for the status endpoint
	c.Set(logger.LogLevelKey, slog.LevelDebug)

	healthy := s.IsHealthy()
	ready := s.IsReady()

	var state string
	switch {
	case healthy && ready:
		state = serverStatusOK
	case healthy && !ready:
		state = serverStatusNotReady
	case !healthy:
		state = serverStatusUnhealthy
	}

	c.JSON(http.StatusOK, &api.StatusReply{
		Status:  state,
		Version: pkg.Version(false),
		Uptime:  time.Since(s.started).String(),
	})
}

// If the server is in maintenance mode, aborts the current request and renders the
// maintenance mode page instead. Returns nil if not in maintenance mode.
func (s *Server) Maintenance() gin.HandlerFunc {
	if s.conf.Maintenance {
		return func(c *gin.Context) {
			c.Negotiate(http.StatusServiceUnavailable, gin.Negotiate{
				Offered: []string{binding.MIMEJSON, binding.MIMEHTML},
				Data: &api.StatusReply{
					Status:  serverStatusMaintenance,
					Version: pkg.Version(false),
					Uptime:  time.Since(s.started).String(),
				},
				HTMLName: "errors/maintenance/index.html",
			})
			c.Abort()
		}
	}
	return func(c *gin.Context) { c.Next() }
}
