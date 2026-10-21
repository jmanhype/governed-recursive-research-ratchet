//go:build linux

// Guest-only trusted supervisor. Never imports or executes candidate host code.
package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"
)

const control = "/work/control"
const vault = "/work/vault"
const expected = "SUPERVISOR-OWNED-CONTENT\n"

type capture struct {
	mu       sync.Mutex
	data     []byte
	exceeded bool
}

func (c *capture) Write(p []byte) (int, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	left := 512*1024 - len(c.data)
	if len(p) > left {
		c.exceeded = true
		c.data = append(c.data, p[:left]...)
		return len(p), errors.New("candidate output exceeded cap")
	}
	c.data = append(c.data, p...)
	return len(p), nil
}

func privateFile(path string) error {
	info, err := os.Lstat(path)
	if err != nil {
		return err
	}
	st, ok := info.Sys().(*syscall.Stat_t)
	if !ok || !info.Mode().IsRegular() || st.Uid != 0 || info.Mode().Perm()&0077 != 0 || st.Nlink != 1 {
		return errors.New("supervisor artifact is not private root-owned regular file")
	}
	return nil
}

func hashFile(path string) (string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	value := sha256.Sum256(data)
	return hex.EncodeToString(value[:]), nil
}

func prctl(option, value uintptr) error {
	_, _, errno := syscall.RawSyscall6(syscall.SYS_PRCTL, option, value, 0, 0, 0, 0)
	if errno != 0 {
		return errno
	}
	return nil
}

// restrictThread applies to the locked launching thread and is inherited on fork.
// Dropping the bounding set does not strip the supervisor's current effective
// capabilities; credential drop strips all child effective/permitted capabilities.
func restrictThread() error {
	if err := prctl(38, 1); err != nil { // PR_SET_NO_NEW_PRIVS
		return err
	}
	for capability := uintptr(0); capability < 64; capability++ {
		if err := prctl(24, capability); err != nil && err != syscall.EINVAL { // PR_CAPBSET_DROP
			return err
		}
	}
	return nil
}

func credentials(pid int) (map[string]string, error) {
	data, err := os.ReadFile(fmt.Sprintf("/proc/%d/status", pid))
	if err != nil {
		return nil, err
	}
	status := map[string]string{}
	for _, line := range strings.Split(string(data), "\n") {
		pair := strings.SplitN(line, ":", 2)
		if len(pair) == 2 {
			status[pair[0]] = strings.Join(strings.Fields(pair[1]), " ")
		}
	}
	for _, key := range []string{"Uid", "Gid"} {
		if status[key] != "1000 1000 1000 1000" {
			return nil, errors.New("candidate credential mismatch")
		}
	}
	if status["Groups"] != "" || status["NoNewPrivs"] != "1" {
		return nil, errors.New("candidate groups or privilege inheritance unsafe")
	}
	for _, key := range []string{"CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"} {
		if status[key] != "0000000000000000" {
			return nil, errors.New("candidate capability set is nonempty")
		}
	}
	return status, nil
}

func terminateCandidate() error {
	deadline := time.Now().Add(2 * time.Second)
	for {
		entries, err := os.ReadDir("/proc")
		if err != nil {
			return err
		}
		remaining := 0
		for _, entry := range entries {
			pid, err := strconv.Atoi(entry.Name())
			if err != nil {
				continue
			}
			raw, err := os.ReadFile(filepath.Join("/proc", entry.Name(), "status"))
			if err != nil {
				continue // exited between enumeration and read
			}
			for _, line := range strings.Split(string(raw), "\n") {
				if strings.HasPrefix(line, "Uid:") && strings.Fields(line)[1] == "1000" {
					remaining++
					if err := syscall.Kill(pid, syscall.SIGKILL); err != nil && err != syscall.ESRCH {
						return err
					}
				}
			}
		}
		if remaining == 0 {
			return nil
		}
		if time.Now().After(deadline) {
			return errors.New("candidate descendants did not cease")
		}
		time.Sleep(10 * time.Millisecond)
	}
}

