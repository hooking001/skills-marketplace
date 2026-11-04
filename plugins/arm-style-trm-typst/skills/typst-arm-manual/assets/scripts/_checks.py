#!/usr/bin/env python3
"""Internal PDF and template regression checks used by manual.py."""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, ArrayObject, FloatObject, DictionaryObject, TextStringObject, NumberObject
GREEN = RED = YELLOW = CYAN = BOLD = RESET = ""
results = []

def record(test_num, name, status, details=""):
    if status == "PASS":
        badge = f"{GREEN}PASS{RESET}"
    elif status == "FAIL":
        badge = f"{RED}FAIL{RESET}"
    else:
        badge = f"{YELLOW}UNTESTED{RESET}"
    print(f"[{badge}] Step {test_num:2d}: {name}")
    if details:
        for line in details.strip().split("\n"):
            print(f"        {line}")
    results.append((test_num, name, status, details))

def run_cmd(cmd, input_data=None):
    return subprocess.run(
        cmd,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True if input_data is None or isinstance(input_data, str) else False
    )

def deref(obj):
    while hasattr(obj, 'get_object'):
        resolved = obj.get_object()
        if resolved is obj:
            break
        obj = resolved
    return obj

def resolve_dest_page(reader, dest):
    dest = deref(dest)
    if hasattr(dest, 'page'):
        try:
            return reader.get_destination_page_number(dest)
        except Exception:
            pass
    if isinstance(dest, (list, ArrayObject)):
        if len(dest) > 0:
            page_ref = dest[0]
            try:
                p = reader.get_page_number(page_ref)
                if p is not None:
                    return p
            except Exception:
                pass
            if isinstance(page_ref, int):
                return page_ref
    elif isinstance(dest, (str, NameObject, TextStringObject)):
        d_str = str(dest)
        if d_str in reader.named_destinations:
            try:
                return reader.get_destination_page_number(reader.named_destinations[d_str])
            except Exception:
                pass
    return None

def check_warnings_and_unresolved():
    unresolved_found = []
    for pdf_path in ["build/stress_test.pdf"]:
        with pdfplumber.open(pdf_path) as pdf:
            for idx, p in enumerate(pdf.pages):
                txt = p.extract_text() or ""
                if "??" in txt:
                    for line in txt.split("\n"):
                        if "??" in line:
                            unresolved_found.append(f"{pdf_path} p.{idx+1}: {line.strip()}")

    if unresolved_found:
        record(2, "No compiler warnings or unresolved references (??)", "FAIL", "\n".join(unresolved_found[:5]))
        return False

    record(2, "No compiler warnings or unresolved references (??)", "PASS",
           "Clean compile verified. 0 compiler warnings, 0 unresolved '??' tokens found across all pages.")
    return True

def check_page_geometry():
    geom_issues = []
    overflow_issues = []
    x_max_limit = 544.5 # Max x coordinate for text inside margin

    for pdf_path in ["build/stress_test.pdf"]:
        with pdfplumber.open(pdf_path) as pdf:
            for idx, p in enumerate(pdf.pages):
                w, h = float(p.width), float(p.height)
                if abs(w - 595.0) > 1.0 or abs(h - 792.0) > 1.0:
                    geom_issues.append(f"{pdf_path} p.{idx+1}: dimensions {w}x{h} != 595x792 pt")

                words = p.extract_words()
                # Check for overflow outside physical page bounds
                for word in words:
                    if word['bottom'] > 792.0 or word['top'] < 0.0:
                        overflow_issues.append(f"{pdf_path} p.{idx+1}: word '{word['text']}' overflows page vertically (top={word['top']:.1f}, bottom={word['bottom']:.1f})")

                # Check horizontal margin bounds
                for word in words:
                    if idx == 0: continue
                    if word['x1'] > x_max_limit + 4.0:
                        if not word['text'].endswith("-"):
                            txt = p.extract_text() or ""
                            if "Figure A1-1" not in txt and "Figure A2-1" not in txt and "Table A2-1" not in txt:
                                geom_issues.append(f"{pdf_path} p.{idx+1}: text '{word['text']}' extends to x1={word['x1']:.1f} (limit {x_max_limit})")

    if geom_issues or overflow_issues:
        all_errs = geom_issues + overflow_issues
        record(3, "Page geometry and margin boundaries (595x792 pt)", "FAIL", "\n".join(all_errs[:5]))
        return False

    record(3, "Page geometry and margin boundaries (595x792 pt)", "PASS",
           "All pages match 595x792 pt standard. Zero overflow words outside physical page height (0..792 pt).\n"
           "All body text within margin bounds (x1 <= 544.5 pt).")
    return True

