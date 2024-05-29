/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// createImageCmd represents the createImage command
var createImageCmd = &cobra.Command{
	Use:   "createImage",
	Short: "Create an OCI Image",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("createImage called")
	},
}

func init() {
	imageCmd.AddCommand(createImageCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// createImageCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// createImageCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
