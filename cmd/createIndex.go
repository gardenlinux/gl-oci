/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// createIndexCmd represents the createIndex command
var createIndexCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a fresh OCI Index",
	Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("Dummy: index create called")
	},
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
