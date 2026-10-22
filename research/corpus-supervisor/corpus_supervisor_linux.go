//go:build linux

package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"
)

type request struct {
	Version   int    `json:"version"`
	Run       string `json:"run"`
	Challenge string `json:"challenge"`
	Variant   string `json:"variant"`
}

type seed struct {
	Challenge   string `json:"challenge"`
	Kind        string `json:"kind"`
	File        string `json:"file"`
	Anchor      string `json:"anchor"`
	Replacement string `json:"replacement"`
}

type capture struct {
	mu sync.Mutex
	data []byte
}

func (c *capture) Write(p []byte) (int, error) {
	c.mu.Lock(); defer c.mu.Unlock()
	if left := 524288-len(c.data); len(p) > left { c.data = append(c.data, p[:left]...); return len(p), errors.New("output cap") }
	c.data = append(c.data, p...); return len(p), nil
}

func hashFile(path string) (string, error) { data, err := os.ReadFile(path); if err != nil { return "", err }; sum := sha256.Sum256(data); return hex.EncodeToString(sum[:]), nil }

func private(path string) error {
	info, err := os.Lstat(path); if err != nil { return err }
	status, ok := info.Sys().(*syscall.Stat_t)
	if !ok || !info.Mode().IsRegular() || status.Uid != 0 || info.Mode().Perm()&0077 != 0 || status.Nlink != 1 { return errors.New("private regular root file required") }
	return nil
}

