"""Candidate-visible per-scenario Go probes; no protected truth crosses the VM boundary."""

PROBES = {
'D001': r'''dir := t.TempDir()
os.MkdirAll(filepath.Join(dir, ".obsidian"), 0755)
writeProbe(t, filepath.Join(dir, ".obsidian", "hidden.md"), "# Hidden")
if _, err := resolveNote(dir, "hidden"); err == nil { t.Fatal("hidden note resolved") }''',
'D002': r'''dir := t.TempDir(); writeProbe(t, filepath.Join(dir, "Note.md"), "# Note")
if _, err := resolveNote(dir, "NOTE"); err == nil { t.Fatal("case-mismatched exact title resolved") }''',
'D003': r'''dir := t.TempDir(); os.MkdirAll(filepath.Join(dir, "a"), 0755); os.MkdirAll(filepath.Join(dir, "b"), 0755)
writeProbe(t, filepath.Join(dir, "a", "First.md"), "---\naliases: [X]\n---\n")
writeProbe(t, filepath.Join(dir, "b", "Second.md"), "---\naliases: [X]\n---\n")
path, err := resolveNote(dir, "X"); requireProbe(t, err); requireRelProbe(t, dir, path, "a/First.md")''',
'D004': r'''dir := t.TempDir(); os.MkdirAll(filepath.Join(dir, "a"), 0755); os.MkdirAll(filepath.Join(dir, "b"), 0755)
writeProbe(t, filepath.Join(dir, "a", "Note.md"), "# first"); writeProbe(t, filepath.Join(dir, "b", "Note.md"), "# second")
path, err := resolveNote(dir, "Note"); requireProbe(t, err); requireRelProbe(t, dir, path, "a/Note.md")''',
'D005': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Note.md"), "# Note")
if _, ok := v.resolveLink("note"); !ok { t.Fatal("lowercase title did not resolve") }''',
'D006': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "photo.png"), "image")
if _, ok := v.resolveLink("photo.png"); !ok { t.Fatal("attachment did not resolve") }''',
'D007': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Target.md"), "---\naliases: [Alias]\n---\n")
if _, err := v.resolve("ALIAS"); err != nil { t.Fatalf("alias lookup is case-sensitive: %v", err) }''',
'D008': r'''text := "```go\n[[Ignored]]\n```\n"; if links := ParseWikilinks(text); len(links) != 0 { t.Fatalf("inert link observed: %#v", links) }''',
'D009': r'''links := ParseWikilinks("![[Note]]"); if len(links) != 1 || !links[0].Embed { t.Fatalf("embed not observed: %#v", links) }''',
'D010': r'''links := ParseWikilinks("[[Note#^abc]]"); if len(links) != 1 || links[0].BlockID != "abc" { t.Fatalf("block ID differs: %#v", links) }''',
'D011': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Target.md"), "# Target"); writeProbe(t, filepath.Join(v.dir, "Source.md"), "![[Target]]\n")
results, err := FindBacklinks(v.dir, "Target"); requireProbe(t, err); requireContainsProbe(t, results, "Source.md")''',
'D012': r'''lines := strings.Split("## Same\na\n## Same\nb\n", "\n"); _, err := findSection(lines, "## Same")
requireProbe(t, err); if !strings.Contains(err.Error(), "ambiguous") { t.Fatal("duplicate heading was not ambiguous") }''',
'D013': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Note.md"), "---\nmetadata:\n  type: nested\n---\nbody\n")
requireProbe(t, v.PropertySet("Note", "type", "changed")); yaml, _, ok := ExtractFrontmatter(readFileProbe(t, filepath.Join(v.dir, "Note.md")))
if !ok || FrontmatterGetValue(yaml, "type") != "changed" { t.Fatalf("top-level property missing: %q", yaml) }''',
'D014': r'''values := FrontmatterGetList("aliases: [\"Quoted\", Plain]", "aliases")
if len(values) != 2 || values[0] != "Quoted" || values[1] != "Plain" { t.Fatalf("quoted alias survived: %#v", values) }''',
'D015': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Old.md"), "# Old"); _, _ = v.resolve("Old")
requireProbe(t, v.Create("New", "New.md", "# New", false, false)); if _, err := v.resolve("New"); err != nil { t.Fatalf("new note absent from index: %v", err) }''',
'D016': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Source.md"), "# Source"); writeProbe(t, filepath.Join(v.dir, "Target.md"), "# Target")
if _, err := v.Move("Source.md", "Target.md"); err != ErrDestinationExists { t.Fatalf("overwrite denial differs: %v", err) }''',
'D017': r'''v := vaultProbe(t); os.MkdirAll(filepath.Join(v.dir, "_inbox"), 0755); writeProbe(t, filepath.Join(v.dir, "_inbox", "Note.md"), "# Note"); writeProbe(t, filepath.Join(v.dir, "Ref.md"), "[[_inbox/Note]]\n")
_, err := v.Move("_inbox/Note.md", "decisions/Note.md"); requireProbe(t, err); requireContainsProbe(t, []string{readFileProbe(t, filepath.Join(v.dir, "Ref.md"))}, "[[decisions/Note]]")''',
'D018': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Old.md"), "# Old"); _, _ = v.resolve("Old")
_, err := v.Delete("Old", "", true); requireProbe(t, err); if _, err = v.resolve("Old"); err == nil { t.Fatal("deleted note remained indexed") }''',
'D019': r'''dir := t.TempDir(); release, err := LockVault(dir, true); requireProbe(t, err); defer release()
done := make(chan error, 1); go func() { _, err := LockVault(dir, true); done <- err }()
select { case err := <-done: requireProbe(t, err) ; case <-time.After(2 * time.Second): t.Fatal("second lock waited unbounded") }''',
'D020': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Note.md"), "# One"); requireProbe(t, v.Append("Note", "Two", false))
if got := readFileProbe(t, filepath.Join(v.dir, "Note.md")); got != "# One\nTwo" { t.Fatalf("append bytes differ: %q", got) }''',
'D021': r'''if _, err := safePath(t.TempDir(), "/tmp/absolute"); err != ErrPathTraversal { t.Fatalf("absolute path denial differs: %v", err) }''',
'D022': r'''if _, err := safePath(t.TempDir(), "../escape"); err != ErrPathTraversal { t.Fatalf("traversal denial differs: %v", err) }''',
'D023': r'''ranges := expandAndMerge([]int{0, 1}, 1, 3); if len(ranges) != 1 || ranges[0] != (lineRange{0, 2}) { t.Fatalf("adjacent ranges not merged: %#v", ranges) }''',
'D024': r'''v := vaultProbe(t); path := filepath.Join(v.dir, "Note.md"); writeProbe(t, path, "first"); v.registry.register(v.dir, path, []byte("first")); writeProbe(t, path, "changed")
if got := v.VerifyIntegrity("Note")["Note"]; got != IntegrityMismatch { t.Fatalf("tampering was not reported: %v", got) }''',
'C001': r'''v := vaultProbe(t); requireProbe(t, v.Create("Note", "Note.md", "# Exact", false, false)); got, err := v.Read("Note", ""); requireProbe(t, err); if got.Content != "# Exact" { t.Fatalf("round trip differs: %q", got.Content) }''',
'C002': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Target.md"), "---\naliases: [Alias]\n---\n# Target\n"); _, err := v.Read("Alias", ""); requireProbe(t, err)''',
'C003': r'''if links := ParseWikilinks("```go\n[[Ignored]]\n```\n"); len(links) != 0 { t.Fatalf("inert clean control failed: %#v", links) }''',
'C004': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Note.md"), "---\nstatus: active\n---\nold\n"); requireProbe(t, v.Write("Note", "new", false)); requireContainsProbe(t, []string{readFileProbe(t, filepath.Join(v.dir, "Note.md"))}, "status: active")''',
'C005': r'''v := vaultProbe(t); writeProbe(t, filepath.Join(v.dir, "Old.md"), "# Old"); writeProbe(t, filepath.Join(v.dir, "Ref.md"), "[[Old]]\n"); _, err := v.Move("Old.md", "New.md"); requireProbe(t, err); requireContainsProbe(t, []string{readFileProbe(t, filepath.Join(v.dir, "Ref.md"))}, "[[New]]")''',
'C006': r'''dir := t.TempDir(); _, a := safePath(dir, "/tmp/absolute"); _, b := safePath(dir, "../escape"); if a == nil || b == nil { t.Fatal("path denial clean control failed") }''',
'C007': r'''v := vaultProbe(t); if _, err := v.Read("Absent", ""); err == nil { t.Fatal("missing note clean control fabricated content") }''',
'C008': r'''v := vaultProbe(t); path := filepath.Join(v.dir, "Note.md"); writeProbe(t, path, "first"); v.registry.register(v.dir, path, []byte("first")); writeProbe(t, path, "changed"); if got := v.VerifyIntegrity("Note")["Note"]; got != IntegrityMismatch { t.Fatalf("mismatch clean control differs: %v", got) }''',
}

