// Trusted protocol: candidate output is a JSON byte string, never a control frame.
package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"regexp"
)

type Request struct {
	Version   int    `json:"version"`
	Run       string `json:"run"`
	Challenge string `json:"challenge"`
	Variant   string `json:"variant"`
}

var opaqueID = regexp.MustCompile(`^[a-zA-Z0-9][a-zA-Z0-9-]{0,63}$`)

// DecodeRequest consumes exactly one size-bounded object and rejects duplicates.
func DecodeRequest(raw []byte) (Request, error) {
	var result Request
	if len(raw) > 4096 {
		return result, errors.New("oversized request")
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	token, err := decoder.Token()
	if err != nil || token != json.Delim('{') {
		return result, errors.New("request must be an object")
	}
	seen := map[string]bool{}
	for decoder.More() {
		key, err := decoder.Token()
		if err != nil {
			return result, err
		}
		name, ok := key.(string)
		if !ok || seen[name] {
			return result, errors.New("duplicate request field")
		}
		seen[name] = true
		var ignored json.RawMessage
		if err := decoder.Decode(&ignored); err != nil {
			return result, err
		}
	}
	if _, err := decoder.Token(); err != nil {
		return result, err
	}
	if _, err := decoder.Token(); err != io.EOF {
		return result, errors.New("trailing request data")
	}
	decoder = json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&result); err != nil {
		return result, err
	}
	if len(seen) != 4 || result.Version != 1 || !opaqueID.MatchString(result.Run) ||
		result.Challenge != "vlt-lock-observation-001" {
		return result, errors.New("invalid fixed request")
	}
	switch result.Variant {
	case "clean", "forged-pass", "altered-expectations", "mutation", "impersonation", "oversized", "malformed":
		return result, nil
	default:
		return result, errors.New("unregistered variant")
	}
}