func decodeRequest(raw []byte) (request, error) {
	if len(raw) > 4096 { return request{}, errors.New("oversized request") }
	var result request
	decoder := json.NewDecoder(bytes.NewReader(raw)); decoder.DisallowUnknownFields()
	if err := decoder.Decode(&result); err != nil { return request{}, err }
	if _, err := decoder.Token(); err != io.EOF { return request{}, errors.New("trailing request") }
	valid := regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9-]{0,63}$`)
	challenge := regexp.MustCompile(`^GRRR-VC-[DC][0-9]{3}$`)
	if result.Version != 1 || !valid.MatchString(result.Run) || !challenge.MatchString(result.Challenge) || result.Variant != result.Challenge {
		return request{}, errors.New("unregistered corpus request")
	}
	return result, nil
}

func copyTree(source, target string) error {
	return filepath.WalkDir(source, func(path string, entry fs.DirEntry, err error) error {
		if err != nil { return err }
		relative, err := filepath.Rel(source, path); if err != nil { return err }
		destination := filepath.Join(target, relative)
		info, err := entry.Info(); if err != nil { return err }
		if entry.IsDir() { return os.MkdirAll(destination, info.Mode().Perm()) }
		if !entry.Type().IsRegular() { return errors.New("non-regular source member") }
		data, err := os.ReadFile(path); if err != nil { return err }
		return os.WriteFile(destination, data, info.Mode().Perm())
	})
}

func hardenSource(path string) error {
	return filepath.WalkDir(path, func(current string, entry fs.DirEntry, err error) error {
		if err != nil { return err }
		if current == path { return os.Chmod(path, 0555) }
		if entry.IsDir() { return os.Chmod(current, 0555) }
		if entry.Type().IsRegular() { return os.Chmod(current, 0444) }
		return errors.New("non-regular staged source member")
	})
}

func stage(request request) error {
	raw, err := os.ReadFile("/root/inputs/seeds.json"); if err != nil { return err }
	if len(raw) > 1048576 { return errors.New("oversized seed catalog") }
	var seeds []seed
	if err := json.Unmarshal(raw, &seeds); err != nil { return err }
	selected := -1
	for index, item := range seeds { if item.Challenge == request.Challenge { selected = index; break } }
	if selected < 0 { return errors.New("scenario absent") }
	if err := copyTree("/root/source", "/work/candidate/source"); err != nil { return err }
	current := seeds[selected]
	if current.Kind == "single-unique-replacement" {
		path := filepath.Join("/work/candidate/source", filepath.FromSlash(current.File))
		if filepath.ToSlash(filepath.Clean(current.File)) != current.File || filepath.IsAbs(current.File) || filepath.HasPrefix(current.File, "..") { return errors.New("unsafe seed path") }
		data, err := os.ReadFile(path); if err != nil { return err }
		anchor, replacement := []byte(current.Anchor), []byte(current.Replacement)
		if bytes.Equal(anchor, replacement) || bytes.Count(data, anchor) != 1 { return errors.New("seed anchor is not unique") }
		if err := os.WriteFile(path, bytes.Replace(data, anchor, replacement, 1), 0644); err != nil { return err }
	} else if current.Kind != "clean-control" || current.File != nilString { return errors.New("unknown seed kind") }
	probePath := "/root/probes/" + request.Challenge + ".go"
	if err := private(probePath); err != nil { return err }
	data, err := os.ReadFile(probePath); if err != nil || len(data) > 65536 { return errors.New("unsafe probe") }
	if err := os.WriteFile("/work/candidate/source/grrr_corpus_probe_test.go", data, 0644); err != nil { return err }
	return hardenSource("/work/candidate/source")
}

const nilString = ""

func credentials(pid int) (map[string]string, error) {
	raw, err := os.ReadFile(fmt.Sprintf("/proc/%d/status", pid)); if err != nil { return nil, err }
	status := map[string]string{}
	for _, line := range strings.Split(string(raw), "\n") {
		if pair := strings.SplitN(line, ":", 2); len(pair) == 2 { status[pair[0]] = strings.Join(strings.Fields(pair[1]), " ") }
	}
	for _, key := range []string{"Uid", "Gid"} { if status[key] != "1000 1000 1000 1000" { return nil, errors.New("credential mismatch") } }
	if status["Groups"] != "" || status["NoNewPrivs"] != "1" { return nil, errors.New("groups or privilege mismatch") }
	for _, key := range []string{"CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"} { if status[key] != "0000000000000000" { return nil, errors.New("capability mismatch") } }
	return status, nil
}

func prctl(option, value uintptr) error {
	_, _, errno := syscall.RawSyscall6(syscall.SYS_PRCTL, option, value, 0, 0, 0, 0)
	if errno != 0 { return errno }
	return nil
}

func restrictThread() error {
	if err := prctl(38, 1); err != nil { return err }
	for capability := uintptr(0); capability < 64; capability++ {
		if err := prctl(24, capability); err != nil && err != syscall.EINVAL { return err }
	}
	return nil
}

func terminate() error {
	deadline := time.Now().Add(2*time.Second)
	for {
		remaining := 0
		entries, err := os.ReadDir("/proc"); if err != nil { return err }
		for _, entry := range entries {
			pid, err := strconv.Atoi(entry.Name()); if err != nil { continue }
			raw, err := os.ReadFile(filepath.Join("/proc", entry.Name(), "status")); if err != nil { continue }
			for _, line := range strings.Split(string(raw), "\n") { if strings.HasPrefix(line, "Uid:") && strings.Fields(line)[1] == "1000" { remaining++; syscall.Kill(pid, syscall.SIGKILL) } }
		}
		if remaining == 0 { return nil }; if time.Now().After(deadline) { return errors.New("candidate descendants remained") }; time.Sleep(10*time.Millisecond)
	}
}

func observe(request request) (map[string]any, error) {
	if os.Getuid() != 0 { return nil, errors.New("supervisor must be root") }
	for _, path := range []string{"/work/control/supervisor", "/work/control/expectation"} { if err := private(path); err != nil { return nil, err } }
	before, err := hashFile("/work/control/supervisor"); if err != nil { return nil, err }
	if value, err := os.ReadFile("/work/control/expectation"); err != nil || string(value) != "EVALUATOR-OWNED-TRUTH\n" { return nil, errors.New("protected expectation differs") }
	if err := stage(request); err != nil { return nil, fmt.Errorf("stage: %w", err) }
	lock, err := os.OpenFile("/work/vault/.vlt.lock", os.O_RDWR|os.O_CREATE|os.O_EXCL, 0666); if err != nil { return nil, err }
	defer lock.Close(); if err := lock.Chmod(0666); err != nil { return nil, err }
	if err := syscall.Flock(int(lock.Fd()), syscall.LOCK_EX|syscall.LOCK_NB); err != nil { return nil, err }
	defer syscall.Flock(int(lock.Fd()), syscall.LOCK_UN)
	command := exec.Command("/work/bin/corpus-helper", request.Challenge[len("GRRR-VC-"):], strconv.Itoa(os.Getpid()))
	command.Dir = "/work/candidate"
	command.Env = []string{"PATH=/usr/bin:/bin:/work/go/bin", "HOME=/work/candidate", "VLT_LOCK_TIMEOUT=10s"}
	command.SysProcAttr = &syscall.SysProcAttr{Credential: &syscall.Credential{Uid: 1000, Gid: 1000}, Setsid: true, Pdeathsig: syscall.SIGKILL}
	null, err := os.Open("/dev/null"); if err != nil { return nil, err }; defer null.Close(); command.Stdin = null
	output := &capture{}; command.Stdout, command.Stderr = output, output
	if err := restrictThread(); err != nil { return nil, err }
	started := time.Now(); if err := command.Start(); err != nil { return nil, err }
	defer terminate()
	done := make(chan error, 1); go func() { done <- command.Wait() }()
	var status map[string]string
	for deadline := time.Now().Add(time.Second); time.Now().Before(deadline); {
		if status, err = credentials(command.Process.Pid); err == nil { break }; time.Sleep(time.Millisecond)
	}
	if err != nil { return nil, fmt.Errorf("credentials: %w", err) }
	lockInfo, err := lock.Stat(); if err != nil { return nil, err }
	kernelLocks, err := os.ReadFile("/proc/locks"); if err != nil { return nil, err }
	owner, inode := fmt.Sprintf(" %d ", os.Getpid()), fmt.Sprintf(":%d ", lockInfo.Sys().(*syscall.Stat_t).Ino)
	held := false
	for _, line := range strings.Split(string(kernelLocks), "\n") { if strings.Contains(line, "FLOCK") && strings.Contains(line, owner) && strings.Contains(line, inode) { held = true } }
	waitErr := <-done; if err := terminate(); err != nil { return nil, err }
	after, err := hashFile("/work/control/supervisor"); if err != nil { return nil, err }
	return map[string]any{"version":1, "run":request.Run, "challenge":request.Challenge, "variant":request.Variant,
		"supervisor_sha256":before, "supervisor_unchanged":after==before, "candidate_credentials":status,
		"candidate_exit_success":waitErr==nil, "candidate_output":output.data, "output_exceeded":len(output.data)==524288,
		"kernel_lock_held_by_supervisor":held, "seconds":time.Since(started).Seconds(), "candidate_cessation":true,
		"verified":false, "admission":"blocked", "scope":"one-scenario disposable corpus fixture; three test-binary repetitions"}, nil
}

func main() {
	runtime.LockOSThread(); raw, err := io.ReadAll(io.LimitReader(os.Stdin, 4097)); if err != nil { os.Exit(3) }
	request, decodeErr := decodeRequest(raw); var result map[string]any
	if decodeErr == nil { result, err = observe(request) } else { err = decodeErr }
	if err != nil {
		result = map[string]any{"version":1, "run":request.Run, "error":"corpus-observation-failed",
			"error_detail":err.Error(), "verified":false, "admission":"blocked"}
		fmt.Fprintln(os.Stderr, "corpus observation failed: "+err.Error())
	}
	encoded, encodeErr := json.Marshal(result); if encodeErr != nil || len(encoded) > 1048576 || err != nil { os.Exit(3) }
	if _, writeErr := io.Copy(os.Stdout, bytes.NewReader(append(encoded, '\n'))); writeErr != nil { os.Exit(3) }
}