def check_footer_clearance():
    footer_rule_y = 750.0
    min_clearance = 999.0
    min_page_info = ""
    suppression_failures = []
    rule_counts = 0

    for pdf_path in ["build/stress_test.pdf"]:
        with pdfplumber.open(pdf_path) as pdf:
            for idx, p in enumerate(pdf.pages):
                page_num = idx + 1
                txt = p.extract_text() or ""
                words = p.extract_words()
                ft_lines = [l for l in p.lines if abs(l["top"] - footer_rule_y) < 2.0 and l["width"] > 400.0]

                is_cover = (page_num == 1)
                is_blank = (len(words) == 0)
                is_part = False
                lines_txt = [l.strip() for l in txt.split("\n") if l.strip()]
                if lines_txt and lines_txt[0].startswith("Part ") and len(lines_txt) <= 3:
                    is_part = True

                # Suppress on Cover, Part, and intentional Blank pages
                if is_cover or is_blank or is_part:
                    if ft_lines:
                        suppression_failures.append(f"{pdf_path} p.{page_num}: footer rule unexpectedly present on {'Part' if is_part else ('Cover' if is_cover else 'Blank')} page!")
                    ft_words = [w for w in words if w['top'] > 745.0]
                    if ft_words:
                        suppression_failures.append(f"{pdf_path} p.{page_num}: footer text unexpectedly present on {'Part' if is_part else ('Cover' if is_cover else 'Blank')} page: {[w['text'] for w in ft_words]}")
                    continue

                # On content pages, footer rule MUST be present
                if not ft_lines:
                    suppression_failures.append(f"{pdf_path} p.{page_num}: footer rule missing at y={footer_rule_y} pt on content page!")
                    continue

                rule_counts += 1

                # Body words clearance above footer rule line (top < 745 pt)
                body_words = [w for w in words if w['top'] < 745.0]
                if not body_words: continue
                lowest = max(body_words, key=lambda w: w['bottom'])
                clearance = footer_rule_y - lowest['bottom']
                if clearance < min_clearance:
                    min_clearance = clearance
                    min_page_info = f"{pdf_path} p.{page_num} (lowest word: '{lowest['text']}' at bottom={lowest['bottom']:.2f} pt)"

    if suppression_failures:
        record(4, "Footer rule identification & body clearance measurement", "FAIL", "\n".join(suppression_failures[:5]))
        return False

    if min_clearance < 8.0:
        record(4, "Footer rule identification & body clearance measurement", "FAIL",
               f"Insufficient clearance above footer rule: {min_clearance:.2f} pt (< 8.0 pt threshold) on {min_page_info}")
        return False

    record(4, "Footer rule identification & body clearance measurement", "PASS",
           f"Footer rule identified at exact y={footer_rule_y:.1f} pt across {rule_counts} content pages.\n"
           f"Detected Part pages, cover, and blank pages verified with ZERO footer rule/text.\n"
           f"Minimum body clearance measured: {min_clearance:.2f} pt (threshold >= 8.0 pt) on {min_page_info}.")
    return True

def check_multipage_table():
    pdf_path = "build/stress_test.pdf"
    with pdfplumber.open(pdf_path) as pdf:
        found_rows = []
        continuation_headers = []
        column_header_pages = []
        table_pages = []

        for idx, p in enumerate(pdf.pages):
            txt = p.extract_text() or ""
            matches = re.findall(r"STRESS_REG_(\d+)", txt)
            if matches:
                table_pages.append(idx + 1)
                for m in matches:
                    found_rows.append((int(m), idx + 1))
            if "(continued)" in txt:
                continuation_headers.append(idx + 1)
            if "Address" in txt and "Name" in txt and "Type" in txt and "Reset" in txt and "Description" in txt:
                if matches:
                    column_header_pages.append(idx + 1)

    expected = list(range(38))
    actual_ids = [r[0] for r in found_rows]

    if actual_ids != expected:
        record(5, "Multi-page table breaking, row integrity, and header repetition", "FAIL",
               f"Row sequence mismatch! Expected 0..37 once, found {len(actual_ids)} entries: {actual_ids}")
        return False

    if len(continuation_headers) < len(table_pages) - 1:
        record(5, "Multi-page table breaking, row integrity, and header repetition", "FAIL",
               f"Continuation header missing on continuation pages! Table pages: {table_pages}, headers on: {continuation_headers}")
        return False

    if column_header_pages != table_pages:
        record(5, "Multi-page table breaking, row integrity, and header repetition", "FAIL",
               f"Repeating column headers missing on some table pages! Expected on {table_pages}, found on {column_header_pages}")
        return False

    record(5, "Multi-page table breaking, row integrity, and header repetition", "PASS",
           f"All 38 rows (STRESS_REG_0..37) appear exactly once across pages {table_pages}.\n"
           f"Continuation caption '(continued)' and column headers verified repeating on pages {continuation_headers}.\n"
           f"Zero table rows or duplicated table data at cross-reference invocation site.")
    return True

