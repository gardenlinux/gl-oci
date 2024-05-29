/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// attachImageCmd represents the attachImage command
var attachImageCmd = &cobra.Command{
	Use:   "attachImage",
	Short: "Attaches an Image to an existing manifest",
	Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("Dummy: manifest attachImage called")
	},
}

func init() {
	manifestCmd.AddCommand(attachImageCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// attachImageCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// attachImageCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
