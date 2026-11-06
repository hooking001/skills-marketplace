"""Behavior checks; actual EDA integration runs when tools are installed."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import manage
import rtl_flow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rtl flow test ")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def cli(self, *args, ok=True, env=None):
        result = subprocess.run([str(a) for a in args], cwd=str(self.work),
                                env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout[-6000:])
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def project(self, *extra):
        self.cli(sys.executable, ROOT / "scripts/manage.py", "setup", "design",
                 self.work, "--top", "counter_top", *extra)
        return self.work / "design"

    def execute(self, project, script, *args, **kwargs):
        return self.cli("bash", project / script, *args, **kwargs)

    def test_shell_syntax(self):
        for script in ROOT.rglob("*.sh"):
            self.cli("/bin/bash", "-n", script)

    def test_existing_project_preserved(self):
        project = self.project()
        rtl = project / "rtl/counter_top.v"
        rtl.write_text("user RTL\n")
        self.cli(sys.executable, ROOT / "scripts/manage.py", "setup", "design",
                 self.work, ok=False)
        self.assertEqual(rtl.read_text(), "user RTL\n")

    def test_invalid_identifiers_rejected_without_creation(self):
        for name in ("../escape", "a-b", "a;write", "1bad"):
            self.cli(sys.executable, ROOT / "scripts/manage.py", "setup", name,
                     self.work, ok=False)
        self.assertEqual(list(self.work.iterdir()), [])

    def test_custom_liberty_copied_and_project_relocatable(self):
        liberty = self.work / "custom corner.lib"
        liberty.write_text("custom library contents")
        project = self.project("--liberty", liberty)
        liberty.unlink()
        moved = self.work / "moved project"
        project.rename(moved)
        config = json.loads((moved / "project.json").read_text())
        self.assertEqual((moved / config["liberty"]).read_text(), "custom library contents")
        self.assertTrue((moved / "script/rtl_flow.py").is_file())
        self.assertFalse(any(p.is_symlink() for p in moved.rglob("*")))
        self.execute(moved, "clean.sh")

    def test_filelists_spaces_comments_crlf_and_no_final_newline(self):
        source = self.work / "source file.sv"
        source.write_text("module a; endmodule\n")
        listing = self.work / "rtl.f"
        listing.write_bytes(b'# comment\r\n// comment\r\n\r\n"source file.sv"')
        self.assertEqual(rtl_flow.filelist(listing), [source])
        listing.write_text("-f other.f\n")
        with self.assertRaises(ValueError):
            rtl_flow.filelist(listing)

    def test_checksum_mismatch_preserves_file(self):
        lib = self.work / "lib"
        lib.mkdir()
        damaged = lib / "NangateOpenCellLibrary_typical.lib"
        damaged.write_text("corrupt")
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            manage.download(lib)
        self.assertEqual(damaged.read_text(), "corrupt")

    def test_download_validates_before_publishing(self):
        manifest = json.loads((ROOT / "resources/library.json").read_text())

        def fetch(command, **kwargs):
            target = Path(command[-1])
            shutil.copyfile(str(ROOT / "resources/lib" / target.name), str(target))

        with mock.patch.object(manage.subprocess, "run", side_effect=fetch), contextlib.redirect_stdout(io.StringIO()):
            manage.download(self.work)
        for item in manifest["files"]:
            self.assertEqual(manage.digest(self.work / Path(item["path"]).name), item["sha256"])

    def test_download_failure_leaves_no_partial_file(self):
        def corrupt(command, **kwargs):
            Path(command[-1]).write_text("HTML instead of library")

        with mock.patch.object(manage.subprocess, "run", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                manage.download(self.work)
        self.assertEqual(list(self.work.iterdir()), [])

    def test_clean_only_owned_outputs_and_rejects_escape(self):
        project = self.project()
        notes = project / "synth/notes.txt"
        notes.write_text("keep")
        owned = project / "synth/test_synth.v"
        owned.write_text("generated")
        rtl_flow.reserve(project, [owned])
        self.execute(project, "clean.sh")
        self.assertEqual(notes.read_text(), "keep")
        self.assertFalse(owned.exists())
        (project / ".rtl-flow-outputs.json").write_text('["../outside.txt"]')
        self.execute(project, "clean.sh", ok=False)

    def test_symlinked_output_rejected(self):
        project = self.project()
        external = self.work / "external"
        external.write_text("keep")
        link = project / "synth/counter_top_synth.v"
        link.symlink_to(external)
        with self.assertRaises(ValueError):
            rtl_flow.reserve(project, [link])
        self.assertEqual(external.read_text(), "keep")

    def test_install_is_explicit_and_non_destructive(self):
        destination = self.work / "skills"
        self.cli("bash", ROOT / "install.sh", "--destination", destination)
        installed = destination / "nangate45"
        self.assertTrue((installed / "SKILL.md").is_file())
        self.assertFalse((installed / ".git").exists())
        self.assertFalse((installed / ".serena").exists())
        self.assertFalse(any(p.is_symlink() for p in installed.rglob("*")))
        self.cli("bash", ROOT / "install.sh", "--destination", destination, ok=False)
        self.cli("bash", installed / "scripts/setup_project.sh", "installed_project", self.work)

    @unittest.skipUnless(shutil.which("iverilog") and shutil.which("vvp"), "Icarus not installed")
    def test_real_simulation_and_failure_exit(self):
        project = self.project()
        result = self.execute(project, "script/run_tb.sh")
        self.assertIn("PASS:", result.stdout)
        tb = project / "tb/counter_top_tb.v"
        tb.write_text(tb.read_text().replace("((i + 1) & 15)", "((i + 2) & 15)"))
        self.execute(project, "script/run_tb.sh", ok=False)

    @unittest.skipUnless(shutil.which("yosys"), "Yosys not installed")
    def test_real_sequential_mapping_in_space_path_and_failed_rerun(self):
        project = self.project()
        self.execute(project, "script/run_synth.sh")
        netlist = project / "synth/counter_top_synth.v"
        self.assertIn("DFF", netlist.read_text())
        report = (project / "synth/counter_top_synth_report.txt").read_text()
        self.assertIn("Chip area", report)
        rtl = project / "rtl/counter_top.v"
        rtl.write_text("invalid Verilog")
        self.execute(project, "script/run_synth.sh", ok=False)
        self.assertFalse(netlist.exists())

    @unittest.skipUnless(all(shutil.which(t) for t in ("yosys", "iverilog", "vvp")), "EDA tools not installed")
    def test_real_adder_example(self):
        project = self.work / "adder example"
        shutil.copytree(str(ROOT / "example/full_adder_4bit"), str(project), symlinks=False,
                        ignore=shutil.ignore_patterns("synth", "dump", ".rtl-flow-outputs.json"))
        # Reuse the canonical runner with this independent example copy.
        for command in ("tb", "synth"):
            result = self.cli(sys.executable, ROOT / "scripts/rtl_flow.py", "--project", project, command)
            if command == "tb":
                self.assertIn("All 512 test cases PASSED", result.stdout)
        self.assertTrue((project / "synth/full_adder_4bit_synth.v").is_file())


if __name__ == "__main__":
    unittest.main()
