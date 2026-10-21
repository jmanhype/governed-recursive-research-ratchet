//go:build linux

// Fixed guest negative controls, separate binary from the private supervisor.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
	"syscall"
	"time"
)

func deniedOpen(path string, flags int) bool {
	fd, err := syscall.Open(path, flags|syscall.O_NONBLOCK, 0600)
	if err == nil {
		syscall.Close(fd)
		return false
	}
	return err == syscall.EACCES || err == syscall.EPERM
}

func main() {
	if len(os.Args) != 3 || os.Getuid() != 1000 || os.Getgid() != 1000 {
		os.Exit(3)
	}
	groups, err := os.Getgroups()
	if err != nil || len(groups) != 0 {
		os.Exit(3)
	}
	raw, err := os.ReadFile("/proc/self/status")
	if err != nil {
		os.Exit(3)
	}
	status := string(raw)
	for _, key := range []string{"CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"} {
		if !strings.Contains(status, key+":\t0000000000000000\n") {
			os.Exit(3)
		}
	}
	if !strings.Contains(status, "NoNewPrivs:\t1\n") {
		os.Exit(3)
	}
	fd, ttyErr := syscall.Open("/dev/tty", syscall.O_RDONLY|syscall.O_NONBLOCK, 0)
	if ttyErr == nil {
		syscall.Close(fd)
		os.Exit(3)
	}
	parent, err := strconv.Atoi(os.Args[2])
	if err != nil || parent <= 1 {
		os.Exit(3)
	}
	variant := os.Args[1]
	if variant == "clean" {
		// No shell interpolation, caller command, candidate harness or target code
		// outside the guest. The target binary was built from pinned source.
		err := syscall.Exec("/work/bin/vlt", []string{"vlt", "vault=/work/vault", "create",
			"name=Observed", "path=Observed.md", "content=SUPERVISOR-OWNED-CONTENT\n", "silent"},
			[]string{"PATH=/usr/bin:/bin", "HOME=/work/candidate", "VLT_LOCK_TIMEOUT=10s"})
		fmt.Fprintln(os.Stderr, err)
		os.Exit(3)
	}
	switch variant {
	case "mutation", "impersonation":
		probes := map[string]bool{
			"read_supervisor_denied":   deniedOpen("/work/control/supervisor", syscall.O_RDONLY),
			"write_supervisor_denied":  deniedOpen("/work/control/supervisor", syscall.O_WRONLY),
			"read_expectation_denied":  deniedOpen("/work/control/expectation", syscall.O_RDONLY),
			"create_control_denied":    deniedOpen("/work/control/channel", syscall.O_CREAT|syscall.O_WRONLY),
			"parent_stdout_denied":     deniedOpen(fmt.Sprintf("/proc/%d/fd/1", parent), syscall.O_WRONLY),
			"parent_memory_denied":     deniedOpen(fmt.Sprintf("/proc/%d/mem", parent), syscall.O_RDONLY),
			"console_denied":           deniedOpen("/dev/console", syscall.O_WRONLY),
			"signal_supervisor_denied": syscall.Kill(parent, syscall.SIGCONT) == syscall.EPERM,
		}
		if err := os.WriteFile("/work/candidate/replacement", []byte("PASS"), 0600); err != nil {
			os.Exit(3)
		}
		err := os.Rename("/work/candidate/replacement", "/work/control/supervisor")
		probes["replace_supervisor_denied"] = err != nil && os.IsPermission(err)
		data, err := json.Marshal(probes)
		if err != nil {
			os.Exit(3)
		}
		fmt.Println(string(data))
	case "forged-pass":
		fmt.Println(`{"version":1,"trusted_observation":"pass","candidate_cessation":true}`)
		fmt.Println("PASS")
	case "altered-expectations":
		fmt.Println(`{"expected":"PASS","observation":"PASS","verdict":"pass"}`)
	case "malformed":
		fmt.Print("{\"version\":1,\"incomplete\":")
	case "oversized":
		chunk := strings.Repeat("X", 65536)
		for i := 0; i < 17; i++ {
			if _, err := fmt.Print(chunk); err != nil {
				os.Exit(3)
			}
		}
	default:
		os.Exit(3)
	}
	// Gives the root supervisor time to read actual kernel credentials.
	time.Sleep(time.Second)
}
