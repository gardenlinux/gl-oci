/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// annotateManifestCmd represents the annotateManifest command
var annotateManifestCmd = &cobra.Command{
	Use:   "annotateManifest",
	Short: "Add a custom annotation to an OCI manifest",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("annotateManifest called")
	},
}

func init() {
	manifestCmd.AddCommand(annotateManifestCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// annotateManifestCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// annotateManifestCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