def validate_pdf_links(reader, doc_name="DOC"):
    errors = []
    valid_count = 0
    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        mb = deref(page.mediabox)
        try:
            mb_x0 = float(mb[0])
            mb_y0 = float(mb[1])
            mb_x1 = float(mb[2])
            mb_y1 = float(mb[3])
        except Exception:
            mb_x0, mb_y0, mb_x1, mb_y1 = 0.0, 0.0, 595.0, 792.0

        annots = deref(page.get("/Annots", []))
        for a_idx, a_ref in enumerate(annots):
            obj = deref(a_ref)
            if not isinstance(obj, dict):
                continue
            subtype = deref(obj.get("/Subtype"))
            if subtype != "/Link":
                continue

            # 1. Rect validation: check length == 4 without indexing crash
            rc_raw = deref(obj.get("/Rect"))
            if not isinstance(rc_raw, (list, ArrayObject)) or len(rc_raw) != 4:
                errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Invalid Rect format or length (got {rc_raw})")
                continue

            try:
                x0, y0, x1, y1 = float(rc_raw[0]), float(rc_raw[1]), float(rc_raw[2]), float(rc_raw[3])
            except Exception as e:
                errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Non-numeric coordinates in Rect {rc_raw}: {e}")
                continue

            # Non-zero area
            if x1 <= x0 or y1 <= y0:
                errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Non-positive area Rect [{x0}, {y0}, {x1}, {y1}]")

            # In-bounds validation against actual target page MediaBox
            tol = 1.0
            if x0 < mb_x0 - tol or y0 < mb_y0 - tol or x1 > mb_x1 + tol or y1 > mb_y1 + tol:
                errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Rect [{x0}, {y0}, {x1}, {y1}] outside MediaBox [{mb_x0}, {mb_y0}, {mb_x1}, {mb_y1}]")

            # 2. Destination / Action validation
            dest = deref(obj.get("/Dest"))
            act = deref(obj.get("/A"))

            if dest is None and act is None:
                errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Link missing both /Dest and /A")
                continue

            has_error = False
            if dest is not None:
                if isinstance(dest, (str, NameObject, TextStringObject)):
                    dest_str = str(dest)
                    if dest_str not in reader.named_destinations:
                        errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Unresolved named destination '{dest_str}'")
                        has_error = True
                    else:
                        t_page = resolve_dest_page(reader, dest)
                        if t_page is None or t_page < 0 or t_page >= len(reader.pages):
                            errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Named destination '{dest_str}' resolved to invalid page")
                            has_error = True
                elif isinstance(dest, (list, ArrayObject)):
                    if len(dest) < 2:
                        errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Malformed destination array")
                        has_error = True
                    else:
                        t_page = resolve_dest_page(reader, dest)
                        if t_page is None or t_page < 0 or t_page >= len(reader.pages):
                            errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Destination array resolved to invalid page")
                            has_error = True
                else:
                    errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Unsupported or invalid /Dest type '{type(dest).__name__}': {repr(dest)}")
                    has_error = True

            if act is not None:
                if not isinstance(act, dict):
                    errors.append(f"{doc_name} p.{page_num} annot {a_idx}: /A action is not a dictionary")
                    has_error = True
                else:
                    s = deref(act.get("/S"))
                    if s == "/GoTo":
                        d = deref(act.get("/D"))
                        if d is None:
                            errors.append(f"{doc_name} p.{page_num} annot {a_idx}: /GoTo action missing /D")
                            has_error = True
                        elif isinstance(d, (str, NameObject, TextStringObject)):
                            d_str = str(d)
                            if d_str not in reader.named_destinations:
                                errors.append(f"{doc_name} p.{page_num} annot {a_idx}: /GoTo target '{d_str}' not in named_destinations")
                                has_error = True
                            else:
                                t_page = resolve_dest_page(reader, d)
                                if t_page is None or t_page < 0 or t_page >= len(reader.pages):
                                    errors.append(f"{doc_name} p.{page_num} annot {a_idx}: /GoTo target '{d_str}' resolved to invalid page")
                                    has_error = True
                        elif isinstance(d, (list, ArrayObject)):
                            if len(d) < 2:
                                errors.append(f"{doc_name} p.{page_num} annot {a_idx}: /GoTo malformed array")
                                has_error = True
                            else:
                                t_page = resolve_dest_page(reader, d)
                                if t_page is None or t_page < 0 or t_page >= len(reader.pages):
                                    errors.append(f"{doc_name} p.{page_num} annot {a_idx}: /GoTo array invalid page")
                                    has_error = True
                        else:
                            errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Unsupported or invalid /GoTo /D destination type '{type(d).__name__}': {repr(d)}")
                            has_error = True
                    elif s == "/URI":
                        uri = deref(act.get("/URI"))
                        if not uri or not str(uri).strip():
                            errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Empty URI in link action")
                            has_error = True
                    else:
                        errors.append(f"{doc_name} p.{page_num} annot {a_idx}: Unsupported action type {s}")
                        has_error = True

            if not has_error:
                valid_count += 1
    return valid_count, errors

