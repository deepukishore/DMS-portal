from copy import deepcopy

from data.document_library_data import CATEGORY_ALIASES, LIBRARY_CATEGORIES, LIBRARY_DATA


class DocumentLibraryService:
    @staticmethod
    def get_categories():
        return deepcopy(LIBRARY_CATEGORIES)

    @staticmethod
    def resolve_category(category_key):
        if not category_key:
            return "procedures", "", ""

        alias = CATEGORY_ALIASES.get(category_key)
        if alias:
            return (
                alias["key"],
                alias.get("primary", ""),
                alias.get("secondary", ""),
            )

        if category_key in LIBRARY_DATA:
            return category_key, "", ""

        return "procedures", "", ""

    @staticmethod
    def get_category_data(category_key, access_department=""):
        data = deepcopy(LIBRARY_DATA.get(category_key, {}))
        if not access_department or not data:
            return data
        # Filter uploaded files within the category data to only those matching the department
        from services.category_document_service import CategoryDocumentService
        def _filter_files(files):
            if not files:
                return files
            allowed = set(CategoryDocumentService.get_files_for_category(
                category_key, department=access_department
            ))
            # Keep static/mock files always; only restrict DB-uploaded files if any exist
            db_files = set(CategoryDocumentService.get_files_for_category(category_key))
            if not db_files:
                return files  # no DB files at all — static data, no restriction needed
            return [f for f in files if f not in db_files or f in allowed]
        if "files" in data:
            data["files"] = _filter_files(data["files"])
        return data