HEADER = '''package vlt

import (
\t"os"
\t"path/filepath"
\t"strings"
\t"testing"
\t"time"
)

var _ = time.Second

func writeProbe(t *testing.T, path, content string) {
\tt.Helper()
\tif err := os.WriteFile(path, []byte(content), 0644); err != nil { t.Fatal(err) }
}

func requireProbe(t *testing.T, err error) {
\tt.Helper()
\tif err != nil { t.Fatal(err) }
}

func readFileProbe(t *testing.T, path string) string {
\tt.Helper()
\tdata, err := os.ReadFile(path)
\tif err != nil { t.Fatal(err) }
\treturn string(data)
}

func requireRelProbe(t *testing.T, root, path, expected string) {
\tt.Helper()
\tgot, err := filepath.Rel(root, path)
\tif err != nil { t.Fatal(err) }
\tif filepath.ToSlash(got) != expected { t.Fatalf("path %q, want %q", got, expected) }
}

func requireContainsProbe(t *testing.T, values []string, expected string) {
\tt.Helper()
\tfor _, value := range values { if strings.Contains(value, expected) { return } }
\tt.Fatalf("missing %q in %#v", expected, values)
}

func vaultProbe(t *testing.T) *Vault {
\tt.Helper()
\tdir := t.TempDir()
\treturn &Vault{dir: dir, registry: openRegistry(dir)}
}

func TestGRRR__CHALLENGE__(t *testing.T) {
__BODY__
}
'''


def probe_source(challenge: str) -> str:
    from common import require
    require(challenge in PROBES, 'InvalidInput', 'Unknown corpus probe')
    return HEADER.replace('__CHALLENGE__', challenge).replace('__BODY__', PROBES[challenge])
