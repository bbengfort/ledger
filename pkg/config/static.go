package config

import (
	"errors"
	"net/url"
	"os"
	"strings"

	"go.rtnl.ai/confire"
)

// StaticConfig specifies the configuration for serving static files.
type StaticConfig struct {
	Serve bool   `default:"true" desc:"if true, static files will be served from the filesystem"`
	Root  string `default:"pkg/web/static" desc:"the root directory for static files"`
	URL   string `default:"/static" desc:"the URL that static files are served from either a relative URL or a URL to a CDN"`
}

func (c StaticConfig) Validate() (err error) {
	if c.Serve {
		if c.Root == "" {
			err = confire.Join(err, confire.Required("static", "root"))
		} else {
			if _, serr := os.Stat(c.Root); errors.Is(serr, os.ErrNotExist) {
				err = confire.Join(err, confire.Invalid("static", "root", "directory does not exist"))
			}
		}
	}

	if c.URL == "" {
		err = confire.Join(err, confire.Required("static", "url"))
	} else {
		if strings.Contains(c.URL, "://") {
			if u, perr := url.Parse(c.URL); perr != nil || u.Scheme == "" || u.Host == "" || u.Path == "" {
				err = confire.Join(err, confire.Invalid("static", "url", "must be a valid URL or an absolute path starting with a slash"))
			}

			if c.Serve {
				err = confire.Join(err, confire.Invalid("static", "url", "cannot use a remote URL if static files are served from the filesystem"))
			}

		} else {
			if !strings.HasPrefix(c.URL, "/") {
				err = confire.Join(err, confire.Invalid("static", "url", "must be a valid URL or an absolute path starting with a slash"))
			}

			if !c.Serve {
				err = confire.Join(err, confire.Invalid("static", "url", "must be a remote url if static files are not served from the filesystem"))
			}
		}
	}

	return err
}
