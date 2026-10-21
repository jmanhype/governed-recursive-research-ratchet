package main

import (
	"strings"
	"testing"
)

func TestFixedRequest(t *testing.T) {
	request, err := DecodeRequest([]byte(`{"version":1,"run":"run-1","challenge":"vlt-lock-observation-001","variant":"clean"}`))
	if err != nil || request.Run != "run-1" {
		t.Fatalf("fixed request failed: %v", err)
	}
}

func TestUnknownDuplicateMalformedAndExecutableFields(t *testing.T) {
	base := `{"version":1,"run":"run-1","challenge":"vlt-lock-observation-001","variant":"clean"}`
	inputs := []string{
		strings.Replace(base, `"version":1`, `"version":true`, 1),
		strings.Replace(base, `"run-1"`, `"../private"`, 1),
		strings.Replace(base, `"clean"`, `"sh -c id"`, 1),
		strings.TrimSuffix(base, "}"),
		base + "{}",
		strings.Replace(base, `"version":1`, `"version":1,"version":1`, 1),
		strings.Replace(base, `"version":1`, `"version":1,"role":"root"`, 1),
		strings.Replace(base, `"version":1`, `"version":1,"expected":"PASS"`, 1),
		strings.Replace(base, `"version":1,`, "", 1),
		strings.Repeat("x", 4097),
	}
	for _, input := range inputs {
		if _, err := DecodeRequest([]byte(input)); err == nil {
			t.Errorf("accepted invalid request %q", input)
		}
	}
}
