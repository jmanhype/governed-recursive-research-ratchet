//go:build linux

package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strconv"
)

const repetitions = 3

type repetition struct {
	Exit int    `json:"exit"`
	Hash string `json:"output_sha256"`
}

type observation struct {
	Version      int          `json:"version"`
	Challenge    string       `json:"challenge"`
	Test         string       `json:"test"`
	BuildExit    int          `json:"build_exit"`
	BuildSHA256  string       `json:"build_output_sha256"`
	BuildOutput  []byte       `json:"build_output"`
	Repetitions  []repetition `json:"repetitions"`
	InternalBug  bool         `json:"internal_error"`
}

func digest(raw []byte) string { sum := sha256.Sum256(raw); return hex.EncodeToString(sum[:]) }

func bounded(raw []byte) []byte { if len(raw) > 16384 { return raw[:16384] }; return raw }

func main() {
	if len(os.Args) != 3 || os.Getuid() != 1000 || os.Getgid() != 1000 { os.Exit(3) }
	parent, err := strconv.Atoi(os.Args[2])
	if err != nil || parent <= 1 { os.Exit(3) }
	challenge := os.Args[1]
	if len(challenge) != 4 || challenge[0] != 'D' && challenge[0] != 'C' { os.Exit(3) }
	for _, character := range challenge[1:] { if character < '0' || character > '9' { os.Exit(3) } }
	source, err := os.Getwd()
	if err != nil { os.Exit(3) }
	environment := append(os.Environ(), "GOCACHE=/work/candidate/cache", "GOPATH=/work/candidate/gopath",
		"GOTMPDIR=/work/candidate/tmp", "GOFLAGS=-mod=readonly")
	build := exec.Command("/work/go/bin/go", "test", "-c", "-o", "/work/candidate/probe", ".")
	build.Dir = source
	build.Env = environment
	buildRaw, buildErr := build.CombinedOutput()
	result := observation{Version: 1, Challenge: challenge, Test: "TestGRRR" + challenge,
		BuildExit: 0, BuildSHA256: digest(bounded(buildRaw)), BuildOutput: bounded(buildRaw)}
	if buildErr != nil {
		if exitError, ok := buildErr.(*exec.ExitError); ok {
			result.BuildExit = exitError.ExitCode()
		} else {
			result.InternalBug = true
		}
	}
	for number := 0; number < repetitions; number++ {
		if result.BuildExit != 0 {
			result.Repetitions = append(result.Repetitions, repetition{Exit: result.BuildExit, Hash: result.BuildSHA256})
			continue
		}
		probe := exec.Command("/work/candidate/probe", "-test.run", "^"+result.Test+"$", "-test.v=false")
		probe.Dir = "/work/candidate"
		probe.Env = environment
		raw, err := probe.CombinedOutput()
		item := repetition{Exit: 0, Hash: digest(bounded(raw))}
		if err != nil {
			if exitError, ok := err.(*exec.ExitError); ok { item.Exit = exitError.ExitCode() } else { result.InternalBug = true }
		}
		result.Repetitions = append(result.Repetitions, item)
	}
	encoded, err := json.Marshal(result)
	if err != nil || result.InternalBug || len(encoded) > 524288 { fmt.Fprintln(os.Stderr, "observation invalid"); os.Exit(3) }
	fmt.Println(string(encoded))
}
