package web

import (
	"context"
	"embed"
	"fmt"
	"html/template"
	"io/fs"
	"log/slog"
	"net/url"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin/render"
	"go.bengfort.dev/ledger/pkg/config"
	"go.rtnl.ai/x/humanize"
	"go.rtnl.ai/x/rlog"
	"golang.org/x/text/cases"
	"golang.org/x/text/language"
)

//go:embed all:templates
var content embed.FS

var (
	includes = []string{"*.html", "components/*.html", "components/*/*.html"}
)

// Template returns a FileSystem that contains the HTML templates.
func Templates() fs.FS {
	var (
		templateFiles fs.FS
		err           error
	)
	if templateFiles, err = fs.Sub(content, "templates"); err != nil {
		panic(fmt.Errorf("failed to create template file system: %w", err))
	}
	return templateFiles
}

// Creates a new template renderer from the default templates.
// The required templates will be specified by its path relative to the templates directory.
func NewRender(fsys fs.FS) (render *Render, err error) {
	render = &Render{
		templates: make(map[string]*template.Template),
	}

	var entries []fs.DirEntry
	if entries, err = fs.ReadDir(fsys, "."); err != nil {
		return nil, err
	}

	for _, entry := range entries {
		name := entry.Name()

		// Create includes pattern for the layout.
		patterns := []string{
			fmt.Sprintf("%s/*.html", name),
			fmt.Sprintf("%s/*/*.html", name),
			fmt.Sprintf("%s/*/*/*.html", name),
			fmt.Sprintf("%s/*/*/*/*.html", name),
		}

		// Specify patterns to be included for component, partial, and form templates.
		resourcePatterns := []string{
			// Components
			"%s/components/*.html",
			"%s/components/*/*.html",
			"%s/*/components/*.html",
			"%s/*/components/*/*.html",
			// Forms
			"%s/forms/*.html",
			"%s/*/forms/*.html",
			"%s/*/forms/*/*.html",
			// Partials
			"%s/*/partials/*.html",
			"%s/*/partials/*/*.html",
		}

		patternInclude := make([]string, 0, len(includes)+len(resourcePatterns)+1)
		patternInclude = append(patternInclude, includes...)

		// Helper to conditionally append a pattern if it exists.
		appendGlob := func(pattern string) {
			if globExists(fsys, pattern) {
				patternInclude = append(patternInclude, pattern)
			}
		}

		for _, patternFormat := range resourcePatterns {
			appendGlob(fmt.Sprintf(patternFormat, name))
		}

		// Ensure current layout is last in the template list.
		patternInclude = append(patternInclude, fmt.Sprintf("%s/*.html", name))

		// Add templates to the renderer.
		for _, pattern := range patterns {
			if err = render.AddPattern(fsys, pattern, patternInclude...); err != nil {
				return nil, err
			}
		}
	}

	return render, nil
}

func globExists(fsys fs.FS, pattern string) (exists bool) {
	names, _ := fs.Glob(fsys, pattern)
	return len(names) > 0
}

// Implements the render.HTMLRender interface for gin.
type Render struct {
	templates map[string]*template.Template
	funcs     template.FuncMap
}

var _ render.HTMLRender = &Render{}

func (r *Render) Instance(name string, data any) render.Render {
	return &render.HTML{
		Template: r.templates[name],
		Name:     filepath.Base(name),
		Data:     data,
	}
}

func (r *Render) AddPattern(fsys fs.FS, pattern string, includes ...string) (err error) {
	var names []string
	if names, err = fs.Glob(fsys, pattern); err != nil {
		return err
	}

	for _, name := range names {
		patterns := make([]string, 0, len(includes)+1)
		patterns = append(patterns, includes...)
		patterns = append(patterns, name)

		t := template.New(name).Funcs(r.FuncMap())
		if r.templates[name], err = t.ParseFS(fsys, patterns...); err != nil {
			return err
		}

		rlog.TraceAttrs(context.Background(), "parsed template",
			slog.String("template", name),
			slog.Any("patterns", patterns),
		)
	}
	return nil
}

// Create functions available to templates.
func (r *Render) FuncMap() template.FuncMap {
	if r.funcs == nil {
		r.funcs = template.FuncMap{
			"datetime":  datetime,
			"isNil":     isNil,
			"join":      join,
			"lowercase": lowercase,
			"moment":    humanize.Time,
			"static":    static(),
			"titlecase": titlecase,
			"truncate":  truncate,
			"uppercase": uppercase,
		}
	}
	return r.funcs
}

// ===========================================================================
// String Helpers
// ===========================================================================

func titlecase(s string) string {
	title := cases.Title(language.English)
	return title.String(s)
}

func lowercase(s string) string {
	return strings.ToLower(s)
}

func uppercase(s string) string {
	return strings.ToUpper(s)
}

func truncate(s string, n int) string {
	if len(s) > n {
		return s[:n] + "..."
	}
	return s
}

func datetime(t time.Time) string {
	return t.Format("January 2, 2006 3:04 PM")
}

func isNil(v any) bool {
	return v == nil
}

// Join a slice of strings with a separator.
func join(s []string, separator string) string {
	switch len(s) {
	case 0:
		return ""
	case 1:
		return s[0]
	default:
		return strings.Join(s, separator)
	}
}

// Return the static path for a given asset.
func static() func(path string) string {
	// Load the configuration to determine if static files are served from the
	// filesystem or via a CDN. This will allow us to collect static files.
	conf := config.MustGet()
	if !conf.Static.Serve {
		baseURL, _ := url.Parse(conf.Static.URL)
		return func(path string) string {
			// Trim leading slash from the path to ensure it is relative to base URL.
			path = strings.TrimPrefix(path, "/")
			return baseURL.JoinPath(path).String()
		}
	}

	prefix := conf.Static.URL
	return func(path string) string {
		path = strings.TrimPrefix(path, "/")
		return prefix + "/" + path
	}
}
