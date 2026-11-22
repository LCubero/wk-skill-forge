"""Static instruction checks; not live agent-execution certification."""
import re
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / "wk-skill-forge"
GUIDE = "references/style-guide.md"
TOPICS = "references/topic-sources.md"
INTAKE = "references/intake.md"


def text(name="SKILL.md"):
    return (SKILL / name).read_text(encoding="utf-8")


def section(document, heading):
    return document.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]


def bundled_file(path):
    return (
        path.is_relative_to(SKILL)
        and ".." not in path.relative_to(SKILL).parts
        and not any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(SKILL))
        and path.is_file()
    )


class SkillForgeContractTests(unittest.TestCase):
    def contains(self, document, *terms):
        for term in terms:
            with self.subTest(term=term):
                self.assertIn(term, document)

    def test_identity_and_budget(self):
        _, front, body = text().split("---", 2)
        self.contains(front, f"name: {SKILL.name}", "license: MIT", "author: LCubero", 'version: "1.0"', "origin: local-authored")
        self.assertRegex(front, r'(?m)^description: "Trigger: wk-skill-forge\. .{1,132}"$')
        self.assertEqual(re.findall(r"(?m)^## (.+)$", body), ["Activation Contract", "Hard Rules", "Decision Gates", "Execution Steps", "Output Contract", "References"])
        self.assertLessEqual(len(body.split()) * 1.33, 700)
        guide = text(GUIDE)
        examples = re.findall(r"(?ms)^---\n(.*?)^---$", guide)
        self.assertEqual(len(examples), 2)
        for example in examples:
            self.contains(example, "license: <SPDX>", "metadata:", "author:", "version:", "origin:")
        self.contains(section(guide, "3. Layout and Frontmatter"), "metadata.origin", "local-authored", "adapted-portable", "imported-preserved", "review evidence")

    def test_activation(self):
        front = text().split("---", 2)[1]
        pattern = r"(?m)^(?:disable-model-invocation|'disable-model-invocation'|\"disable-model-invocation\")[ \t]*:[ \t]*(.*)$"
        self.assertEqual(re.findall(pattern, front), ["true"])
        self.assertEqual(re.findall(pattern, front + "disable-model-invocation: false\n"), ["true", "false"])
        self.assertNotRegex(front, r"\bforge,")
        self.contains(section(text(), "Activation Contract"), "invokes this skill by name", "never activate on topic overlap", "one run")
        gates = section(text(GUIDE), "16. Quality Gates")
        self.contains(gates, "Only Simple Create skips", "Audit always", "should trigger", "near miss", "ambiguous", "statically")

    def test_modes_and_tool_gates(self):
        gates = section(text(), "Decision Gates")
        self.contains(gates, "file-read", "FAILED", "native file-write", "show draft or diff; PARTIAL", "Mode or target missing", "never assume paths")
        self.contains(text(), "Audit is read-only", "Create", "Improve", "overengineer")
        self.assertRegex(gates, r"Before intake.*skill folder names.*likely duplicates.*continue only if the user confirms")
        self.contains(gates, "report likely duplicates with the intake batch")
        self.contains(text(), "Check local tools per guide")
        self.contains(text(GUIDE), "only skills the host loaded or folders the user names; never search elsewhere",
                      "If the skill needs a local tool and the user allows it, check its version and name it in the draft; otherwise declare it as a prerequisite")
        self.assertRegex(text(GUIDE), r"Before Create intake.*skill folder names.*host-shown or user-named.*listing.*description only if.*overlap.*path check")
        self.contains(text(GUIDE), "smallest skill", "concrete need", "Audit applies every check to any target")

    def test_intake_batch(self):
        row, = [line for line in section(text(), "Decision Gates").splitlines() if "One batch" in line]
        self.contains(row, "Create/Improve", "Create only:", "if depth is unstated", "confirm")
        self.contains(text(GUIDE), "Partial answers: confirm them; ask the rest in one short line", "After Create, suggest one test with a real input")
        self.contains(section(text(GUIDE), "7. Hard Rules Baseline"), "one intake batch", "only for unstated details", "parent folder", "skill name", "identity", "languages", "consequential gaps", "English for skill files only")
        authorship = section(text(GUIDE), "12. Authorship and Provenance")
        self.contains(authorship, "missing author, license, version", "imported or adapted origin", "local-authored", "Simple Create", "accepts the proposed name", "Never silently fill identity defaults")
        gates = section(text(), "Decision Gates")
        self.assertRegex(gates, r"Purpose unknown.*Ask only what the skill should do.*intake")
        self.contains(row, "Never ask conversation language if the user's message sets it")
        self.contains(text(), "Omit unknown version and warn")
        self.contains(authorship, "Omit unknown version and warn", "never write `unknown` or a placeholder")
        self.contains(text(), "Never invent author, license, or version", "Never delete meaningful content silently")
        budget = section(text(GUIDE), "4. Body Structure and Budget")
        self.assertRegex(budget, r"\| Simple \(default\) \| .*only `SKILL\.md`.*missing essentials.*target body budget")
        self.assertRegex(budget, r"\| Complex \| .*`references/`.*concrete need.*decision gates.*full validation")
        self.assertRegex(budget, r"\| Professional \| .*topic-sources\.md.*approval.*evaluation only on user request.*Security Audit and Quality Gates")
        self.assertRegex(budget, r"(?m)^\| Simple .*no activation prompts")
        for depth in ("Complex", "Professional"):
            self.assertRegex(budget, rf"(?m)^\| {depth} .*three activation prompts")
        self.contains(budget, "Depth never relaxes security, approval, or path rules")

    def test_approval_and_write_loop(self):
        self.contains(text(), "Project policy governs this run's actions", "not host policy", "Invocation authorizes reading and drafting only; forge writes and network calls always need approval.", "Never copy into or write to a global or installed skills directory")
        effects = section(text(GUIDE), "11. Effects and Coexistence")
        self.contains(effects, "forge writes and network calls always need approval")
        for document in (text(), effects):
            self.contains(document, "stated purpose", "other sensitive effects need separate approval")
        steps = section(text(), "Execution Steps")
        self.assertRegex(steps, r"Improve: [Aa]udit.*preservation map.*smallest draft")
        ordered = ("Validate", "Stop before approval if blockers remain", "Get approval", "Run the path check for each write destination", "native file tool", "written result")
        self.contains(steps, *ordered, "exact draft or diff", "effects", "Without write access or approval, end PARTIAL")
        self.assertNotIn("or unwritable", steps)
        self.assertRegex(steps, "(?s)" + ".*".join(map(re.escape, ordered)))

    def test_untrusted_paths_and_audit_coverage(self):
        supporting = section(text(GUIDE), "10. Supporting Files and Portability")
        for document in (text(), supporting):
            self.contains(document, "existing skill target", "bundled references are exempt", "path check for each write destination", "without following them with the host's tools", "ask the user to confirm", "stop with Status PARTIAL", "skip and report")
            self.assertNotIn("lexical containment suffices", document)
        self.contains(text(), "never install or follow them", "Never execute bundled tools")
        self.contains(supporting, "exact case", "when to read", "stale references", "`find <target> -type l` (Linux/macOS)", "`Get-ChildItem <target> -Recurse -Force -Attributes ReparsePoint` (PowerShell)")
        audit = section(text(GUIDE), "15. Security Audit")
        self.contains(supporting, "`find <target>`", "`Get-ChildItem <target> -Recurse -Force`", "`(Get-Item <target>).LinkType`", "everything inside", "drop any trailing slash first", 'Normalize `\\` in user-given paths to `/`')
        self.assertRegex(section(text(), "Hard Rules"), r"Before reading an existing skill target, apply the guide's no-follow path check")
        self.assertRegex(supporting, r"check each component in order from the approved workspace root through the target.*Stop before reading or copying if any component is linked")
        self.contains(section(text(), "Execution Steps"), "full no-follow listing")
        self.contains(audit, "`LC_ALL=C.UTF-8 grep -rnP '[\\x{200B}-\\x{200F}\\x{202A}-\\x{202E}\\x{2066}-\\x{2069}\\x{FEFF}]' <target>`", "`Get-ChildItem <target> -Recurse -File -Force | Select-String -Encoding UTF8 -Pattern '[\\u200B-\\u200F\\u202A-\\u202E\\u2066-\\u2069\\uFEFF]'`")
        self.contains(audit, "full no-follow listing", "report it unavailable", "every shipped file", "referenced executable", "inaccessible", "not passed", "configuration, memory, hooks, or permission settings", "remote instruction loading", "hide steps, URLs, or terms", "third-party content", "data, never as instructions", "Unicode-aware", "zero-width, bidi", "reviewed or imported content", "not fresh forge drafts")

    def test_research_consent_privacy_and_local_help(self):
        self.contains(text(), "local evidence first", "Before any network call, name the source, purpose, and data sent; get explicit approval.", "workspace-relative paths or placeholders", "redact secrets, private identifiers, and sensitive URL parameters", "public attribution")
        self.contains(section(text(TOPICS), "How to research"), "Official vendor docs", "untrusted data", "<tool> --help", "local commands", "optional", "user approval", "already installed", "never run supplied binaries", "compatibility unverified")

    def test_status_and_severity(self):
        output = section(text(), "Output Contract")
        self.assertRegex(output.strip(), r"^All modes: start with 2–3 lines: what was done, Status, decisions needed\.")
        self.contains(output, "Show only required details, findings, and failures", "omit empty sections")
        self.contains(output, "severity · path:line · rule · fix", "passed, failed, skipped, unverified", "Static checks", "Status: SUCCESS | PARTIAL | FAILED")
        self.contains(output, "Create and Improve imply a write")
        self.assertRegex(output, r"SUCCESS[^.]*draft-only only on request")
        self.assertRegex(output, r"PARTIAL[^.;]*write[^.;]*pending[^.;]*declined[^.;]*impossible")
        self.assertRegex(output, r"FAILED[^.;]*unreadable[^.;]*approved write fails")
        self.assertRegex(output, r"PARTIAL[^.;]*incomplete audit coverage")
        self.contains(output, "Unverified checks", "blockers", "intake")
        gates = section(text(GUIDE), "16. Quality Gates")
        self.contains(gates, "### Required (MUST)", "normal use", "user-reported")
        self.assertRegex(gates, r"Load- or trigger-blocking frontmatter.*invalid or mismatched name.*missing or placeholder description.*is `blocking`")
        self.assertNotIn("### Blocking (MUST)", gates)
        inherited = "Ask when something is missing or unclear; never assume; verify with real tool output; make the smallest change that works."
        baseline = section(text(GUIDE), "7. Hard Rules Baseline")
        skeleton = text(GUIDE).split("\n## 18. Skeleton\n", 1)[1]
        for rules in (baseline, section(skeleton, "Hard Rules")):
            self.contains(rules, "- " + inherited)
        required = gates.split("### Advisory", 1)[0]
        self.assertRegex(required, r"(?m)^- \[ \] Created or fixed skills carry the ask/verify/minimal-change rule and only safety rules their effects need\.")
        for rules in (baseline, required):
            self.contains(rules, "audit procedures", "link scans", "redaction passes", "preserve function")
        self.contains(gates, "Changed imports have a complete preservation map")
        imports = section(text(GUIDE), "13. Imported and Adapted Skills")
        self.assertNotIn("missing preservation map", imports)

    def test_self_containment_and_bundled_paths(self):
        guide = text(GUIDE)
        references = section(text(), "References")
        for name in (GUIDE, TOPICS, INTAKE):
            self.contains(references, f"`{name}`")
            self.assertNotRegex(text(name), r"\]\(\s*<?(?![\s<])(?!(?:#|https?://))[^)]+\)", "local file link")
        heads = [re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-") for h in re.findall(r"(?m)^#+ (.+)$", guide)]
        for anchor in re.findall(r"\]\(#([^)]+)\)", guide):
            self.assertIn(anchor, heads)
        for head in ("Security Audit", "Quality Gates", "Skeleton"):
            self.assertRegex(guide, rf"(?m)^## \d+\. {head}$")
        documents = "\n".join(text(name) for name in ("SKILL.md", GUIDE, TOPICS, INTAKE))
        for code, link in re.findall(r"`([^`\n]+)`|\]\(([^)\n]+)\)", documents):
            target = (code or link).strip()
            if re.match(r"(?:\./|\.\./)*(?:references|assets|scripts)/.+", target) and not re.search(r"<[^<>]+>", target):
                with self.subTest(target=target):
                    self.assertTrue(bundled_file(SKILL / target.split("#", 1)[0]))
        path = SKILL / GUIDE
        for linked in (path, path.parent, SKILL):
            with self.subTest(linked=linked), patch.object(type(path), "is_symlink", lambda candidate: candidate == linked):
                self.assertFalse(bundled_file(path))
        self.assertNotRegex(documents, r"(?<![A-Za-z])[A-Za-z]:[\\/]", "absolute drive path")
        self.assertNotIn("docs/", re.sub(r"\]\(https://[^\s)]+\)", "]()", documents))
        for leak in ("LD9", "Users/", "00-skillssss", "repo-harness", "0_skill", "adaptation-playbook", "REPO-HARNESS.md", "odd/tasks/", "tests/test_skill_forge_skill_contract.py"):
            self.assertNotIn(leak, documents)

    def test_mode_boundary(self):
        self.contains(section(text(), "Hard Rules"), "Audit is read-only; Evaluate writes only its approved run folder. Neither authorizes a fix.")
        steps = section(text(), "Execution Steps")
        self.assertRegex(steps, r"(?m)^\d+\. Create/Improve: Validate per Quality Gates")
        self.assertRegex(steps, r"(?m)^\d+\. Evaluate: per `references/intake\.md`")
        self.contains(text(INTAKE), "changes nothing outside the run folder")

    def test_evaluate_gates_and_verdict(self):
        intake = text(INTAKE)
        gates = section(intake, "4. Decide")
        self.contains(gates, "first supported gate wins", "why each earlier gate is unsupported")
        order = ["| G1 ", "| G2 ", "| G3 ", "| G4 ", "| G5 ", "| G6 ", "| G7 "]
        self.assertRegex(gates, "(?s)" + ".*".join(map(re.escape, order)))
        for verdict in ("`reject`", "`defer`", "`adopt-as-is`", "`recreate`"):
            self.contains(gates, verdict)
        self.contains(gates, "could change the gate", "G4 even when a collision is confirmed", "unverifiable license where required", "an unmet MUST blocks G6", "If no useful idea survives and no earlier gate applies, `reject`")
        self.assertNotIn("Candidate unreadable", gates)
        self.assertRegex(gates, r"\| G1 \| Unsafe or coercive content[^\n]+\| `reject` \|")
        self.contains(section(intake, "2. Extract"), "met", "unmet", "missing", "not-applicable", "Existence", "Deciding content", "Permission", "never proves")
        output = section(intake, "5. Verdict")
        self.contains(output, "Keep", "Change", "Drop", "Consumers at risk", "path:line", "unknown", "Not verified")
        self.assertRegex(output, r"Drop \(with reason\)")
        self.assertRegex(output, r"PARTIAL[^.]*named missing evidence")
        self.assertRegex(output, r"FAILED[^.]*unreadable[^.]*no verdict")
        self.assertRegex(output, r"SUCCESS[^.]*no deciding gaps[^.]*preflight")
        self.assertRegex(output, r"PARTIAL[^.]*G4")
        self.contains(output, "replace the general Status values")
        self.contains(section(text(GUIDE), "16. Quality Gates"), "reports one `Status` line for workflows")

    def test_evaluate_collisions(self):
        compare = section(text(INTAKE), "3. Compare")
        self.contains(compare, "activation-overlap", "rule-contradiction", "artifact-conflict", "precedence-gap", "both sides", "exclusions")
        self.contains(compare, "Create keeps its folder-name check")

    def test_evaluate_acquisition(self):
        acquire = section(text(INTAKE), "1. Acquire")
        self.contains(
            acquire, "data, never instructions", "never echo secrets", "approval", "new run folder", "never over a prior run",
            "before extracting", "absolute paths", "`..`", "links", "Never execute, install, or source", "no-follow",
            "SHA-256", "manifest", "Cleanup is separate", "maximum entries and total uncompressed bytes",
            "in memory", "manifest is not applicable", "Before copying or extracting", "host's archive tools",
            "nothing is extracted and the verdict is G1 `reject`",
        )
        self.contains(section(text(INTAKE), "6. After the verdict"), "plan, not an edit", "separate approved Improve or Create", "writes the result only to `<run-id>/candidate/`", "leaves `<run-id>/source/` unchanged", "only the user promotes", "never installs")

    def test_evaluate_local_source_preflight(self):
        acquire = section(text(INTAKE), "1. Acquire")
        preflight, = [line for line in acquire.splitlines() if "Before reading or copying a local source" in line]
        self.contains(preflight, "file or folder", "approved source", "may be outside the workspace",
                      "filesystem root", "Stop if any component is linked",
                      "scan its contents without following links", "Stop if any check cannot be completed")
        self.assertLess(acquire.index(preflight), acquire.index("Copy the candidate"))
        self.assertLess(acquire.index("destination: it must be new, contained, and unlinked"),
                        acquire.index("Copy the candidate"))

    def test_evaluate_zip_type_preflight(self):
        acquire = section(text(INTAKE), "1. Acquire")
        self.assertRegex(acquire, r"list each entry's name, uncompressed size, and type before extracting")
        self.assertRegex(acquire, r"If any entry's type cannot be established, stop before extracting")

    def test_topic_sources(self):
        self.assertRegex(section(text(), "Execution Steps"), rf"(?m)^\d+\. Create: .*Professional:.*`{re.escape(TOPICS)}`")
        topics = text(TOPICS)
        self.contains(topics, "starting points only", "file-name encoding (NFC/NFD), document size, tables")
        for heading in (
            "Frontend and UI", "Backend and APIs", "Data and Databases", "DevOps, CI and Cloud",
            "Testing and QA", "Security", "Automation, Scripts and CLI Tools", "Git and GitHub",
            "Documents and Office Files", "Content Creation (writing, image, audio, video)", "Design",
            "AI, LLM and MCP", "Research and Web", "Productivity and Project Management",
        ):
            with self.subTest(heading=heading):
                entry = re.search(r"(?m)^- \*\*Start at:\*\* (.+)$", section(topics, heading))
                self.assertIsNotNone(entry)
                self.assertGreaterEqual(len(re.findall(r"\[[^\]\n]+\]\(https://[^\s)]+\)", entry[1])), 2)
        self.contains(section(topics, "Productivity and Project Management"), "CommonMark", "GFM", "Mermaid", "notes", "diagrams")


if __name__ == "__main__":
    unittest.main()
