from typing import Dict, Any, List
import pandas as pd


def _force_flat(df):
    """Fix multi-column or list-like MPN problems."""
    df = df.copy()

    # If duplicate columns exist → keep first
    df = df.loc[:, ~df.columns.duplicated()]

    # If a column contains lists, flatten them
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x[0] if isinstance(x, list) else x)

    # Ensure MPN exists and is string
    if "MPN" not in df.columns:
        df["MPN"] = ""

    df["MPN"] = df["MPN"].astype(str).str.strip()

    return df


def _aggregate_bom(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate BOM by MPN:
    - Sum Quantity
    - Concatenate Ref_Des
    - Keep first Description
    """
    df = _force_flat(df)   # <<< ADD THIS LINE
    
    if df is None or df.empty:
        return pd.DataFrame(columns=["MPN", "Quantity", "Ref_Des", "Description"])

    df = df.copy()
    df["Ref_Des"] = df["Ref_Des"].fillna("")
    df["Description"] = df["Description"].fillna("")

    agg = (
        df.groupby("MPN", as_index=False)
        .agg(
            Quantity=("Quantity", "sum"),
            Ref_Des=("Ref_Des", lambda x: ", ".join(sorted(set(str(i) for i in x if i)))),
            Description=("Description", "first"),
        )
    )
    return agg


def compare_boms(master_df: pd.DataFrame, target_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare a master BOM against a single target BOM.

    Detects:
    - Quantity mismatch
    - Missing parts (in master, not in target)
    - Extra parts   (in target, not in master)
    - Modified description
    - Changed reference designators

    Returns:
        JSON-serializable dict with per-MPN detail + summary counts.
    """
    master = _aggregate_bom(master_df)
    target = _aggregate_bom(target_df)

    master_mpn_set = set(master["MPN"])
    target_mpn_set = set(target["MPN"])

    missing_mpns = master_mpn_set - target_mpn_set  # in master, not target
    extra_mpns = target_mpn_set - master_mpn_set    # in target, not master
    common_mpns = master_mpn_set & target_mpn_set

    rows: List[Dict[str, Any]] = []

    quantity_mismatches = 0
    description_mismatches = 0
    refdes_mismatches = 0

    # Handle common MPNs
    master_indexed = master.set_index("MPN")
    target_indexed = target.set_index("MPN")

    for mpn in common_mpns:
        m_row = master_indexed.loc[mpn]
        t_row = target_indexed.loc[mpn]

        qty_mismatch = int(m_row["Quantity"]) != int(t_row["Quantity"])
        desc_mismatch = (m_row["Description"] or "").strip() != (t_row["Description"] or "").strip()
        refdes_mismatch = (m_row["Ref_Des"] or "").strip() != (t_row["Ref_Des"] or "").strip()

        if qty_mismatch:
            quantity_mismatches += 1
        if desc_mismatch:
            description_mismatches += 1
        if refdes_mismatch:
            refdes_mismatches += 1

        rows.append(
            {
                "mpn": mpn,
                "master": {
                    "Quantity": int(m_row["Quantity"]),
                    "Ref_Des": m_row["Ref_Des"],
                    "Description": m_row["Description"],
                },
                "target": {
                    "Quantity": int(t_row["Quantity"]),
                    "Ref_Des": t_row["Ref_Des"],
                    "Description": t_row["Description"],
                },
                "flags": {
                    "quantity_mismatch": qty_mismatch,
                    "description_mismatch": desc_mismatch,
                    "refdes_mismatch": refdes_mismatch,
                    "status": "mismatch" if qty_mismatch or desc_mismatch or refdes_mismatch else "match",
                },
            }
        )

    # Missing parts (present only in master)
    missing_parts: List[Dict[str, Any]] = []
    for mpn in missing_mpns:
        m_row = master_indexed.loc[mpn]
        missing_parts.append(
            {
                "mpn": mpn,
                "master": {
                    "Quantity": int(m_row["Quantity"]),
                    "Ref_Des": m_row["Ref_Des"],
                    "Description": m_row["Description"],
                },
                "target": None,
                "flags": {
                    "missing_in_target": True,
                    "status": "missing",
                },
            }
        )

    # Extra parts (present only in target)
    extra_parts: List[Dict[str, Any]] = []
    for mpn in extra_mpns:
        t_row = target_indexed.loc[mpn]
        extra_parts.append(
            {
                "mpn": mpn,
                "master": None,
                "target": {
                    "Quantity": int(t_row["Quantity"]),
                    "Ref_Des": t_row["Ref_Des"],
                    "Description": t_row["Description"],
                },
                "flags": {
                    "extra_in_target": True,
                    "status": "extra",
                },
            }
        )

    all_rows = rows + missing_parts + extra_parts

    result: Dict[str, Any] = {
        "summary": {
            "total_master_parts": len(master_mpn_set),
            "total_target_parts": len(target_mpn_set),
            "missing_parts_count": len(missing_parts),
            "extra_parts_count": len(extra_parts),
            "quantity_mismatch_count": quantity_mismatches,
            "description_mismatch_count": description_mismatches,
            "refdes_mismatch_count": refdes_mismatches,
        },
        "details": all_rows,
    }
    return result


def compare_master_with_multiple_targets(master_df: pd.DataFrame, targets: Dict[int, pd.DataFrame]) -> Dict[str, Any]:
    """
    Compare one master BOM against multiple target BOM DataFrames.

    Args:
        master_df: DataFrame of master BOM
        targets: dict {uploaded_file_id: df}

    Returns:
        JSON-serializable dict keyed by target_file_id.
    """
    result: Dict[str, Any] = {
        "targets": []
    }
    for file_id, df in targets.items():
        single_result = compare_boms(master_df, df)
        result["targets"].append(
            {
                "target_file_id": file_id,
                "comparison": single_result,
            }
        )
    return result
