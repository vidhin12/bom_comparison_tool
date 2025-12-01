from django.shortcuts import render

# Create your views here.
import json
from typing import Dict

from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import UploadedFile, ComparisonResult
from .utils.parsers import parse_file_to_df
from .utils.comparison import compare_master_with_multiple_targets
from django.core.paginator import Paginator
import pandas as pd


ALLOWED_MASTER_EXT = {"xlsx"}
ALLOWED_TARGET_EXT = {"xlsx", "csv", "txt", "docx", "pdf"}


def _get_file_extension(file_obj) -> str:
    """
    Extract file extension from uploaded file name.
    """
    name = file_obj.name
    if "." not in name:
        return ""
    return name.rsplit(".", 1)[-1].lower()


def upload_bom_view(request):
    """
    Main page:
    - Upload one master BOM (.xlsx)
    - Upload 1–5 target files (xlsx/csv/txt/docx/pdf)
    - Perform comparison and store the result in ComparisonResult
    """
    if request.method == "POST":
        master_file = request.FILES.get("master_file")
        target_files = request.FILES.getlist("target_files")

        # Basic validations
        if not master_file:
            messages.error(request, "Please upload a master BOM file.")
            return redirect("comparison:upload")

        if not (1 <= len(target_files) <= 5):
            messages.error(request, "Please upload between 1 and 5 target files.")
            return redirect("comparison:upload")

        master_ext = _get_file_extension(master_file)
        if master_ext not in ALLOWED_MASTER_EXT:
            messages.error(request, "Master BOM must be an .xlsx file.")
            return redirect("comparison:upload")

        # Check each target file
        for f in target_files:
            ext = _get_file_extension(f)
            if ext not in ALLOWED_TARGET_EXT:
                messages.error(request, f"Target file '{f.name}' has unsupported type .{ext}.")
                return redirect("comparison:upload")

        # File size validation (simple per-file check)
        max_size = getattr(settings, "MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
        if master_file.size > max_size:
            messages.error(request, f"Master file exceeds max size of {max_size // (1024 * 1024)} MB.")
            return redirect("comparison:upload")
        for f in target_files:
            if f.size > max_size:
                messages.error(request, f"Target file '{f.name}' exceeds max size of {max_size // (1024 * 1024)} MB.")
                return redirect("comparison:upload")

        # Save master UploadedFile
        master_uploaded = UploadedFile.objects.create(
            file=master_file,
            file_type=master_ext,
            is_master=True,
        )

        # Parse master to DataFrame
        master_df = parse_file_to_df(master_uploaded.file, master_uploaded.file_type)

        # Save and parse targets
        target_dfs: Dict[int, object] = {}
        target_uploaded_objs = []

        for f in target_files:
            ext = _get_file_extension(f)
            target_uploaded = UploadedFile.objects.create(
                file=f,
                file_type=ext,
                is_master=False,
            )
            target_uploaded_objs.append(target_uploaded)

            df = parse_file_to_df(target_uploaded.file, target_uploaded.file_type)
            target_dfs[target_uploaded.pk] = df

        # Perform comparisons
        combined_result_json = compare_master_with_multiple_targets(master_df, target_dfs)

        # Store comparison result in DB
        comparison_result = ComparisonResult.objects.create(
            master_file=master_uploaded,
            result_json=combined_result_json,
        )
        comparison_result.target_files.set(target_uploaded_objs)

        messages.success(request, "Comparison completed successfully.")
        return redirect("comparison:result", pk=comparison_result.pk)

    # GET request: show upload form
    return render(request, "comparison/upload.html")


def comparison_result_view(request, pk: int):
    """
    Display comparison results:
    - Side-by-side tables
    - Color highlighting for differences
    """
    comparison_result = get_object_or_404(ComparisonResult, pk=pk)
    data = comparison_result.result_json or {}

    # For convenience in template, attach UploadedFile objects to each target entry
    target_id_to_obj = {t.id: t for t in comparison_result.target_files.all()}
    for target in data.get("targets", []):
        file_id = target.get("target_file_id")
        target["file_obj"] = target_id_to_obj.get(file_id)

    context = {
        "comparison_result": comparison_result,
        "data": data,
    }
    return render(request, "comparison/result.html", context)


def download_result_view(request, pk: int):
    """
    Download the JSON comparison result as a .json file.
    URL: /download_result/<id>/
    """
    comparison_result = get_object_or_404(ComparisonResult, pk=pk)
    result_dict = comparison_result.result_json or {}

    # Serialize to JSON string
    json_str = json.dumps(result_dict, indent=2)

    response = HttpResponse(json_str, content_type="application/json")
    filename = f"bom_comparison_result_{comparison_result.pk}.json"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response



def comparison_history_view(request):
    """
    List past comparison runs with pagination.
    """
    qs = ComparisonResult.objects.select_related("master_file").order_by("-created_at")
    paginator = Paginator(qs, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "comparison/history.html", {"page_obj": page_obj})


def download_result_excel_view(request, pk: int):
    """
    Export comparison result as an Excel file.
    Flattens JSON 'details' per target into one sheet per target.
    """
    comparison_result = get_object_or_404(ComparisonResult, pk=pk)
    data = comparison_result.result_json or {}

    # Create a Pandas Excel writer in-memory
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for target in data.get("targets", []):
            target_id = target.get("target_file_id")
            comp = target.get("comparison", {})
            rows = comp.get("details", [])

            # Normalize rows: flatten master/target dicts
            flat_rows = []
            for r in rows:
                row = {
                    "MPN": r.get("mpn"),
                    "status": r.get("flags", {}).get("status"),
                    "quantity_mismatch": r.get("flags", {}).get("quantity_mismatch"),
                    "description_mismatch": r.get("flags", {}).get("description_mismatch"),
                    "refdes_mismatch": r.get("flags", {}).get("refdes_mismatch"),
                }
                master = r.get("master") or {}
                target_part = r.get("target") or {}

                row.update({
                    "master_qty": master.get("Quantity"),
                    "master_ref_des": master.get("Ref_Des"),
                    "master_desc": master.get("Description"),
                    "target_qty": target_part.get("Quantity"),
                    "target_ref_des": target_part.get("Ref_Des"),
                    "target_desc": target_part.get("Description"),
                })

                flat_rows.append(row)

            df = pd.DataFrame(flat_rows)
            sheet_name = f"target_{target_id}" if target_id is not None else "target"
            df.to_excel(writer, index=False, sheet_name=sheet_name[:31])  # Excel sheet name limit

    output.seek(0)
    filename = f"bom_comparison_{comparison_result.pk}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response