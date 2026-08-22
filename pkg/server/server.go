package server

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"go.bengfort.dev/ledger/pkg"
	"go.bengfort.dev/ledger/pkg/config"
	"go.rtnl.ai/x/probez"
	"go.rtnl.ai/x/rlog"
)

type Server struct {
	sync.RWMutex
	probez.Handler
	url     *url.URL
	srv     *http.Server
	conf    config.Config
	errc    chan error
	router  *gin.Engine
	started time.Time
}

func New() (s *Server, err error) {
	// Create a new server instance
	s = &Server{errc: make(chan error, 1)}

	// Load the configuration from the environment
	if s.conf, err = config.Get(); err != nil {
		return nil, err
	}

	// Create a new router
	gin.SetMode(s.conf.Mode)
	s.router = gin.New()
	s.router.RedirectTrailingSlash = true
	s.router.RedirectFixedPath = false
	s.router.HandleMethodNotAllowed = true
	s.router.ForwardedByClientIP = true
	s.router.UseRawPath = false
	s.router.UnescapePathValues = true

	if err = s.setupRoutes(); err != nil {
		return nil, err
	}

	// Create the http server
	s.srv = &http.Server{
		Addr:              s.conf.BindAddr,
		Handler:           s.router,
		ErrorLog:          nil,
		ReadHeaderTimeout: s.conf.ReadHeaderTimeout,
		WriteTimeout:      s.conf.WriteTimeout,
		IdleTimeout:       s.conf.IdleTimeout,
	}

	return s, nil
}

func (s *Server) Serve() (err error) {
	// Catch OS signals for graceful shutdowns
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-quit
		s.errc <- s.Shutdown()
	}()

	// After rlog.Fatal, run graceful shutdown then exit.
	// NOTE: this is done after the server is fully initialized.
	rlog.SetFatalHook(func() {
		if err := s.Shutdown(); err != nil {
			rlog.ErrorAttrs(context.Background(), "error(s) during fatal shutdown of endeavor server", slog.Any("err", err))
		}
		os.Exit(1)
	})

	// Create a socket to listen on and infer the final URL.
	// NOTE: if the bindaddr is 127.0.0.1:0 for testing, a random port will be assigned,
	// manually creating the listener will allow us to determine which port.
	// When we start listening all incoming requests will be buffered until the server
	// actually starts up in its own go routine below.
	var sock net.Listener
	if sock, err = net.Listen("tcp", s.srv.Addr); err != nil {
		return fmt.Errorf("could not listen on bind addr %s: %s", s.srv.Addr, err)
	}

	// At this point the server is live and healthy, but is not ready.
	s.setURL(sock.Addr())
	s.started = time.Now()
	s.Healthy()

	// Listen for HTTP requests and handle them (liveness requests in particular)
	go func() {
		// Make sure we don't use the external err to avoid data races.
		if serr := s.serve(sock); !errors.Is(serr, http.ErrServerClosed) {
			s.errc <- serr
		}
	}()

	// Now the server is live and ready
	s.Ready()

	rlog.InfoAttrs(context.Background(), "ledger server started",
		slog.String("url", s.URL().String()),
		slog.Bool("maintenance", s.conf.Maintenance),
		slog.String("version", pkg.Version(false)),
	)
	return <-s.errc
}

// ServeTLS if a tls configuration is provided, otherwise Serve.
func (s *Server) serve(sock net.Listener) error {
	if s.srv.TLSConfig != nil {
		return s.srv.ServeTLS(sock, "", "")
	}
	return s.srv.Serve(sock)
}

func (s *Server) Shutdown() (err error) {
	rlog.Info("gracefully shutting down the ledger server")
	s.NotReady()
	defer s.Unhealthy()

	ctx, cancel := context.WithTimeout(context.Background(), s.conf.ShutdownTimeout)
	defer cancel()

	// Shut down the server
	s.srv.SetKeepAlivesEnabled(false)
	if serr := s.srv.Shutdown(ctx); serr != nil {
		err = errors.Join(err, fmt.Errorf("could not shutdown the server: %w", serr))
	}

	// log the shutdown just before we shutdown telemetry
	rlog.DebugAttrs(context.Background(), "endeavor server shutdown", slog.Any("err", err))

	return err
}

// URL returns the endpoint of the server as determined by the configuration and the
// socket address and port (if specified).
func (s *Server) URL() *url.URL {
	s.RLock()
	defer s.RUnlock()
	u := *s.url
	return &u
}

func (s *Server) setURL(addr net.Addr) {
	s.Lock()
	defer s.Unlock()

	s.url = &url.URL{
		Scheme: "http",
		Host:   addr.String(),
	}

	if s.srv.TLSConfig != nil {
		s.url.Scheme = "https"
	}

	if tcp, ok := addr.(*net.TCPAddr); ok && tcp.IP.IsUnspecified() {
		s.url.Host = fmt.Sprintf("127.0.0.1:%d", tcp.Port)
	}
}
