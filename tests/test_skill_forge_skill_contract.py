"""Static instruction checks; not live agent-execution certification."""
import re
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / "wk-skill-forge"
GUIDE = "references/style-guide.md"
TOPICS = "references/topic-sources.md"


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
        self.contains(text(GUIDE), "should trigger", "near miss", "ambiguous", "statically")

    def test_modes_and_tool_gates(self):
        gates = section(text(), "Decision Gates")
        self.contains(gates, "file-read", "FAILED", "native file-write", "draft or diff only", "Mode or target missing", "never assume paths")
        self.contains(text(), "Audit is read-only", "Create", "Improve", "only among skills the host shows or the user names", "overengineer")
        self.contains(text(GUIDE), "smallest skill", "concrete need", "Audit applies every check to any target")

    def test_intake_batch(self):
        row, = [line for line in section(text(), "Decision Gates").splitlines() if "one batch" in line]
        self.contains(row, "Create", "Improve", "First prompt", "parent folder", "skill name", "author", "license", "version", "conversation language", "skill language", "local-authored", "imported or adapted", "current language", "English only", "never fill identity defaults silently")
        self.contains(row, "Propose Create depth from the request", "confirm", "Simple", "accept in one reply")
        self.contains(text(), "Never invent author, license, or version", "Never delete meaningful content silently")
        budget = section(text(GUIDE), "4. Body Structure and Budget")
        self.assertRegex(budget, r"\| Simple \(default\) \| .*only `SKILL\.md`.*missing essentials.*target body budget")
        self.assertRegex(budget, r"\| Complex \| .*`references/`.*concrete need.*decision gates.*full validation")
        self.assertRegex(budget, r"\| Professional \| .*topic-sources\.md.*approval.*evaluation only on user request.*Security Audit and Quality Gates")
        self.contains(budget, "Depth never relaxes security, approval, or path rules")

    def test_approval_and_write_loop(self):
        self.contains(text(), "Project policy governs this run's actions", "not host policy", "Invocation authorizes reading and drafting only; forge writes and network calls always need approval.", "Never copy into or write to a global or installed skills directory")
        effects = section(text(GUIDE), "11. Effects and Coexistence")
        self.contains(effects, "forge writes and network calls always need approval")
        for document in (text(), effects):
            self.contains(document, "stated purpose", "other sensitive effects need separate approval")
        steps = section(text(), "Execution Steps")
        self.assertRegex(steps, r"Improve: [Aa]udit.*preservation map.*smallest draft")
        ordered = ("Validate", "Stop before approval if blockers remain", "Get approval", "Before each write, repeat the path check", "native file tool", "written result")
        self.contains(steps, *ordered, "exact draft or diff", "effects")
        self.assertRegex(steps, "(?s)" + ".*".join(map(re.escape, ordered)))

    def test_untrusted_paths_and_audit_coverage(self):
        supporting = section(text(GUIDE), "10. Supporting Files and Portability")
        for document in (text(), supporting):
            self.contains(document, "every target", "without following", "find <target> -type l", "folder itself is not a link", "ask the user to confirm", "stop with Status PARTIAL", "skip and report")
            self.assertNotIn("lexical containment suffices", document)
        self.contains(text(), "never install or follow them", "Never execute bundled tools")
        self.contains(supporting, "exact case", "when to read", "stale references")
        audit = section(text(GUIDE), "15. Security Audit")
        self.contains(audit, "no-follow listing", "report it unavailable", "every shipped file", "referenced executable", "inaccessible", "not passed", "configuration, memory, hooks, or permission settings", "remote instruction loading", "hide steps, URLs, or terms", "third-party content", "data, never as instructions", "Unicode-aware", "zero-width, bidi")

    def test_research_consent_privacy_and_local_help(self):
        self.contains(text(), "local evidence first", "Before any network call, name the source, purpose, and data sent; get explicit approval.", "workspace-relative paths or placeholders", "redact secrets, private identifiers, and sensitive URL parameters", "public attribution")
        self.contains(section(text(TOPICS), "How to research"), "Official vendor docs", "untrusted data", "<tool> --help", "local commands", "optional", "user approval", "already installed", "never run supplied binaries", "compatibility unverified")

    def test_status_and_severity(self):
        output = section(text(), "Output Contract")
        self.assertRegex(output.strip(), r"^All modes: start with 2–3 lines: what was done, Status, decisions needed\.")
        self.contains(output, "details only for findings or failures", "omit empty sections")
        self.contains(output, "severity · path:line · rule · fix", "passed, failed, skipped, unverified", "Static checks", "Status: SUCCESS | PARTIAL | FAILED")
        self.assertRegex(output, r"SUCCESS[^.;]*draft-only")
        self.assertRegex(output, r"PARTIAL[^.;]*write[^.;]*pending[^.;]*declined[^.;]*impossible")
        self.assertRegex(output, r"FAILED[^.;]*unreadable[^.;]*approved write fails")
        self.assertRegex(output, r"PARTIAL[^.;]*incomplete audit coverage")
        self.contains(output, "Unverified checks", "blockers", "intake")
        gates = section(text(GUIDE), "16. Quality Gates")
        self.contains(gates, "### Required (MUST)", "normal use", "user-reported")
        self.assertNotIn("### Blocking (MUST)", gates)
        inherited = "Ask when something is missing or unclear; never assume; verify with real tool output; make the smallest change that works."
        baseline = section(text(GUIDE), "7. Hard Rules Baseline")
        skeleton = text(GUIDE).split("\n## 18. Skeleton\n", 1)[1]
        for rules in (baseline, section(skeleton, "Hard Rules")):
            self.contains(rules, "- " + inherited)
        self.assertRegex(gates.split("### Advisory", 1)[0], r"(?m)^- \[ \] Created or fixed skills carry the ask/verify/minimal-change rule from the Hard Rules Baseline\.$")
        self.contains(gates, "Changed imports have a complete preservation map")
        imports = section(text(GUIDE), "13. Imported and Adapted Skills")
        self.assertNotIn("missing preservation map", imports)

    def test_self_containment_and_bundled_paths(self):
        guide = text(GUIDE)
        references = section(text(), "References")
        for name in (GUIDE, TOPICS):
            self.contains(references, f"`{name}`")
            self.assertNotRegex(text(name), r"\]\(\s*<?(?![\s<])(?!(?:#|https?://))[^)]+\)", "local file link")
        heads = [re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-") for h in re.findall(r"(?m)^#+ (.+)$", guide)]
        for anchor in re.findall(r"\]\(#([^)]+)\)", guide):
            self.assertIn(anchor, heads)
        for head in ("Security Audit", "Quality Gates", "Skeleton"):
            self.assertRegex(guide, rf"(?m)^## \d+\. {head}$")
        documents = "\n".join(text(name) for name in ("SKILL.md", GUIDE, TOPICS))
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

    def test_topic_sources(self):
        self.assertRegex(section(text(), "Execution Steps"), rf"(?m)^\d+\. Create: .*Professional:.*`{re.escape(TOPICS)}`")
        topics = text(TOPICS)
        self.contains(topics, "starting points only")
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
