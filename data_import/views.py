# data_import/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileUploadForm
from .import_handlers import handle_uploaded_file
import traceback

def import_data(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            import_type = form.cleaned_data["import_type"]
            uploaded_file = request.FILES["file"]
            try:
                records_imported = handle_uploaded_file(uploaded_file, import_type)
                messages.success(
                    request,
                    f"Successfully imported/updated {records_imported} records for {import_type}.",
                )
                return redirect("dashboard")
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(
                    request, f"An unexpected error occurred during import: {str(e)}"
                )
                # Print the full traceback for debugging
                print(traceback.format_exc())
    else:
        form = FileUploadForm()
    return render(request, "data_import/import.html", {"form": form})
