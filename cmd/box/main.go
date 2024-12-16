package main

import (
	"fmt"
	"log"
	"os"

	"github.com/unkaktus/box"
	"github.com/urfave/cli/v2"
)

var (
	version string
)

func main() {
	app := &cli.App{
		Name:     "box",
		HelpName: "box",
		Usage:    "Package and extract box files",
		Authors: []*cli.Author{
			{
				Name:  "Ivan Markin",
				Email: "git@unkaktus.art",
			},
		},
		Version: version,
		Commands: []*cli.Command{
			{
				Name:  "append",
				Usage: "append files into a box (box append destination.box [file1 file2 ...])",
				Action: func(cCtx *cli.Context) error {
					destFilename := cCtx.Args().First()
					filenames := cCtx.Args().Tail()
					if len(filenames) == 0 {
						return fmt.Errorf("the source files are not specified")
					}
					return box.Append(destFilename, filenames)
				},
			},
			{
				Name:  "extract",
				Usage: "extract files from a box file (box extract source.box destination_directory)",
				Action: func(cCtx *cli.Context) error {
					filename := cCtx.Args().First()
					if len(cCtx.Args().Tail()) == 0 {
						return fmt.Errorf("destination is not specified")
					}
					destFilename := cCtx.Args().Tail()[0]
					return box.Extract(destFilename, filename)
				},
			},
		},
	}

	if err := app.Run(os.Args); err != nil {
		log.Fatal((err))
	}

}
