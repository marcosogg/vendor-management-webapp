from django import forms


class FileUploadForm(forms.Form):
    IMPORT_TYPES = [
        ("vendors", "Vendors Report"),
        ("parts", "Parts Report"),
        ("spend", "Spend Report"),
    ]

    file = forms.FileField(label="Select a CSV or Excel file")
    import_type = forms.ChoiceField(choices=IMPORT_TYPES, label="Select Import Type")

    def clean_file(self):
        file = self.cleaned_data["file"]
        ext = file.name.split(".")[-1].lower()
        if ext not in ["csv", "xlsx", "xls"]:
            raise forms.ValidationError("Only CSV and Excel files are allowed.")
        return file
