#!/usr/bin/env python3
"""Audit the historical PAR2 V1 project without modifying historical files.

The audit deliberately uses only the Python standard library so it can run
before RDKit/GNINA/ProLIF are installed.  It writes new summaries below
YONSEI_FINAL10_V2/00_AUDIT and never rewrites any V1 input or result.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def read_table(path: Path, delimiter: str | None = None) -> list[dict[str, str]]:
    if delimiter is None:
        delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def count_sdf_records(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    return text.count("$$$$")


def sdf_inventory(root: Path, directory: Path) -> dict[str, int]:
    files = sorted(directory.rglob("*.sdf")) if directory.exists() else []
    return {
        "files": len(files),
        "nonempty_files": sum(path.stat().st_size > 0 for path in files),
        "records": sum(count_sdf_records(path) for path in files),
    }


def parse_pdb_atom(line: str) -> tuple[str, str, tuple[float, float, float]] | None:
    if not line.startswith(("ATOM", "HETATM")):
        return None
    try:
        xyz = tuple(float(line[start : start + 8]) for start in (30, 38, 46))
    except ValueError:
        return None
    residue = line[17:20].strip()
    element = line[76:78].strip() or re.sub(r"[^A-Za-z]", "", line[12:16])
    return residue, element.upper(), xyz


def centroid_and_dimensions(points: list[tuple[float, float, float]]) -> dict:
    if not points:
        return {"atom_count": 0, "centroid_x": None, "centroid_y": None, "centroid_z": None,
                "min_x": None, "min_y": None, "min_z": None, "max_x": None, "max_y": None,
                "max_z": None, "span_x": None, "span_y": None, "span_z": None}
    centroid = tuple(sum(point[i] for point in points) / len(points) for i in range(3))
    minimum = tuple(min(point[i] for point in points) for i in range(3))
    maximum = tuple(max(point[i] for point in points) for i in range(3))
    return {
        "atom_count": len(points),
        "centroid_x": centroid[0], "centroid_y": centroid[1], "centroid_z": centroid[2],
        "min_x": minimum[0], "min_y": minimum[1], "min_z": minimum[2],
        "max_x": maximum[0], "max_y": maximum[1], "max_z": maximum[2],
        "span_x": maximum[0] - minimum[0], "span_y": maximum[1] - minimum[1],
        "span_z": maximum[2] - minimum[2],
    }


def benchmark_audit(path: Path, expected_residue: str) -> dict:
    all_atoms = []
    ligand_atoms = []
    residue_counts = Counter()
    element_counts = Counter()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parsed = parse_pdb_atom(line)
        if parsed is None:
            continue
        residue, element, xyz = parsed
        all_atoms.append(xyz)
        residue_counts[residue] += 1
        element_counts[element] += 1
        if residue == expected_residue:
            ligand_atoms.append((element, xyz))
    heavy = [xyz for element, xyz in ligand_atoms if element not in {"H", "D"}]
    ligand_residue_counts = Counter(element for element, _ in ligand_atoms)
    return {
        "file": str(path),
        "exists": path.exists(),
        "all_hetatm_atom_count": len(all_atoms),
        "ligand_residue": expected_residue,
        "ligand_atom_count": len(ligand_atoms),
        "ligand_heavy_atom_count": len(heavy),
        "ligand_elements": dict(sorted(ligand_residue_counts.items())),
        "non_ligand_residues": dict(sorted((key, value) for key, value in residue_counts.items()
                                             if key != expected_residue)),
        "all_hetatm_elements": dict(sorted(element_counts.items())),
        "ligand_heavy_geometry": centroid_and_dimensions(heavy),
    }


def parse_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def numeric(config: dict[str, str], key: str) -> float | None:
    try:
        return float(config[key])
    except (KeyError, TypeError, ValueError):
        return None


def config_audit(path: Path, benchmark: dict | None) -> dict:
    values = parse_config(path)
    result: dict[str, object] = {"file": str(path), "exists": path.exists(), "values": values}
    if not values:
        result["issues"] = ["configuration file missing or empty"]
        return result
    receptor_ref = values.get("receptor", "")
    receptor_path = (path.parent / receptor_ref).resolve() if receptor_ref else None
    result["resolved_receptor_path"] = str(receptor_path) if receptor_path else None
    result["receptor_path_exists"] = bool(receptor_path and receptor_path.exists())
    issues: list[str] = []
    if receptor_path and not receptor_path.exists():
        issues.append("configured receptor path does not exist")
    if benchmark:
        geometry = benchmark["ligand_heavy_geometry"]
        center = [numeric(values, key) for key in ("center_x", "center_y", "center_z")]
        spans = [numeric(values, key) for key in ("size_x", "size_y", "size_z")]
        centroid = [geometry[f"centroid_{axis}"] for axis in ("x", "y", "z")]
        if all(value is not None for value in center):
            result["ligand_centroid_offset_config_minus_ligand"] = [
                center[i] - centroid[i] for i in range(3)
            ]
            result["center_to_ligand_centroid_angstrom"] = math.sqrt(
                sum((center[i] - centroid[i]) ** 2 for i in range(3))
            )
        if all(value is not None for value in spans):
            result["box_padding_each_side_from_heavy_bounds"] = [
                (spans[i] - geometry[f"span_{axis}"]) / 2 for i, axis in enumerate(("x", "y", "z"))
            ]
            result["historical_box_is_40_angstrom_cube"] = all(abs(value - 40.0) < 1e-6 for value in spans)
    if "cnn_scoring" in values:
        issues.append("historical configuration requests CNN rescoring; CNN values are ranking features")
    result["issues"] = issues
    return result


def row_key(row: dict[str, str], smiles_field: str = "SMILES") -> str:
    return (row.get("inchikey") or row.get("InChIKey") or row.get(smiles_field) or
            row.get("smiles") or row.get("mol_name") or row.get("Name") or "").strip()


def source_table_audit(root: Path) -> list[dict]:
    sources = [
        ("FDA_DRUGS", root / "SCREENING/FDA_DRUGS.csv", ",", "SMILES"),
        ("BLEACHING_APROVED", root / "SCREENING/BLEACHING_APROVED_clean.csv", ",", "SMILES"),
        ("MITF_SCAFFOLDS", root / "SCREENING/elite_mitf_scaffolds_clean.csv", ",", "Representative_SMILES"),
        ("NPATLAS", root / "SCREENING/NPATLAS.tsv", "\t", "smiles"),
        ("LOTUS", root / "SCREENING/LOTUS_2021_03.tsv", "\t", "smiles"),
        ("CHEMBL_PAR2_COMPOUNDS", root / "XGBOOST_RANDOM_FORREST/chembl_par2_raw_compounds.csv", ",", "smiles"),
    ]
    output = []
    for name, path, delimiter, smiles_column in sources:
        present = path.exists()
        rows = read_table(path, delimiter) if present else []
        output.append({
            "source": name,
            "path": str(path),
            "present": present,
            "row_count": len(rows),
            "column_count": len(rows[0]) if rows else 0,
            "smiles_column": smiles_column,
            "smiles_column_present": bool(rows and smiles_column in rows[0]),
            "nonempty_smiles_count": sum(bool(row.get(smiles_column, "").strip()) for row in rows),
        })
    return output


def file_inventory(directory: Path) -> list[dict]:
    rows = []
    if not directory.exists():
        return rows
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        text = path.read_text(encoding="utf-8", errors="replace")
        rows.append({
            "file": str(path),
            "bytes": path.stat().st_size,
            "suffix": suffix,
            "line_count": len(text.splitlines()),
            "sdf_record_count": text.count("$$$$") if suffix in {".sdf", ".mol"} else "",
        })
    return rows


def gnina_log_audit(log_dir: Path) -> dict:
    logs = sorted(log_dir.glob("*.log")) if log_dir.exists() else []
    stages = Counter()
    cnn_modes = Counter()
    commandline_count = 0
    no_gpu_warning_count = 0
    min_rmsd_filters = Counter()
    for path in logs:
        text = path.read_text(encoding="utf-8", errors="replace")
        stage = "P1" if path.name.startswith("P1_") else ("P2" if path.name.startswith("P2_") else "OTHER")
        stages[stage] += 1
        commandline_count += text.count("Commandline:")
        no_gpu_warning_count += int("No GPU detected" in text)
        modes = re.findall(r"--cnn_scoring(?:=|\s+)(\w+)", text)
        cnn_modes.update(modes)
        min_rmsd_filters.update(re.findall(r"--min_rmsd_filter\s+(\S+)", text))
    return {
        "log_file_count": len(logs),
        "logs_by_stage": dict(sorted(stages.items())),
        "commandline_count": commandline_count,
        "cnn_scoring_modes": dict(sorted(cnn_modes.items())),
        "no_gpu_warning_count": no_gpu_warning_count,
        "min_rmsd_filter_values": dict(sorted(min_rmsd_filters.items())),
    }


def pass2_audit(root: Path, pass1_rows: list[dict[str, str]]) -> dict:
    input_dir = root / "GNINA_SCREEN_EX32/PASS2_MOLS"
    output_dir = root / "GNINA_SCREEN_EX32/PASS2"
    input_files = sorted(input_dir.glob("*.sdf"))
    output_files = sorted(output_dir.glob("*.sdf"))
    linked = []
    all_pass1_text = [" ".join(row.values()).lower() for row in pass1_rows]
    for path in input_files:
        stem = path.stem.lower()
        tokens = [token for token in re.split(r"[_-]", stem) if len(token) >= 4]
        matches = sum(any(token in text for token in tokens) for text in all_pass1_text)
        linked.append({"file": str(path), "bytes": path.stat().st_size, "pass1_rows_containing_identifier": matches})
    output_by_box = Counter()
    for path in output_files:
        prefix = path.name.split("_", 1)[0]
        output_by_box[prefix] += 1
    expected_outputs = len(input_files) * 3
    nonempty_outputs = sum(path.stat().st_size > 0 for path in output_files)
    return {
        "input_file_count": len(input_files),
        "input_nonempty_file_count": sum(path.stat().st_size > 0 for path in input_files),
        "output_file_count": len(output_files),
        "expected_output_file_count_for_A_B_C": expected_outputs,
        "output_nonempty_file_count": nonempty_outputs,
        "output_files_by_box_prefix": dict(sorted(output_by_box.items())),
        "all_input_files_have_nonempty_sdf": bool(input_files) and all(path.stat().st_size > 0 for path in input_files),
        "all_expected_outputs_present": len(output_files) == expected_outputs,
        "all_outputs_nonempty": bool(output_files) and nonempty_outputs == len(output_files),
        "clean_historical_35_candidate_pass2_shortlist_exists": (
            len(input_files) == 35 and
            all(path.stat().st_size > 0 for path in input_files) and
            len(output_files) == expected_outputs and
            nonempty_outputs == len(output_files)
        ),
        "input_linkage": linked,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    out = root / "YONSEI_FINAL10_V2/00_AUDIT"
    out.mkdir(parents=True, exist_ok=True)

    pass1_path = root / "GNINA_SCREEN_EX32/pass1_all_hits.csv"
    final_path = root / "RESULTS/CNN_FINAL_SCORES.csv"
    pass1_rows = read_table(pass1_path)
    final_rows = read_table(final_path)

    pass1_unique = {row_key(row) for row in pass1_rows if row_key(row)}
    pass1_by_library = defaultdict(set)
    pass1_by_box = defaultdict(set)
    for row in pass1_rows:
        key = row_key(row)
        if key:
            pass1_by_library[row.get("library", "")].add(key)
            pass1_by_box[row.get("box", "")].add(key)

    source_counts = []
    for library in sorted(set(row.get("library", "") for row in pass1_rows)):
        rows = [row for row in pass1_rows if row.get("library", "") == library]
        source_counts.append({
            "library": library,
            "pass1_result_rows": len(rows),
            "unique_candidates": len(pass1_by_library[library]),
            "box_a_result_rows": sum(row.get("box") == "BoxA_orthosteric" for row in rows),
            "box_b_result_rows": sum(row.get("box") == "BoxB_allosteric" for row in rows),
            "box_a_unique_candidates": len({row_key(row) for row in rows if row.get("box") == "BoxA_orthosteric"}),
            "box_b_unique_candidates": len({row_key(row) for row in rows if row.get("box") == "BoxB_allosteric"}),
        })
    write_csv(out / "v1_source_library_counts.csv", source_counts, list(source_counts[0]))

    box_counts = []
    for box in sorted(set(row.get("box", "") for row in pass1_rows)):
        rows = [row for row in pass1_rows if row.get("box", "") == box]
        box_counts.append({
            "box": box,
            "result_rows": len(rows),
            "unique_candidates": len({row_key(row) for row in rows if row_key(row)}),
            "libraries": ";".join(sorted(set(row.get("library", "") for row in rows))),
        })
    write_csv(out / "v1_box_counts.csv", box_counts, list(box_counts[0]))

    final_by_key = defaultdict(list)
    for row in pass1_rows:
        for key in {row_key(row), row.get("SMILES", "").strip()} - {""}:
            final_by_key[key].append(row)
    linked_rows = []
    for row in final_rows:
        matches = final_by_key.get(row_key(row), []) or final_by_key.get(row.get("smiles", "").strip(), [])
        linked_rows.append({
            "rank": row.get("rank", ""),
            "mol_name": row.get("mol_name", ""),
            "current_source_library": row.get("source_library", ""),
            "current_binding_site": row.get("binding_site", ""),
            "original_library_from_pass1": ";".join(sorted(set(match.get("library", "") for match in matches))),
            "pass1_match_count": len(matches),
            "linked_to_pass1": bool(matches),
        })
    write_csv(out / "v1_final500_source_linkage.csv", linked_rows, list(linked_rows[0]))

    for n in (10, 50, 100, 500):
        rows = final_rows[:n]
        if rows:
            write_csv(out / f"V1_TOP{n}.csv", rows, list(rows[0]))

    benchmarks = {
        "5NDD_AZ8838": benchmark_audit(root / "BENCHMARK_LIGS/lig_AZ8838_orthosteric_boxA.pdb", "8TZ"),
        "5NDZ_AZ3451": benchmark_audit(root / "BENCHMARK_LIGS/lig_AZ3451_allosteric_boxB.pdb", "8UN"),
    }
    configs = {
        "BoxA_orthosteric": config_audit(root / "PROTEINS/CONF/boxA_orthosteric_5NDD.conf", benchmarks["5NDD_AZ8838"]),
        "BoxB_allosteric": config_audit(root / "PROTEINS/CONF/boxB_allosteric_5NDZ.conf", benchmarks["5NDZ_AZ3451"]),
    }
    benchmark_config_rows = []
    for name, benchmark in benchmarks.items():
        geometry = benchmark["ligand_heavy_geometry"]
        benchmark_config_rows.append({
            "system": name,
            "reference_ligand_file": benchmark["file"],
            "reference_residue": benchmark["ligand_residue"],
            "heavy_atom_count": benchmark["ligand_heavy_atom_count"],
            "centroid_x": geometry["centroid_x"], "centroid_y": geometry["centroid_y"], "centroid_z": geometry["centroid_z"],
            "span_x": geometry["span_x"], "span_y": geometry["span_y"], "span_z": geometry["span_z"],
            "non_ligand_species": json.dumps(benchmark["non_ligand_residues"], sort_keys=True),
            "config_file": configs["BoxA_orthosteric" if name.startswith("5NDD") else "BoxB_allosteric"]["file"],
            "config_receptor_path_exists": configs["BoxA_orthosteric" if name.startswith("5NDD") else "BoxB_allosteric"].get("receptor_path_exists", False),
            "center_to_ligand_centroid_angstrom": configs["BoxA_orthosteric" if name.startswith("5NDD") else "BoxB_allosteric"].get("center_to_ligand_centroid_angstrom", ""),
            "historical_box_sizes": ";".join(str(configs["BoxA_orthosteric" if name.startswith("5NDD") else "BoxB_allosteric"]["values"].get(key, "")) for key in ("size_x", "size_y", "size_z")),
        })
    write_csv(out / "benchmark_config_audit.csv", benchmark_config_rows, list(benchmark_config_rows[0]))

    receptor_inventory = []
    for path in sorted((root / "PROTEINS").rglob("*")):
        if path.is_file() and path.suffix.lower() in {".pdb", ".pdbqt", ".conf"}:
            atom_count = sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
                             if line.startswith(("ATOM", "HETATM")))
            receptor_inventory.append({"file": str(path), "bytes": path.stat().st_size, "atom_records": atom_count})
    write_csv(out / "receptor_and_config_inventory.csv", receptor_inventory, list(receptor_inventory[0]))

    sdf_dirs = [
        root / "GNINA_SCREEN_EX32/SDF_CHUNKS",
        root / "GNINA_SCREEN_EX32/PASS1/BoxA_orthosteric",
        root / "GNINA_SCREEN_EX32/PASS1/BoxB_allosteric",
        root / "GNINA_SCREEN_EX32/PASS2_MOLS",
        root / "GNINA_SCREEN_EX32/PASS2",
        root / "RESULTS",
    ]
    sdf_summary = [{"directory": str(path), **sdf_inventory(root, path)} for path in sdf_dirs]
    write_csv(out / "sdf_output_inventory.csv", sdf_summary, list(sdf_summary[0]))

    source_inputs = source_table_audit(root)
    write_csv(out / "screening_source_inventory.csv", source_inputs, list(source_inputs[0]))
    screening_files = file_inventory(root / "SCREENING")
    write_csv(out / "screening_file_inventory.csv", screening_files, list(screening_files[0]))

    historical_script = root / "PYTHON/GNINA.py"
    historical_script_text = historical_script.read_text(encoding="utf-8", errors="replace") if historical_script.exists() else ""
    expected_script_paths = [
        "SCREENING/SAFE_coconut_3D.sdf",
        "SCREENING/SAFE_coconut.csv",
        "SCREENING/LOTUS_2021_03_simple.sdf",
        "SCREENING/NPAtlas_download_2024_09.sdf",
        "GNINA_SCREEN_EX32/SDF_GENERATED/BLEACHING_3D.sdf",
    ]
    base_path_line = next((line.strip() for line in historical_script_text.splitlines() if line.strip().startswith("BASE") and "=" in line), "")
    base_path_match = re.search(r'Path\("([^"]+)"\)', base_path_line)
    hard_coded_base_path = base_path_match.group(1) if base_path_match else base_path_line.split("=", 1)[-1].strip().strip('"')
    script_path_audit = {
        "script": str(historical_script),
        "exists": historical_script.exists(),
        "hard_coded_base_path": hard_coded_base_path,
        "hard_coded_base_path_exists": Path(hard_coded_base_path).exists() if hard_coded_base_path else False,
        "referenced_library_paths": [{"path": str(root / value), "exists": (root / value).exists()} for value in expected_script_paths],
    }
    (out / "historical_script_path_audit.json").write_text(json.dumps(script_path_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log_summary = gnina_log_audit(root / "GNINA_SCREEN_EX32/LOGS")
    (out / "gnina_log_audit.json").write_text(json.dumps(log_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    pass2 = pass2_audit(root, pass1_rows)
    (out / "pass2_audit.json").write_text(json.dumps(pass2, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    final_top_summary = []
    for n in (10, 50, 100, 500):
        rows = final_rows[:n]
        final_top_summary.append({
            "top_n": n,
            "rows": len(rows),
            "libraries": dict(sorted(Counter(row.get("source_library", "") for row in rows).items())),
            "binding_sites": dict(sorted(Counter(row.get("binding_site", "") for row in rows).items())),
            "receptors": dict(sorted(Counter(row.get("receptor", "") for row in rows).items())),
        })

    findings = [
        f"Pass-1 contains {len(pass1_rows):,} result rows and {len(pass1_unique):,} unique row keys.",
        "Pass-1 result rows by box: " + ", ".join(f"{key}={value}" for key, value in sorted(Counter(row.get("box", "") for row in pass1_rows).items())) + ".",
        "Pass-1 result rows by source library: " + ", ".join(f"{key}={value}" for key, value in sorted(Counter(row.get("library", "") for row in pass1_rows).items())) + ".",
        "The final V1 ranking contains " + ", ".join(f"{key}={value}" for key, value in sorted(Counter(row.get("source_library", "") for row in final_rows).items())) + ".",
        "The final V1 ranking contains " + ", ".join(f"{key}={value}" for key, value in sorted(Counter(row.get("binding_site", "") for row in final_rows).items())) + ".",
        f"Final V1 rows not linked by exact InChIKey/SMILES to Pass-1: {sum(not row['linked_to_pass1'] for row in linked_rows)}.",
        f"Historical Pass-2 input files: {pass2['input_file_count']}; nonempty: {pass2['input_nonempty_file_count']}; output files: {pass2['output_file_count']}; nonempty outputs: {pass2['output_nonempty_file_count']}.",
        "The clean historical 35-candidate Pass-2 shortlist exists: " + str(pass2["clean_historical_35_candidate_pass2_shortlist_exists"]) + ".",
        "5NDD benchmark contains non-ligand residues: " + json.dumps(benchmarks["5NDD_AZ8838"]["non_ligand_residues"], sort_keys=True) + ".",
        "5NDZ benchmark contains non-ligand residues: " + json.dumps(benchmarks["5NDZ_AZ3451"]["non_ligand_residues"], sort_keys=True) + ".",
        "Historical Box A configured receptor exists: " + str(configs["BoxA_orthosteric"].get("receptor_path_exists", False)) + "; Box B configured receptor exists: " + str(configs["BoxB_allosteric"].get("receptor_path_exists", False)) + ".",
        "The historical GNINA driver hard-codes `/Users/mk/PycharmProjects/Pigment-Firewall-PAR2` rather than the checked-out repository path.",
        "Historical GNINA driver referenced paths missing from this checkout: " + ", ".join(item["path"] for item in script_path_audit["referenced_library_paths"] if not item["exists"]) + ".",
        "GNINA log command stages/modes: " + json.dumps(log_summary["logs_by_stage"], sort_keys=True) + " / " + json.dumps(log_summary["cnn_scoring_modes"], sort_keys=True) + ".",
    ]

    summary = {
        "audit_generated_utc": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(root),
        "historical_v1_inputs": {
            "pass1_file": str(pass1_path), "pass1_rows": len(pass1_rows), "pass1_columns": list(pass1_rows[0]) if pass1_rows else [],
            "pass1_unique_candidates_by_available_identifier": len(pass1_unique),
            "final_file": str(final_path), "final_rows": len(final_rows), "final_columns": list(final_rows[0]) if final_rows else [],
        },
        "pass1_result_rows_by_library": dict(sorted(Counter(row.get("library", "") for row in pass1_rows).items())),
        "pass1_result_rows_by_box": dict(sorted(Counter(row.get("box", "") for row in pass1_rows).items())),
        "pass1_unique_candidates_by_library": {key: len(value) for key, value in sorted(pass1_by_library.items())},
        "pass1_unique_candidates_by_box": {key: len(value) for key, value in sorted(pass1_by_box.items())},
        "final_v1_top_summaries": final_top_summary,
        "final_v1_missing_fields": {field: sum(not row.get(field, "").strip() for row in final_rows) for field in final_rows[0]},
        "final_v1_linkage": {
            "linked_rows": sum(row["linked_to_pass1"] for row in linked_rows),
            "unlinked_rows": sum(not row["linked_to_pass1"] for row in linked_rows),
        },
        "benchmarks": benchmarks,
        "configs": configs,
        "pass2": pass2,
        "screening_source_inventory": source_inputs,
        "receptor_and_config_file_count": len(receptor_inventory),
        "sdf_inventory": sdf_summary,
        "screening_file_inventory": screening_files,
        "historical_script_path_audit": script_path_audit,
        "gnina_log_audit": log_summary,
        "findings": findings,
    }
    (out / "V1_AUDIT_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# V1 audit",
        "",
        f"Generated: `{summary['audit_generated_utc']}`",
        "",
        "This audit reads historical files only and writes new files below `YONSEI_FINAL10_V2/00_AUDIT`. It does not overwrite V1 results.",
        "",
        "## Confirmed findings",
        "",
    ]
    lines.extend(f"- {finding}" for finding in findings)
    lines += [
        "",
        "## Current V1 ranking composition",
        "",
        "| Prefix | Rows | Source libraries | Binding sites |",
        "|---:|---:|---|---|",
    ]
    for item in final_top_summary:
        lines.append(f"| {item['top_n']} | {item['rows']} | `{json.dumps(item['libraries'], sort_keys=True)}` | `{json.dumps(item['binding_sites'], sort_keys=True)}` |")
    lines += [
        "",
        "## Current V1 top 10",
        "",
        "| Rank | Molecule | Library | Site | Vina affinity | CNN score | InChIKey |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for row in final_rows[:10]:
        lines.append("| {rank} | {mol_name} | {source_library} | {binding_site} | {vina_affinity} | {cnn_score} | {inchikey} |".format(**row))
    lines += [
        "",
        "## Benchmark/configuration audit",
        "",
        "The reference ligand geometry is calculated from the heavy atoms in the crystallographic ligand residue only. Non-ligand HETATM records are reported rather than silently retained.",
        "",
    ]
    for name, benchmark in benchmarks.items():
        geometry = benchmark["ligand_heavy_geometry"]
        config_name = "BoxA_orthosteric" if name.startswith("5NDD") else "BoxB_allosteric"
        config = configs[config_name]
        lines.append(f"- **{name}**: {benchmark['ligand_heavy_atom_count']} heavy atoms; centroid `({geometry['centroid_x']:.3f}, {geometry['centroid_y']:.3f}, {geometry['centroid_z']:.3f})`; spans `({geometry['span_x']:.3f}, {geometry['span_y']:.3f}, {geometry['span_z']:.3f}) Å`; non-ligand species `{json.dumps(benchmark['non_ligand_residues'], sort_keys=True)}`; configured receptor exists: `{config.get('receptor_path_exists', False)}`; config/centroid distance: `{config.get('center_to_ligand_centroid_angstrom', 'NA')}` Å.")
    lines += [
        "",
        "## Pass-2 status",
        "",
        f"The repository contains {pass2['input_file_count']} nonempty Pass-2 input structures expected to represent the historical 35-candidate shortlist, but {pass2['output_file_count']} output files are present and {pass2['output_nonempty_file_count']} contain data. Therefore a clean, completed historical 35-candidate Pass-2 shortlist is **not established**.",
        "",
        "## Reproducible files",
        "",
        "- `V1_AUDIT_SUMMARY.json` — complete machine-readable audit summary.",
        "- `v1_source_library_counts.csv`, `v1_box_counts.csv` — result and unique-candidate counts.",
        "- `V1_TOP10.csv`, `V1_TOP50.csv`, `V1_TOP100.csv`, `V1_TOP500.csv` — preserved current ranking prefixes.",
        "- `benchmark_config_audit.csv`, `receptor_and_config_inventory.csv`, `screening_source_inventory.csv`, `sdf_output_inventory.csv`, `pass2_audit.json` — detailed inventories.",
    ]
    (out / "V1_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out / "V1_AUDIT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
