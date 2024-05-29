/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

    "encoding/json"
    "io/ioutil"

    ocispecs "github.com/opencontainers/image-spec/specs-go"
)

// createIndexCmd represents the createIndex command
var createIndexCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a fresh OCI Index",
	Run: func(cmd *cobra.Command, args []string) {
        createIndex("index.json")
	},
}

func createIndex(filePath string) error {

    fmt.Println("Dummy: index create called ----")

    ociIndex := ocispecs.v1.Index{
		Versioned: ocispecs.versioned{
			SchemaVersion: 2,
		},
		Manifests: []ocispecs.v1.Descriptor{},
	}
    indexJSON, err := json.Marshal(ociIndex)
    if err != nil {
        return fmt.Errorf("failed to marshal index to JSON: %v", err)
    }

    err = ioutil.WriteFile(filePath, indexJson, 0644)

    if err != nil {
        return fmt.Errorf("failed to write index to file: %v", err)
    }

    return nil
}



func init() {
	indexCmd.AddCommand(createIndexCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// createIndexCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// createIndexCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
