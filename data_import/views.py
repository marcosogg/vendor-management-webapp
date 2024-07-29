# data_import/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileUploadForm
from .import_handlers import handle_uploaded_file
import traceback
from core.models import Activity
from django.contrib.auth.decorators import login_required


@login_required
def import_data(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            import_type = form.cleaned_data["import_type"]
            uploaded_file = request.FILES["file"]
            try:
                records_imported = handle_uploaded_file(uploaded_file, import_type)

                # Create an Activity record for the import
                Activity.objects.create(
                    user=request.user,
                    action=f"Import {import_type}",
                    details=f"Successfully imported/updated {records_imported} records for {import_type}.",
                )

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
                print(traceback.format_exc())
    else:
        form = FileUploadForm()
    return render(request, "data_import/import.html", {"form": form})
