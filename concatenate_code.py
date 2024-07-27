import os
import pathlib
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def read_file_content(file_path):
    encodings = ["utf-8", "latin-1", "ascii"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as infile:
                return infile.read()
        except UnicodeDecodeError:
            continue
    logging.warning(
        f"Could not read file {file_path} with any of the attempted encodings."
    )
    return None


def generate_tree(project_root, relevant_dirs):
    tree = ["Directory structure of included files:"]
    tree.append(f"└── {os.path.basename(project_root)}")
    tree.append("    └── manage.py")

    for dir_name in relevant_dirs:
        dir_path = os.path.join(project_root, dir_name)
        if os.path.exists(dir_path):
            tree.append(f"    └── {dir_name}")
            for root, dirs, files in os.walk(dir_path):
                level = root.replace(project_root, "").count(os.sep)
                indent = "    " * (level + 1) + "└── "
                subindent = "    " * (level + 2) + "└── "
                tree.append(f"{indent}{os.path.basename(root)}/")
                for file in files:
                    if pathlib.Path(file).suffix.lower() in [
                        ".py",
                        ".html",
                        ".css",
                        ".js",
                        ".md",
                        ".txt",
                    ]:
                        tree.append(f"{subindent}{file}")

    return "\n".join(tree)


def concatenate_files(project_root, output_file):
    relevant_dirs = ["core", "data_import", "templates", "vendor_management"]

    with open(output_file, "w", encoding="utf-8") as outfile:
        # First, write the directory tree
        tree = generate_tree(project_root, relevant_dirs)
        outfile.write(f"{tree}\n\n")

        # Then, add manage.py from the root
        manage_py_path = os.path.join(project_root, "manage.py")
        if os.path.exists(manage_py_path):
            content = read_file_content(manage_py_path)
            if content is not None:
                outfile.write(f"\n\n{'='*80}\n")
                outfile.write(f"File: manage.py\n")
                outfile.write(f"{'='*80}\n")
                outfile.write('"""\n')
                outfile.write(content)
                outfile.write('\n"""')

        # Finally, process the relevant directories
        for dir_name in relevant_dirs:
            dir_path = os.path.join(project_root, dir_name)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, project_root)
                        file_extension = pathlib.Path(file).suffix.lower()

                        if file_extension in [
                            ".py",
                            ".html",
                            ".css",
                            ".js",
                            ".md",
                            ".txt",
                        ]:
                            content = read_file_content(file_path)
                            if content is not None:
                                outfile.write(f"\n\n{'='*80}\n")
                                outfile.write(f"File: {relative_path}\n")
                                outfile.write(f"{'='*80}\n")
                                outfile.write('"""\n')
                                outfile.write(content)
                                outfile.write('\n"""')
                            else:
                                logging.warning(
                                    f"Skipping file {relative_path} due to encoding issues."
                                )


if __name__ == "__main__":
    project_root = "C:\\Users\\marcos.gomes\\dev\\Python\\vendor-management-webapp"
    output_file = "concatenated_code.txt"
    try:
        concatenate_files(project_root, output_file)
        logging.info(f"Relevant code files have been concatenated into {output_file}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
