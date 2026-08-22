package main

import (
	"context"
	"fmt"
	"os"
	"text/tabwriter"

	"github.com/joho/godotenv"
	"github.com/urfave/cli/v3"

	confire "go.rtnl.ai/confire/usage"

	"go.bengfort.dev/ledger/pkg"
	"go.bengfort.dev/ledger/pkg/config"
	"go.bengfort.dev/ledger/pkg/server"
)

func main() {
	// Load environment variables from .env file
	_ = godotenv.Load()

	app := &cli.Command{
		Name:    "ledger",
		Usage:   "start and manage the ledger server",
		Version: pkg.Version(false),
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name:    "dsn",
				Usage:   "for database operations, use this DSN instead of the configured one",
				Sources: cli.EnvVars("LEDGER_DATABASE_URL"),
			},
		},
		Commands: []*cli.Command{
			{
				Name:     "serve",
				Usage:    "start the ledger server",
				Action:   serve,
				Category: "service",
			},
			{
				Name:     "config",
				Usage:    "print ledger configuration guide",
				Category: "service",
				Action:   usage,
				Flags: []cli.Flag{
					&cli.BoolFlag{
						Name:    "list",
						Aliases: []string{"l"},
						Usage:   "print in list mode instead of table mode",
					},
				},
			},
		},
	}

	if err := app.Run(context.Background(), os.Args); err != nil {
		if ec, ok := err.(cli.ExitCoder); ok {
			os.Exit(ec.ExitCode())
		}
		fmt.Fprintf(os.Stderr, "%v\n", err)
		os.Exit(1)
	}
}

//===========================================================================
// Server commands
//===========================================================================

// serve starts the endeavor HTTP server.
func serve(ctx context.Context, cmd *cli.Command) (err error) {
	var srv *server.Server
	if srv, err = server.New(); err != nil {
		return cli.Exit(err, 1)
	}
	if err = srv.Serve(); err != nil {
		return cli.Exit(err, 1)
	}
	return nil
}

// usage prints the endeavor configuration guide.
func usage(ctx context.Context, cmd *cli.Command) error {
	tabs := tabwriter.NewWriter(os.Stdout, 1, 0, 4, ' ', 0)
	format := confire.DefaultTableFormat
	if cmd.Bool("list") {
		format = confire.DefaultListFormat
	}

	var conf config.Config
	if err := confire.Usagef(config.Prefix, &conf, tabs, format); err != nil {
		return cli.Exit(err, 1)
	}
	tabs.Flush()
	return nil
}