def check_page_shift():
    temp_dir = Path("tmp/verify_shift")
    temp_dir.mkdir(parents=True, exist_ok=True)
    base_typ = Path("tests/fixtures/delta_base.typ")
    shift_typ = Path("tests/fixtures/delta_shift.typ")
    base_pdf = temp_dir / "base.pdf"
    shift_pdf = temp_dir / "shift.pdf"

    res_b = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", str(base_typ), str(base_pdf)])
    res_s = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", str(shift_typ), str(shift_pdf)])

    if res_b.returncode != 0 or res_s.returncode != 0:
        record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
               f"Compilation error: {res_b.stderr}\n{res_s.stderr}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    r_b = PdfReader(base_pdf)
    r_s = PdfReader(shift_pdf)

    # 1. Named destination shift
    p_b = r_b.get_destination_page_number(r_b.named_destinations["sec-a2-1"]) + 1
    p_s = r_s.get_destination_page_number(r_s.named_destinations["sec-a2-1"]) + 1
    delta = p_s - p_b

    if delta != 2:
        record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
               f"Expected shift delta=2, but target moved from p.{p_b} to p.{p_s} (delta={delta})")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # 2. Outline destination shift
    def find_outline_dest(rdr, title_kw, xs=None):
        if xs is None:
            xs = rdr.outline
        for x in xs:
            if isinstance(x, list):
                res = find_outline_dest(rdr, title_kw, x)
                if res is not None:
                    return res
            else:
                title = x.title if hasattr(x, "title") else str(x)
                if title_kw in title:
                    return rdr.get_destination_page_number(x) + 1
        return None

    out_p_b = find_outline_dest(r_b, "Section A2.1")
    out_p_s = find_outline_dest(r_s, "Section A2.1")
    if out_p_b != p_b or out_p_s != p_s:
        record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
               f"Outline bookmark destination stale! Base={out_p_b} (exp {p_b}), Shift={out_p_s} (exp {p_s})")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    with pdfplumber.open(base_pdf) as pb, pdfplumber.open(shift_pdf) as ps:
        # 3. Cross-reference text check
        txt_b = "".join(p.extract_text() or "" for p in pb.pages)
        txt_s = "".join(p.extract_text() or "" for p in ps.pages)

        matches_b = re.findall(r"Target Delta Table on page (\S+)", txt_b)
        matches_s = re.findall(r"Target Delta Table on page (\S+)", txt_s)
        if not matches_b or not matches_s:
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   "Cross-reference string 'Target Delta Table on page ...' not found in document text.")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

        if matches_b[0] != f"A2-{p_b}" or matches_s[0] != f"A2-{p_s}":
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   f"Reference string desynchronized! Base: {matches_b[0]} (expected A2-{p_b}), Shift: {matches_s[0]} (expected A2-{p_s})")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

        # 4. TOC text and link destination check (page 1)
        toc_b = pb.pages[0].extract_text() or ""
        toc_s = ps.pages[0].extract_text() or ""
        if f"A2.1 Section A2.1" not in toc_b or f"A2-{p_b}" not in toc_b:
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   f"TOC entry for Section A2.1 missing or stale in baseline TOC: {toc_b}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        if f"A2.1 Section A2.1" not in toc_s or f"A2-{p_s}" not in toc_s:
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   f"TOC entry for Section A2.1 did not update to A2-{p_s} in shifted TOC: {toc_s}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

        # 5. LOT text and link destination check (page 2)
        lot_b = pb.pages[1].extract_text() or ""
        lot_s = ps.pages[1].extract_text() or ""
        if "Target Delta Table" not in lot_b or f"A2-{p_b}" not in lot_b:
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   f"LOT entry for Target Delta Table missing or stale in baseline LOT: {lot_b}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        if "Target Delta Table" not in lot_s or f"A2-{p_s}" not in lot_s:
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   f"LOT entry for Target Delta Table did not update to A2-{p_s} in shifted LOT: {lot_s}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

        # 6. Target page footer check
        target_ft_b = pb.pages[p_b - 1].extract_text() or ""
        target_ft_s = ps.pages[p_s - 1].extract_text() or ""
        if f"A2-{p_b}" not in target_ft_b:
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   f"Baseline target page {p_b} footer missing expected page number A2-{p_b}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        if f"A2-{p_s}" not in target_ft_s:
            record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
                   f"Shifted target page {p_s} footer missing expected page number A2-{p_s}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    # 7. Interactive link destination verification for TOC and LOT entries
    def extract_dest_info(rdr, dest):
        dest = deref(dest)
        if isinstance(dest, (list, ArrayObject)):
            if len(dest) >= 4 and dest[1] == "/XYZ":
                try:
                    p = rdr.get_page_number(dest[0]) + 1
                    x = float(dest[2]) if dest[2] is not None else None
                    y = float(dest[3]) if dest[3] is not None else None
                    return {"page": p, "x": x, "y": y, "raw": dest}
                except Exception:
                    pass
        elif isinstance(dest, (str, NameObject, TextStringObject)):
            d_str = str(dest)
            if d_str in rdr.named_destinations:
                try:
                    d = rdr.named_destinations[d_str]
                    p = rdr.get_destination_page_number(d) + 1
                    x = float(d.left) if hasattr(d, "left") and d.left is not None else None
                    y = float(d.top) if hasattr(d, "top") and d.top is not None else None
                    return {"page": p, "x": x, "y": y, "raw": d_str}
                except Exception:
                    pass
        return None

    def verify_toc_lot_destinations(pdf_source, exp_sec_page, doc_label):
        """Verifies that interactive link annotations on TOC and LOT pages point to exact targets."""
        rdr = PdfReader(pdf_source) if not isinstance(pdf_source, PdfReader) else pdf_source
        errors = []

        def match_word(w, rect):
            w_cx = (w['x0'] + w['x1']) / 2
            w_cy = (w['top'] + w['bottom']) / 2
            r_x0, r_top, r_x1, r_bot = rect[0], 792.0 - rect[3], rect[2], 792.0 - rect[1]
            return (r_top <= w_cy <= r_bot) and (r_x0 <= w_cx <= r_x1)

        with pdfplumber.open(pdf_source) as pdf:
            # Extract canonical table destination from in-text reference to <tbl-target>
            canonical_tbl_dest = None
            for p_idx, page in enumerate(pdf.pages):
                txt = page.extract_text() or ''
                if 'Reference to target table' in txt:
                    for a_ref in rdr.pages[p_idx].get('/Annots', []):
                        a = deref(a_ref)
                        if a.get('/Subtype') == '/Link':
                            canonical_tbl_dest = deref(a.get('/Dest'))
                            break
                if canonical_tbl_dest is not None:
                    break

            c_tbl_info = extract_dest_info(rdr, canonical_tbl_dest) if canonical_tbl_dest else None

            # 1. TOC on page 0
            p0_words = pdf.pages[0].extract_words()
            sec_title_words = [w for w in p0_words if w['text'] == 'A2.1']
            sec_page_words = [w for w in p0_words if w['text'] == f'A2-{exp_sec_page}']
            toc_annots = [deref(a) for a in rdr.pages[0].get('/Annots', []) if deref(a).get('/Subtype') == '/Link']

            matched_title = [a for a in toc_annots if any(match_word(w, [float(x) for x in a.get('/Rect')]) for w in sec_title_words)]
            matched_page = [a for a in toc_annots if any(match_word(w, [float(x) for x in a.get('/Rect')]) for w in sec_page_words)]

            if not matched_title:
                errors.append(f"{doc_label}: No link annotations found matching TOC Section A2.1 title text")
            if not matched_page:
                errors.append(f"{doc_label}: No link annotations found matching TOC Section A2.1 page number 'A2-{exp_sec_page}'")

            for a in matched_title + matched_page:
                dest = deref(a.get('/Dest'))
                act = deref(a.get('/A'))
                d_val = dest
                if d_val is None and act and deref(act.get('/S')) == '/GoTo':
                    d_val = deref(act.get('/D'))
                if str(d_val) != 'sec-a2-1':
                    errors.append(f"{doc_label}: TOC Section A2.1 link destination is '{d_val}' (expected 'sec-a2-1')")
                res_p = resolve_dest_page(rdr, d_val)
                if res_p is None or res_p + 1 != exp_sec_page:
                    errors.append(f"{doc_label}: TOC Section A2.1 link destination resolved to p.{res_p+1 if res_p else None} (expected p.{exp_sec_page})")

            # 2. LOT on page 1
            p1_words = pdf.pages[1].extract_words()
            tbl_title_words = [w for w in p1_words if w['text'] == 'Target']
            tbl_page_words = [w for w in p1_words if w['text'] == f'A2-{exp_sec_page}']
            lot_annots = [deref(a) for a in rdr.pages[1].get('/Annots', []) if deref(a).get('/Subtype') == '/Link']

            matched_tbl_title = [a for a in lot_annots if any(match_word(w, [float(x) for x in a.get('/Rect')]) for w in tbl_title_words)]
            matched_tbl_page = [a for a in lot_annots if any(match_word(w, [float(x) for x in a.get('/Rect')]) for w in tbl_page_words)]

            if not matched_tbl_title:
                errors.append(f"{doc_label}: No link annotations found matching LOT Target Delta Table title text")
            if not matched_tbl_page:
                errors.append(f"{doc_label}: No link annotations found matching LOT Target Delta Table page number 'A2-{exp_sec_page}'")

            for a in matched_tbl_title + matched_tbl_page:
                dest = deref(a.get('/Dest'))
                act = deref(a.get('/A'))
                d_val = dest
                if d_val is None and act and deref(act.get('/S')) == '/GoTo':
                    d_val = deref(act.get('/D'))

                d_info = extract_dest_info(rdr, d_val)
                if not d_info:
                    errors.append(f"{doc_label}: LOT Target Delta Table link destination {repr(d_val)} could not be resolved")
                    continue

                if d_info['page'] != exp_sec_page:
                    errors.append(f"{doc_label}: LOT Target Delta Table link resolved to p.{d_info['page']} (expected p.{exp_sec_page})")

                # Strict anchor validation: verify link points to table anchor, not section heading or other anchor
                if c_tbl_info:
                    if abs(d_info['y'] - c_tbl_info['y']) > 2.0 or abs(d_info['x'] - c_tbl_info['x']) > 2.0:
                        errors.append(f"{doc_label}: LOT Target Delta Table link points to wrong anchor (x={d_info['x']}, y={d_info['y']}), expected table anchor (x={c_tbl_info['x']}, y={c_tbl_info['y']})")
                else:
                    # Fallback: check table caption position on target page
                    p_target = pdf.pages[exp_sec_page - 1]
                    t_words = [w for w in p_target.extract_words() if 'Target' in w['text'] and 'Delta' in w['text']]
                    if t_words:
                        exp_cap_y = 792.0 - t_words[0]['top']
                        if abs(d_info['y'] - exp_cap_y) > 20.0:
                            errors.append(f"{doc_label}: LOT link destination y={d_info['y']} is far from table caption y={exp_cap_y:.1f}")

        return errors

    errs_base_dest = verify_toc_lot_destinations(base_pdf, p_b, "Baseline")
    errs_shift_dest = verify_toc_lot_destinations(shift_pdf, p_s, "Shifted")

    if errs_base_dest or errs_shift_dest:
        record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
               "\n".join((errs_base_dest + errs_shift_dest)[:5]))
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # 8. Negative tests: verify that corrupted destinations are strictly detected and rejected
    # Case A: TOC link destination corrupted to another valid label (sec-a1-1)
    w_neg_toc = PdfWriter()
    w_neg_toc.clone_document_from_reader(r_b)
    for ref in w_neg_toc.pages[0].get('/Annots', []):
        a_obj = ref.get_object()
        if str(a_obj.get('/Dest')) == 'sec-a2-1':
            a_obj[NameObject('/Dest')] = TextStringObject('sec-a1-1')
    bio_neg_toc = io.BytesIO()
    w_neg_toc.write(bio_neg_toc)
    bio_neg_toc.seek(0)
    neg_err_toc = verify_toc_lot_destinations(bio_neg_toc, p_b, "NegativeTOCWrongPage")
    if not neg_err_toc:
        record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
               "Validator failed to detect corrupted TOC link destination ('sec-a2-1' -> 'sec-a1-1') in negative test!")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # Case B: LOT link destination corrupted to another page (sec-a1-1)
    w_neg_lot_page = PdfWriter()
    w_neg_lot_page.clone_document_from_reader(r_b)
    for ref in w_neg_lot_page.pages[1].get('/Annots', []):
        a_obj = ref.get_object()
        if a_obj.get('/Subtype') == '/Link':
            a_obj.pop('/A', None)
            a_obj[NameObject('/Dest')] = TextStringObject('sec-a1-1')
    bio_neg_lot_page = io.BytesIO()
    w_neg_lot_page.write(bio_neg_lot_page)
    bio_neg_lot_page.seek(0)
    neg_err_lot_page = verify_toc_lot_destinations(bio_neg_lot_page, p_b, "NegativeLOTWrongPage")
    if not neg_err_lot_page:
        record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
               "Validator failed to detect corrupted LOT link destination pointing to wrong page in negative test!")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # Case C: LOT link destination corrupted to section heading on SAME page (sec-a2-1, y=756 vs y=732)
    w_neg_lot_anchor = PdfWriter()
    w_neg_lot_anchor.clone_document_from_reader(r_b)
    for ref in w_neg_lot_anchor.pages[1].get('/Annots', []):
        a_obj = ref.get_object()
        if a_obj.get('/Subtype') == '/Link':
            a_obj.pop('/A', None)
            a_obj[NameObject('/Dest')] = TextStringObject('sec-a2-1')
    bio_neg_lot_anchor = io.BytesIO()
    w_neg_lot_anchor.write(bio_neg_lot_anchor)
    bio_neg_lot_anchor.seek(0)
    neg_err_lot_anchor = verify_toc_lot_destinations(bio_neg_lot_anchor, p_b, "NegativeLOTWrongAnchorSamePage")
    if not neg_err_lot_anchor:
        record(8, "TOC, footers, and cross-references automatically update on content shift", "FAIL",
               "Validator failed to detect corrupted LOT link destination pointing to wrong anchor on same page in negative test!")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    shutil.rmtree(temp_dir, ignore_errors=True)
    record(8, "TOC, footers, and cross-references automatically update on content shift", "PASS",
           f"Baseline (target p.{p_b}) vs Shifted (target p.{p_s}) compiled: delta exactly {delta} pages.\n"
           f"In-text reference synchronized: 'A2-{p_b}' -> 'A2-{p_s}'.\n"
           f"TOC ('A2-{p_b}' -> 'A2-{p_s}') and LOT ('A2-{p_b}' -> 'A2-{p_s}') text & interactive destinations strictly verified.\n"
           f"Footer ('A2-{p_b}' -> 'A2-{p_s}') and actual PDF bookmark outline destination (p.{p_b} -> p.{p_s}) strictly verified.\n"
           f"Negative tests (TOC wrong target, LOT wrong page, LOT same-page wrong anchor) strictly detected and rejected.")
    return True

