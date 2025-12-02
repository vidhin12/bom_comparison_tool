from django.db import models

class UploadedFile(models.Model):
    """
    Stores metadata about each uploaded file.
    'file_type' is derived from the file extension to standardize processing.
    """
    FILE_TYPE_CHOICES = [
        ("xlsx", "Excel (.xlsx)"),
        ("csv", "CSV (.csv)"),
        ("pdf", "PDF (.pdf)"),
        ("txt", "Text (.txt)"),
        ("docx", "Word (.docx)"),
    ]

    file = models.FileField(upload_to="uploads/")
    original_name = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    is_master = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Store original filename for easy display
        if not self.original_name and self.file:
            self.original_name = self.file.name

        # Auto-detect file type from extension if not set
        if not self.file_type and self.file:
            ext = self.file.name.rsplit(".", 1)[-1].lower()
            if ext in dict(self.FILE_TYPE_CHOICES):
                self.file_type = ext

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_name or self.file.name} ({'Master' if self.is_master else 'Target'})"


class ComparisonResult(models.Model):
    """
    Stores the result of a comparison between one master BOM and one or more target BOMs.
    Enables /download_result/<id>/ endpoint to fetch saved JSON.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    master_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="comparison_master_runs",
    )
    target_files = models.ManyToManyField(
        UploadedFile,
        related_name="comparison_target_runs",
    )
    # JSON-serializable dict containing all comparison details
    result_json = models.JSONField()

    def __str__(self):
        return f"ComparisonResult #{self.pk} (master={self.master_file_id})"
