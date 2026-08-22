package config

import (
	"net"
	"net/url"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"go.rtnl.ai/confire"
	"go.rtnl.ai/x/rlog"
)

// All environment variables will have this prefix unless otherwise defined in struct
// tags. For example, the conf.LogLevel environment variable will be LEDGER_LOG_LEVEL
// because of this prefix and the split_words struct tag in the conf below.
const Prefix = "ledger"

// Config contains all of the configuration parameters for the Ledger server which
// are loaded from the environment and should be validated before use.
type Config struct {
	Maintenance       bool              `default:"false" desc:"if true, the server will start in maintenance mode"`
	Mode              string            `default:"release" desc:"specify the mode of the server (release, debug, testing)"`
	LogLevel          rlog.LevelDecoder `split_words:"true" default:"info" desc:"specify the verbosity of logging (trace, debug, info, warn, error, fatal, or panic)"`
	ConsoleLog        bool              `split_words:"true" default:"false" desc:"if true logs human readable text output instead of json"`
	BindAddr          string            `default:":8000" split_words:"true" desc:"the ip address and port to bind the web server on"`
	Origin            string            `default:"http://localhost:8000" desc:"origin (url) of the web ui for creating endpoints and CORS access"`
	AllowOrigins      []string          `split_words:"true" default:"http://localhost:8000" desc:"a list of allowed origins (domains including port) for CORS requests"`
	DatabaseURL       string            `split_words:"true" default:"postgres://localhost:5432/ledger?sslmode=disable" desc:"dsn containing backend database configuration"`
	ReadHeaderTimeout time.Duration     `split_words:"true" default:"180s" desc:"the maximum duration for reading the request header (see Go's http.Server.ReadHeaderTimeout)"`
	WriteTimeout      time.Duration     `split_words:"true" default:"180s" desc:"the maximum duration for writing the response (see Go's http.Server.WriteTimeout)"`
	IdleTimeout       time.Duration     `split_words:"true" default:"360s" desc:"the maximum duration for idle connections (see Go's http.Server.IdleTimeout)"`
	ShutdownTimeout   time.Duration     `split_words:"true" default:"180s" desc:"the maximum duration for shutting down the server"`
}

// New creates a new Config instance and loads the configuration from the environment,
// validating the configuration and returning an error if the configuration is invalid
// or could not be parsed from environment variables.
//
// NOTE: New should only be used for testing, for module access to the config use Get().
func New() (conf *Config, err error) {
	// NOTE: confire.Process calls Validate() internally.
	conf = &Config{}
	if err = confire.Process(Prefix, conf); err != nil {
		return nil, err
	}
	return conf, nil
}

// Custom validations are added here, particularly validations that require one or more
// fields to be processed before the validation occurs.
// NOTE: This method only validates the config itself and nested configs are
// validated by [Config.Mark].
func (c Config) Validate() (err error) {
	if c.Mode != gin.ReleaseMode && c.Mode != gin.DebugMode && c.Mode != gin.TestMode {
		err = confire.Join(err, confire.Invalid("", "mode", "must be one of: release, debug, test"))
	}

	if c.BindAddr == "" {
		err = confire.Join(err, confire.Required("", "bindAddr"))
	} else {
		if _, _, perr := net.SplitHostPort(c.BindAddr); perr != nil {
			err = confire.Join(err, confire.Invalid("", "bindAddr", "must be a valid host:port address"))
		}
	}

	if c.Origin == "" {
		err = confire.Join(err, confire.Required("", "origin"))
	} else {
		if u, perr := url.Parse(c.Origin); perr != nil || u.Scheme == "" || u.Host == "" || u.Path != "" {
			err = confire.Join(err, confire.Invalid("", "origin", "must be a a complete URL without a trailing slash"))
		}
	}

	return err
}

//============================================================================
// Config Package Management
//============================================================================

var (
	mu   sync.RWMutex
	err  error // only written by New() inside Get's sync.Once, and cleared on successful Set
	load sync.Once
	conf *Config
)

func Get() (Config, error) {
	load.Do(func() {
		mu.Lock()
		defer mu.Unlock()

		if conf == nil {
			conf, err = New()
		}
	})
	mu.RLock()
	defer mu.RUnlock()
	if conf != nil {
		return *conf, err
	}
	return Config{}, err
}

func MustGet() Config {
	conf, err := Get()
	if err != nil {
		panic(err)
	}
	return conf
}

func Set(c Config) error {
	mu.Lock()
	defer mu.Unlock()

	if err = c.Validate(); err != nil {
		return err
	}

	conf = &c
	err = nil

	return nil
}

func Reset() {
	mu.Lock()
	defer mu.Unlock()
	conf = nil
	err = nil
	load = sync.Once{}
}