// observe runs a fixed challenge and returns measurements, NOT a passing gate.
func observe(request Request) (map[string]any, error) {
	if os.Getuid() != 0 {
		return nil, errors.New("guest supervisor must be root")
	}
	for _, path := range []string{control + "/supervisor", control + "/expectation"} {
		if err := privateFile(path); err != nil {
			return nil, err
		}
	}
	before, err := hashFile(control + "/supervisor")
	if err != nil {
		return nil, err
	}
	secret, err := os.ReadFile(control + "/expectation")
	if err != nil || string(secret) != expected {
		return nil, errors.New("protected expectation differs")
	}
	lock, err := os.OpenFile(vault+"/.vlt.lock", os.O_RDWR|os.O_CREATE|os.O_EXCL, 0666)
	if err != nil {
		return nil, err
	}
	defer lock.Close()
	if err := lock.Chmod(0666); err != nil {
		return nil, err
	}
	if err := syscall.Flock(int(lock.Fd()), syscall.LOCK_EX|syscall.LOCK_NB); err != nil {
		return nil, err
	}
	defer syscall.Flock(int(lock.Fd()), syscall.LOCK_UN)
	ctx, cancel := context.WithTimeout(context.Background(), 230*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "/work/bin/candidate-helper", request.Variant, strconv.Itoa(os.Getpid()))
	cmd.Dir = "/work/candidate"
	cmd.Env = []string{"PATH=/usr/bin:/bin", "HOME=/work/candidate", "VLT_LOCK_TIMEOUT=10s"}
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Credential: &syscall.Credential{Uid: 1000, Gid: 1000, Groups: []uint32{}},
		Setsid:     true, Pdeathsig: syscall.SIGKILL,
	}
	null, err := os.Open("/dev/null")
	if err != nil {
		return nil, err
	}
	defer null.Close()
	cmd.Stdin = null
	output := &capture{}
	cmd.Stdout, cmd.Stderr = output, output
	cmd.Cancel = func() error {
		err := syscall.Kill(-cmd.Process.Pid, syscall.SIGTERM)
		if err == syscall.ESRCH {
			return os.ErrProcessDone
		}
		return err
	}
	// After the approved TERM grace, os/exec kills the direct child; the
	// bounded UID sweep below verifies cessation of descendants for two seconds.
	cmd.WaitDelay = 5 * time.Second
	if err := restrictThread(); err != nil {
		return nil, err
	}
	started := time.Now()
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	defer terminateCandidate()
	done := make(chan error, 1)
	go func() { done <- cmd.Wait() }()
	var status map[string]string
	deadline := time.Now().Add(time.Second)
	for time.Now().Before(deadline) {
		status, err = credentials(cmd.Process.Pid)
		if err == nil {
			break
		}
		time.Sleep(time.Millisecond)
	}
	if err != nil {
		return nil, err
	}
	// Supervisor owns both lock and schedule. This demonstrates only the
	// observed hold/release behavior, not exhaustive race freedom.
	time.Sleep(250 * time.Millisecond)
	_, beforeErr := os.Lstat(vault + "/Observed.md")
	heldUnchanged := os.IsNotExist(beforeErr)
	lockStat, err := lock.Stat()
	if err != nil {
		return nil, err
	}
	kernelLocks, err := os.ReadFile("/proc/locks")
	if err != nil {
		return nil, err
	}
	ownerPattern := fmt.Sprintf(" %d ", os.Getpid())
	inodePattern := fmt.Sprintf(":%d ", lockStat.Sys().(*syscall.Stat_t).Ino)
	heldBySupervisor := false
	for _, line := range strings.Split(string(kernelLocks), "\n") {
		if strings.Contains(line, "FLOCK") && strings.Contains(line, ownerPattern) && strings.Contains(line, inodePattern) {
			heldBySupervisor = true
		}
	}
	if err := syscall.Flock(int(lock.Fd()), syscall.LOCK_UN); err != nil {
		return nil, err
	}
	waitErr := <-done
	if err := terminateCandidate(); err != nil {
		return nil, err
	}
	after, err := hashFile(control + "/supervisor")
	if err != nil {
		return nil, err
	}
	note, noteErr := readNote()
	return map[string]any{
		"version": 1, "run": request.Run, "challenge": request.Challenge, "variant": request.Variant,
		"supervisor_sha256": before, "supervisor_unchanged": after == before,
		"candidate_credentials": status, "candidate_exit_success": waitErr == nil,
		"candidate_output": output.data, "output_exceeded": output.exceeded,
		"kernel_lock_held_by_supervisor": heldBySupervisor, "note_absent_during_hold": heldUnchanged,
		"observed_note": note, "note_regular": noteErr == nil, "seconds": time.Since(started).Seconds(),
		"candidate_cessation": true, "verified": false, "admission": "blocked",
		"scope": "bounded supervisor-owned schedule observation; not exhaustive race freedom",
	}, nil
}

func readNote() ([]byte, error) {
	fd, err := syscall.Open(vault+"/Observed.md", syscall.O_RDONLY|syscall.O_NOFOLLOW|syscall.O_NONBLOCK, 0)
	if err != nil {
		return nil, err
	}
	file := os.NewFile(uintptr(fd), "Observed.md")
	defer file.Close()
	info, err := file.Stat()
	if err != nil || !info.Mode().IsRegular() || info.Size() > 4096 || info.Sys().(*syscall.Stat_t).Nlink != 1 {
		return nil, errors.New("invalid note artifact")
	}
	return io.ReadAll(io.LimitReader(file, 4097))
}

func main() {
	runtime.LockOSThread()
	raw, err := io.ReadAll(io.LimitReader(os.Stdin, 4097))
	request, decodeErr := DecodeRequest(raw)
	var result map[string]any
	if err == nil && decodeErr == nil {
		result, err = observe(request)
	} else {
		err = errors.New("invalid supervisor request")
	}
	if err != nil {
		result = map[string]any{"version": 1, "run": request.Run, "error": "trusted-observation-failed",
			"verified": false, "admission": "blocked"}
	}
	data, encodeErr := json.Marshal(result)
	if encodeErr != nil || len(data) > 1048576 {
		os.Exit(3)
	}
	if _, writeErr := io.Copy(os.Stdout, bytes.NewReader(append(data, '\n'))); writeErr != nil || err != nil {
		os.Exit(3)
	}
}
