from django import forms


class FileUploadForm(forms.Form):
    file = forms.FileField(label="Select a CSV or Excel file")

    def clean_file(self):
        file = self.cleaned_data["file"]
        ext = file.name.split(".")[-1].lower()
        if ext not in ["csv", "xlsx", "xls"]:
            raise forms.ValidationError("Only CSV and Excel files are allowed.")
        return file
