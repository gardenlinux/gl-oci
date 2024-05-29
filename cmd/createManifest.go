/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// createManifestCmd represents the createManifest command
var createManifestCmd = &cobra.Command{
	Use:   "createManifest",
	Short: "Create an OCI manifest",
	Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("Dummy: manifest create called")
	},
}

func init() {
	manifestCmd.AddCommand(createManifestCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// createManifestCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// createManifestCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