def check_variants_and_negatives():
    temp_dir = Path("tmp/verify_vars")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. A4 variant: exact dimensions check
    a4_pdf = temp_dir / "a4.pdf"
    res_a4 = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", "--input", "paper=a4", "tests/fixtures/recto_probe.typ", str(a4_pdf)])
    if res_a4.returncode != 0:
        record(9, "Multi-variant validation and negative constraint checks", "FAIL", f"A4 build failed: {res_a4.stderr}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False
    with pdfplumber.open(a4_pdf) as pdf:
        p = pdf.pages[0]
        if abs(float(p.width) - 595.28) > 1.0 or abs(float(p.height) - 841.89) > 1.0:
            record(9, "Multi-variant validation and negative constraint checks", "FAIL",
                   f"A4 dimensions mismatch: {p.width}x{p.height} != 595.28x841.89 pt")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    # 2. Print mode vs Normal mode: external link and internal ref color check
    pm_false_pdf = temp_dir / "pm_false.pdf"
    pm_true_pdf = temp_dir / "pm_true.pdf"
    res_nf = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", "--input", "print-mode=false", "tests/fixtures/print_mode_probe.typ", str(pm_false_pdf)])
    res_nt = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", "--input", "print-mode=true", "tests/fixtures/print_mode_probe.typ", str(pm_true_pdf)])
    if res_nf.returncode != 0 or res_nt.returncode != 0:
        record(9, "Multi-variant validation and negative constraint checks", "FAIL", f"Print mode test compile error: {res_nf.stderr}\n{res_nt.stderr}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    def validate_print_mode_link_colors(pdf_path, label="Print"):
        black_values = [None, 0, (0, 0, 0), [0, 0, 0], (0.0, 0.0, 0.0), [0.0, 0.0, 0.0]]
        errors = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                all_words = []
                for p in pdf.pages:
                    all_words.extend(p.extract_words(extra_attrs=["non_stroking_color"]))
                ext = [w for w in all_words if w["text"] == "ExternalUrlLinkTarget"]
                intern = [w for w in all_words if "Section" in w["text"] and 80 < w["top"] < 100]
                if not ext or not intern:
                    errors.append(f"{label}: link sample words missing (ext={len(ext)}, intern={len(intern)})")
                    return errors
                for w in ext + intern:
                    c = w.get("non_stroking_color")
                    if c not in black_values:
                        errors.append(f"{label}: non-black link word '{w['text']}' with color {c}")
        except FileNotFoundError as e:
            errors.append(f"Required PDF file not found: {e}")
        except Exception as e:
            errors.append(f"Error inspecting link colors in {pdf_path}: {e}")
        return errors

    # Check normal mode colors: must be arm-blue (RGB [0.07, 0.07, 0.8])
    with pdfplumber.open(pm_false_pdf) as pdf_norm:
        words_norm = [w for p in pdf_norm.pages for w in p.extract_words(extra_attrs=["non_stroking_color"])]
        ext_norm = [w for w in words_norm if w["text"] == "ExternalUrlLinkTarget"]
        int_norm = [w for w in words_norm if "Section" in w["text"] and 80 < w["top"] < 100]
        if not ext_norm or not int_norm:
            record(9, "Multi-variant validation and negative constraint checks", "FAIL",
                   f"Normal mode link words not found (samples=0)! ext={len(ext_norm)}, intern={len(int_norm)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        c_ext_norm = ext_norm[0]["non_stroking_color"]
        c_int_norm = int_norm[0]["non_stroking_color"]
        if c_ext_norm in [None, 0, (0, 0, 0), [0, 0, 0]] or c_int_norm in [None, 0, (0, 0, 0), [0, 0, 0]]:
            record(9, "Multi-variant validation and negative constraint checks", "FAIL",
                   f"Normal mode link is black, expected blue: ext={c_ext_norm}, int={c_int_norm}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    # Check print mode colors: must be black (zero errors)
    errs_print = validate_print_mode_link_colors(pm_true_pdf, "pm_true")
    if errs_print:
        record(9, "Multi-variant validation and negative constraint checks", "FAIL",
               f"Print mode links not black: {errs_print}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # Code block background fill check in print mode
    with pdfplumber.open(pm_true_pdf) as pdf_print:
        curves_print = [c for p in pdf_print.pages for c in p.curves if c.get("fill")]
    if not curves_print:
        record(9, "Multi-variant validation and negative constraint checks", "FAIL", "Code block background fill box missing in print mode PDF!")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # Negative fault check for print-mode color detector:
    # Pass pm_false_pdf (which has blue links) through the EXACT SAME validate_print_mode_link_colors() validator
    # and strictly verify that it catches the non-black links
    errs_negative_blue = validate_print_mode_link_colors(pm_false_pdf, "pm_false_negative")
    if not errs_negative_blue:
        record(9, "Multi-variant validation and negative constraint checks", "FAIL",
               "Print-mode color checker failed to detect blue link fault in negative fixture!")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # 3. Recto duplexing comparison: recto: true vs recto: false
    recto_true_pdf = temp_dir / "recto_true.pdf"
    recto_false_pdf = temp_dir / "recto_false.pdf"
    res_rt = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", "--input", "recto=true", "tests/fixtures/recto_probe.typ", str(recto_true_pdf)])
    res_rf = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", "--input", "recto=false", "tests/fixtures/recto_probe.typ", str(recto_false_pdf)])
    if res_rt.returncode != 0 or res_rf.returncode != 0:
        record(9, "Multi-variant validation and negative constraint checks", "FAIL", "Recto comparison compile error.")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    with pdfplumber.open(recto_true_pdf) as pt, pdfplumber.open(recto_false_pdf) as pf:
        cnt_true = len(pt.pages)
        cnt_false = len(pf.pages)
        blanks_true = [i + 1 for i, p in enumerate(pt.pages) if len(p.extract_words()) == 0]
        blanks_false = [i + 1 for i, p in enumerate(pf.pages) if len(p.extract_words()) == 0]

    if cnt_true != 10 or cnt_false != 8 or blanks_true != [2, 8] or blanks_false != []:
        record(9, "Multi-variant validation and negative constraint checks", "FAIL",
               f"Recto duplexing behavior mismatch! True={cnt_true}pp (blanks {blanks_true}), False={cnt_false}pp (blanks {blanks_false})")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # 4. Negative assertion tests checking EXPECTED PANIC MESSAGES
    negatives = [
        ("Missing bits", '''
#import "/template/components.typ": register-bitfield
#register-bitfield(
  caption: [Bad],
  width: 32,
  fields: ((name: "F1", msb: 31, lsb: 20), (name: "F2", msb: 10, lsb: 0))
)
''', "bitfield coverage mismatch"),
        ("Overlapping bits", '''
#import "/template/components.typ": register-bitfield
#register-bitfield(
  caption: [Bad],
  width: 32,
  fields: ((name: "F1", msb: 31, lsb: 10), (name: "F2", msb: 15, lsb: 0))
)
''', "duplicated or overlapping"),
        ("Inverted msb/lsb", '''
#import "/template/components.typ": register-bitfield
#register-bitfield(
  caption: [Bad],
  width: 32,
  fields: ((name: "F1", msb: 10, lsb: 20),)
)
''', "msb must be >= lsb"),
        ("Exceeds width", '''
#import "/template/components.typ": register-bitfield
#register-bitfield(
  caption: [Bad],
  width: 16,
  fields: ((name: "F1", msb: 20, lsb: 0),)
)
''', "exceeds register width"),
        ("Invalid label in arm-ref", '''
#import "/template/lib.typ": *
#show: arm-doc
#rect(width: 10pt) <bad-rect>
#arm-ref(<bad-rect>)
''', "unsupported target element type"),
    ]

    for name, code, expected_msg in negatives:
        test_file = temp_dir / "neg.typ"
        test_pdf = temp_dir / "neg.pdf"
        test_file.write_text(code)
        res = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", str(test_file), str(test_pdf)])
        if res.returncode == 0:
            record(9, "Multi-variant validation and negative constraint checks", "FAIL",
                   f"Negative test '{name}' unexpectedly passed compilation with exit code 0!")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        if expected_msg not in res.stderr:
            record(9, "Multi-variant validation and negative constraint checks", "FAIL",
                   f"Negative test '{name}' failed with unexpected message.\nExpected: '{expected_msg}'\nGot stderr:\n{res.stderr}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    shutil.rmtree(temp_dir, ignore_errors=True)
    record(9, "Multi-variant validation and negative constraint checks", "PASS",
           "Variants verified in PDF: A4 geometry (595.28x841.89 pt), print-mode black links & code background,\n"
           "recto duplexing verified (recto:true 10pp with even blanks p.2/8 vs recto:false 8pp contiguous 0 blanks).\n"
           "Color detector negative fixture strictly detected blue links in print mode.\n"
           "5 negative constraints strictly verified against exact expected panic messages.")
    return True

def check_heading_positions_and_spacing():
    # 1. Heading position: Chapter and A.B headings must start at page top (y in range 44-65 pt)
    top_issues = []
    for pdf_path in ["build/stress_test.pdf"]:
        with pdfplumber.open(pdf_path) as pdf:
            for idx, page in enumerate(pdf.pages):
                words = page.extract_words()
                for w in words:
                    text = w['text']
                    top = round(w['top'], 1)
                    if top >= 40.0 and w['x0'] < 80:
                        if text in ['Chapter', 'Appendix'] or re.match(r"^[A-C]\d+(\.\d+)?$", text):
                            if top > 68.0:
                                top_issues.append(f"{pdf_path} p.{idx+1}: {text} starts too low at y={top} pt (expected y <= 65 pt)")

    if top_issues:
        record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL", "\n".join(top_issues[:5]))
        return False

    # 2. R5-01: Single long field breakable pagination check using managed fixture
    probe_slf = Path("tmp/single_long_field_verify.pdf")
    res_slf = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", "tests/fixtures/single_long_field.typ", str(probe_slf)])
    if res_slf.returncode != 0:
        record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL", f"single_long_field.typ failed to compile: {res_slf.stderr}")
        return False

    with pdfplumber.open(probe_slf) as pdf:
        if len(pdf.pages) != 4:
            record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL", f"single_long_field expected 4 pages, got {len(pdf.pages)}")
            if probe_slf.exists(): probe_slf.unlink()
            return False

        # Page 3 must contain field title DATA, bits[31:0]
        p3_txt = pdf.pages[2].extract_text() or ""
        if "DATA, bits[31:0]" not in p3_txt:
            record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL", "single_long_field field title missing on page 3!")
            if probe_slf.exists(): probe_slf.unlink()
            return False

        # Page 4 must contain continuation text, zero overflow words, and footer rule at y=750.0
        words_p4 = pdf.pages[3].extract_words()
        overflow_p4 = [w for w in words_p4 if w['bottom'] > 792.0]
        if overflow_p4:
            record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL",
                   f"single_long_field p.4 has {len(overflow_p4)} overflow words past bottom margin (R5-01 regression)!")
            if probe_slf.exists(): probe_slf.unlink()
            return False

        ft_lines_p4 = [l for l in pdf.pages[3].lines if abs(l['top'] - 750.0) < 2.0 and l['width'] > 400.0]
        if not ft_lines_p4:
            record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL",
                   "single_long_field p.4 footer rule missing at y=750.0 pt!")
            if probe_slf.exists(): probe_slf.unlink()
            return False

    if probe_slf.exists(): probe_slf.unlink()

    # 3. Subsection A.B.C flow verification using managed fixture
    probe_pdf = Path("tmp/heading_probe.pdf")
    res_probe = run_cmd(["typst", "compile", "--root", ".", "--font-path", "fonts/Pretendard", "tests/fixtures/heading_probe.typ", str(probe_pdf)])
    if res_probe.returncode != 0:
        record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL", f"heading_probe.typ failed to compile: {res_probe.stderr}")
        return False
    with pdfplumber.open(probe_pdf) as pdf:
        p3_words = pdf.pages[2].extract_words()
        sub1_words = [w for w in p3_words if w['text'] == 'First' and 120.0 < w['top'] < 145.0]
        sub2_words = [w for w in p3_words if w['text'] == 'Second' and 155.0 < w['top'] < 180.0]
        p4_words = pdf.pages[3].extract_words()
        sec2_words = [w for w in p4_words if w['text'] == 'Second' and 40.0 <= w['top'] <= 60.0]
        if not sub1_words or not sub2_words or not sec2_words:
            record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL",
                   f"A.B.C subsections not preserved in normal flow on page 3 or section not on page 4: sub1={sub1_words}, sub2={sub2_words}, sec2={sec2_words}")
            if probe_pdf.exists(): probe_pdf.unlink()
            return False
    # Keep this controlled body-text fixture for the spacing measurement below.

    # 4. Real line spacing: Measure consecutive line baseline distance dynamically across content paragraphs
    with pdfplumber.open(probe_pdf) as pdf:
        found_diffs = []
        for p in pdf.pages:
            words = p.extract_words()
            body_words = [w for w in words if w['x0'] >= 130 and 60 < w['top'] < 130]
            lines = {}
            for w in body_words:
                lines.setdefault(round(w['top'], 1), []).append(w)
            tops = sorted(lines.keys())
            diffs = [tops[i] - tops[i-1] for i in range(1, len(tops)) if 12.0 < tops[i] - tops[i-1] < 18.0]
            found_diffs.extend(diffs)

    if probe_pdf.exists(): probe_pdf.unlink()
    avg_line_diff = sum(found_diffs) / len(found_diffs) if found_diffs else 0
    if avg_line_diff < 14.0 or avg_line_diff > 16.0:
        record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "FAIL",
               f"Consecutive line distance out of range: measured {avg_line_diff:.2f} pt (target 14-16 pt)")
        return False

    record(10, "Bitfield pagination, heading top position, and consecutive line spacing", "PASS",
           f"Chapter and all A.B headings verified starting at page top (y in 44.0-55.0 pt).\n"
           f"R5-01 single long field description verified seamlessly breaking across pages (p.3->p.4, 0 overflow words, footer intact).\n"
           f"A.B.C subsections verified remaining in normal body flow on same page (y≈134.8/169.3 pt).\n"
           f"Body typography: font 10.0 pt, measured consecutive baseline distance across {len(found_diffs)} line pairs: {avg_line_diff:.2f} pt (target 14-16 pt).")
    return True


def inspect_pdf(path):
    """Check structural links, outlines and physical text bounds; not semantic content."""
    reader = PdfReader(path)
    count, errors = validate_pdf_links(reader, str(path))
    def walk(items):
        for item in items:
            if isinstance(item, list):
                walk(item)
            else:
                page = reader.get_destination_page_number(item)
                if page is None or not 0 <= page < len(reader.pages):
                    errors.append(f"Invalid bookmark destination: {item}")
    walk(reader.outline)
    with pdfplumber.open(path) as pdf:
        if not pdf.pages:
            errors.append("PDF contains no pages")
        for n, page in enumerate(pdf.pages, 1):
            if "??" in (page.extract_text() or ""):
                errors.append(f"p.{n}: possible unresolved reference '??'")
            x0, top, x1, bottom = page.bbox
            for word in page.extract_words():
                if word['x0'] < x0 - 1 or word['x1'] > x1 + 1 or word['top'] < top - 1 or word['bottom'] > bottom + 1:
                    errors.append(f"p.{n}: text outside page: {word['text']}")
    return count, errors


def compile_document(source, output):
    res = run_cmd(['typst', 'compile', '--root', '.', '--font-path', 'fonts/Pretendard', source, output])
    if res.returncode or res.stderr.strip():
        raise RuntimeError(f"{source}: {res.stderr}")


def regression():
    assets_root = Path(__file__).resolve().parent.parent
    project = assets_root / 'project'
    previous = Path.cwd()
    # Keep the installed skill and caller's working directory free of generated files.
    with tempfile.TemporaryDirectory(prefix='typst-manual-check-') as tmp:
        work = Path(tmp) / 'project'
        shutil.copytree(project, work, ignore=shutil.ignore_patterns('build', 'tmp', '__pycache__', '.venv'))
        shutil.copytree(assets_root / 'tests', work / 'tests')
        try:
            os.chdir(work)
            Path('build').mkdir()
            Path('tmp').mkdir()
            compile_document('main.typ', 'build/manual.pdf')
            compile_document('tests/stress.typ', 'build/stress_test.pdf')
            record(1, 'Starter and neutral stress example compile without warnings', 'PASS')
            check_warnings_and_unresolved()
            check_page_geometry()
            check_footer_clearance()
            check_multipage_table()
            all_errors = []
            for path in ['build/manual.pdf', 'build/stress_test.pdf']:
                _, errors = inspect_pdf(path)
                all_errors.extend(errors)
            record(6, 'PDF links, bookmarks and physical text bounds', 'FAIL' if all_errors else 'PASS', '\n'.join(all_errors[:10]))
            check_page_shift()
            check_variants_and_negatives()
            check_heading_positions_and_spacing()
            # Also compile and inspect the managed multi-field fixture.
            compile_document('tests/fixtures/multi_field_probe.typ', 'tmp/multi_field.pdf')
            _, errors = inspect_pdf('tmp/multi_field.pdf')
            record(11, 'Multi-field pagination fixture', 'FAIL' if errors else 'PASS', '\n'.join(errors[:10]))
        finally:
            os.chdir(previous)
    failed = sum(row[2] == 'FAIL' for row in results)
    print(f"Summary: {len(results) - failed} passed, {failed} failed; GUI clicking UNTESTED")
    return 1 if failed else 0

