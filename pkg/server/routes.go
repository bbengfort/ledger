package server

import (
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"go.bengfort.dev/ledger/pkg"
	"go.rtnl.ai/gimlet/logger"
)

// Sets up the server's middleware and routes.
func (s *Server) setupRoutes() (err error) {
	// Application Middleware
	// NOTE: ordering is important to how middleware is handled
	middlewares := []gin.HandlerFunc{
		// Panic recovery middleware
		gin.Recovery(),

		// Optional logging middleware
		logger.Logger(pkg.ServiceName, pkg.Version(false)),

		// Return unavailable if the server is in maintenance mode
		s.Maintenance(),

		// CORS configuration allows the front-end to make cross-origin requests
		cors.New(s.conf.CORS()),
	}

	// Kubernetes liveness probes added before middleware.
	s.router.GET("/healthz", gin.WrapF(s.Healthz))
	s.router.GET("/livez", gin.WrapF(s.Healthz))
	s.router.GET("/readyz", gin.WrapF(s.Readyz))

	// Add the middleware to the router
	for _, middleware := range middlewares {
		if middleware != nil {
			s.router.Use(middleware)
		}
	}

	v1o := s.router.Group("/v1")
	{
		v1o.GET("/status", s.Status)
	}

	return nil
}
