# BOM Comparison Tool

This Django project provides a web-based interface to compare a master Bill of Materials (BOM) with several target BOM files. It supports various file formats (xlsx, csv, txt, docx, pdf), parses them, and highlights the differences.

## 1. Project Setup

### 1.1. Create a Virtual Environment

First, create a virtual environment for the project. Make sure you have Python 3.12 or higher installed.

```bash
python -m venv venv
```

### 1.2. Activate the Virtual Environment

**On Windows:**

```bash
venv\\Scripts\\activate
```

**On macOS/Linux:**

```bash
source venv/bin/activate
```

### 1.3. Install Dependencies

Install all the required packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

## 2. Django Project Initialization

### 2.1. Create the Project and App

The following commands will set up the Django project and the `comparison` app.

```bash
django-admin startproject bom_comparison_tool .
python manage.py startapp comparison
```

*Note: The command `django-admin startproject bom_comparison_tool .` creates the project in the current directory. If you prefer a subdirectory, omit the dot at the end.*

### 2.2. Configure Settings

Modify `bom_comparison_tool/settings.py` to include the `comparison` app, and configure media file handling.

```python
# bom_comparison_tool/settings.py

# ...

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'comparison',  # Add the app
]

# ...

# Media files
MEDIA_URL = 
/media/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Optional: Add file upload size limits (e.g., 10MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
```

### 2.3. Set Up URLs

Configure the project's main `urls.py` to include the app's URLs.

```python
# bom_comparison_tool/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comparison.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 3. Database Migrations

After defining the models in `comparison/models.py`, create and apply the database migrations.

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Running the Development Server

Once the setup is complete, you can run the Django development server.

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## 5. Future Development

Here are some potential areas for future improvement:

*   **Asynchronous Processing:** For large files, the parsing and comparison process can be time-consuming. Offload these tasks to a background worker using Celery and Redis to avoid blocking the web server.
*   **User Authentication:** Add user accounts to allow users to save their comparison history and manage their uploaded files.
*   **Advanced Error Handling:** Implement more robust error handling for file parsing, especially for malformed or unexpected file structures. Provide clearer feedback to the user about what went wrong.
*   **More Flexible Column Mapping:** Allow users to map the columns from their uploaded files to the expected columns (`MPN`, `Quantity`, `Ref_Des`, `Description`) instead of relying on hardcoded column names.
*   **Testing:** Write a comprehensive suite of unit and integration tests to ensure the reliability of the parsing and comparison logic.
*   **Deployment:** Containerize the application using Docker for easier deployment to production environments.
