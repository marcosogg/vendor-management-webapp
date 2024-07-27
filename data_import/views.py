from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileUploadForm
from .import_handlers import handle_uploaded_file

def import_data(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            try:
                records_imported, errors = handle_uploaded_file(uploaded_file)
                if errors:
                    for error in errors:
                        messages.warning(request, error)
                messages.success(request, f'Successfully imported {records_imported} records.')
                return redirect('vendor_list')
            except Exception as e:
                messages.error(request, f'Error importing file: {str(e)}')
    else:
        form = FileUploadForm()
    return render(request, 'data_import/import.html', {'form': form})