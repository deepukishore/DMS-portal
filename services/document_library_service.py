import re
from copy import deepcopy

from data.customers import sort_customers
from data.document_library_data import CATEGORY_ALIASES, LIBRARY_CATEGORIES, LIBRARY_DATA
from services.category_document_service import CategoryDocumentService


class DocumentLibraryService:
    _DOCUMENT_FILE_PATTERN = re.compile(
        r"\.(pdf|docx?|xlsx?|pptx?)$",
        re.IGNORECASE,
    )

    @staticmethod
    def _collect_document_files(node, files=None):
        """Collect unique file names without counting labels or descriptions."""
        files = files if files is not None else set()
        if isinstance(node, dict):
            for value in node.values():
                DocumentLibraryService._collect_document_files(value, files)
        elif isinstance(node, (list, tuple, set)):
            for value in node:
                DocumentLibraryService._collect_document_files(value, files)
        elif isinstance(node, str) and DocumentLibraryService._DOCUMENT_FILE_PATTERN.search(node.strip()):
            files.add(node.strip())
        return files

    @staticmethod
    def _append_unique(files, file_name):
        if file_name and file_name not in files:
            files.append(file_name)

    @staticmethod
    def _plant_folder_key(plants, plant):
        if plant in plants:
            return plant
        if plant in {"P2 - Guduvachery Plant", "P3 - Guduvachery Plant"}:
            combined = "P2&3 - Guduvachery Plants"
            if combined in plants:
                return combined
        return plant

    @staticmethod
    def _core_tool_folder_for_file(file_name):
        normalized = (file_name or "").lower().replace("-", "_").replace(" ", "_")
        folder_markers = (
            ("ppap", "ppap"),
            ("msa", "msa"),
            ("fmea", "fmea"),
            ("apqp", "apqp"),
            ("spc", "spc"),
            ("control_plan", "cp"),
            ("iatf", "iatf_manual"),
        )
        for marker, folder_key in folder_markers:
            if marker in normalized:
                return folder_key
        return "iatf_manual"

    @staticmethod
    def _order_customer_mappings(node):
        if not isinstance(node, dict):
            return node
        customers = node.get("customers")
        if isinstance(customers, dict):
            node["customers"] = {
                customer: customers[customer]
                for customer in sort_customers(customers.keys())
            }
        for value in node.values():
            if isinstance(value, dict):
                DocumentLibraryService._order_customer_mappings(value)
        return node

    @staticmethod
    def _merge_uploaded_files(category_key, data, access_department=""):
        uploaded = CategoryDocumentService.get_file_records_for_category(
            category_key,
            department=access_department,
            approved_only=True,
        )
        if category_key == "qms":
            # IATF Audit used to be a separate category. Merge those approved
            # records into the new QMS/IATF Audit folders so nothing is lost.
            legacy_audit_records = CategoryDocumentService.get_file_records_for_category(
                "audit_nc",
                department=access_department,
                approved_only=True,
            )
        else:
            legacy_audit_records = []
        if not uploaded:
            if not legacy_audit_records:
                return data

        if category_key == "qms":
            groups = data.get("document_groups", {})
            for record in uploaded:
                sub_category = record.get("sub_category") or ""
                path_parts = [part for part in sub_category.split(":") if part]
                if path_parts and path_parts[0] in {"L1", "L2", "L3", "L4"}:
                    path_parts = path_parts[1:]
                group_key = path_parts[0] if path_parts else ""
                subfolder_key = path_parts[1] if len(path_parts) > 1 else ""
                # Plans used to be a top-level QMS folder. Keep previously
                # uploaded files visible after moving it under IATF Audit.
                if group_key == "plans":
                    group_key = "iatf_audit"
                    subfolder_key = "plans"
                group = groups.get(group_key)
                if not group:
                    continue
                if "secondary_options" in group:
                    subfolders = group.get("secondary_options", {})
                    subfolder = subfolders.get(subfolder_key)
                    if subfolder is None and group_key == "business_procedures":
                        subfolder = subfolders.get("bp_cp")
                    if subfolder is not None:
                        if "plants" in subfolder:
                            plant = path_parts[2] if len(path_parts) > 2 else record.get("plant") or ""
                            plant = DocumentLibraryService._plant_folder_key(
                                subfolder.setdefault("plants", {}),
                                plant,
                            )
                            if plant:
                                DocumentLibraryService._append_unique(
                                    subfolder.setdefault("plants", {}).setdefault(plant, []),
                                    record.get("file_name"),
                                )
                        else:
                            DocumentLibraryService._append_unique(
                                subfolder.setdefault("files", []),
                                record.get("file_name"),
                            )
                else:
                    DocumentLibraryService._append_unique(
                        group.setdefault("files", []),
                        record.get("file_name"),
                    )

            audit_group = groups.get("iatf_audit", {})
            audit_folders = audit_group.get("secondary_options", {})
            for record in legacy_audit_records:
                parts = [part for part in (record.get("sub_category") or "").split(":") if part]
                primary = parts[0] if parts else ""
                secondary = parts[1] if len(parts) > 1 else "ncs"
                primary = {
                    "iatf_internal_audits": "internal_audit",
                    "iatf_external_audits": "external_audit",
                }.get(primary, primary)
                folder_key = {
                    ("internal_audit", "ncs"): "internal_audit_ncs",
                    ("internal_audit", "reports"): "internal_audit_reports",
                    ("external_audit", "ncs"): "external_audit_ncs",
                    ("external_audit", "reports"): "external_audit_reports",
                }.get((primary, secondary))
                folder = audit_folders.get(folder_key) if folder_key else None
                if not folder:
                    continue
                plant = parts[2] if len(parts) > 2 else record.get("plant") or ""
                plant = DocumentLibraryService._plant_folder_key(
                    folder.setdefault("plants", {}),
                    plant,
                )
                if plant:
                    DocumentLibraryService._append_unique(
                        folder.setdefault("plants", {}).setdefault(plant, []),
                        record.get("file_name"),
                    )
            return data

        if "primary_options" in data:
            options = data.get("primary_options", {})
            for record in uploaded:
                sub_category = record.get("sub_category") or ""
                parts = sub_category.split(":")
                primary = parts[0] if parts else ""
                secondary = parts[1] if len(parts) > 1 else ""
                tertiary = ":".join(parts[2:]) if len(parts) > 2 else ""
                if category_key == "audit_nc":
                    legacy_primary = {
                        "iatf_internal_audits": "internal_audit",
                        "iatf_external_audits": "external_audit",
                    }
                    if primary in legacy_primary:
                        primary = legacy_primary[primary]
                        secondary = secondary or "ncs"
                if category_key == "core_tools_manuals" and primary not in options:
                    primary = DocumentLibraryService._core_tool_folder_for_file(
                        record.get("file_name")
                    )
                folder = options.get(primary)
                if not folder:
                    continue
                if "customers" in folder:
                    customer = secondary
                    if customer:
                        DocumentLibraryService._append_unique(
                            folder.setdefault("customers", {}).setdefault(customer, []),
                            record.get("file_name"),
                        )
                elif "secondary_options" in folder:
                    secondary_folder = folder.get("secondary_options", {}).get(secondary)
                    if secondary_folder is not None:
                        if "plants" in secondary_folder:
                            plants = secondary_folder.setdefault("plants", {})
                            plant = tertiary or record.get("plant") or ""
                            plant = DocumentLibraryService._plant_folder_key(plants, plant)
                            if plant:
                                DocumentLibraryService._append_unique(
                                    plants.setdefault(plant, []),
                                    record.get("file_name"),
                                )
                        else:
                            DocumentLibraryService._append_unique(
                                secondary_folder.setdefault("files", []),
                                record.get("file_name"),
                            )
                else:
                    DocumentLibraryService._append_unique(
                        folder.setdefault("files", []),
                        record.get("file_name"),
                    )
            return data

        if "customers" in data:
            customers = data.setdefault("customers", {})
            for record in uploaded:
                customer = record.get("sub_category") or ""
                if customer:
                    DocumentLibraryService._append_unique(
                        customers.setdefault(customer, []),
                        record.get("file_name"),
                    )
            return data

        if "files" in data:
            files = data.setdefault("files", [])
            for record in uploaded:
                DocumentLibraryService._append_unique(files, record.get("file_name"))
        return data

    @staticmethod
    def get_categories():
        return deepcopy(LIBRARY_CATEGORIES)

    @staticmethod
    def get_dashboard_statistics(qms_level="", access_department=""):
        """Return access-aware file counts for each document-library category."""
        statistics = []
        for category in DocumentLibraryService.get_categories():
            category_key = category["key"]
            if category_key == "plant_wise_records":
                from services.plant_asset_service import PlantAssetService

                file_count = PlantAssetService.get_available_file_count(
                    access_department=access_department,
                )
            else:
                data = DocumentLibraryService.get_client_category_data(
                    category_key,
                    qms_level=qms_level,
                    access_department=access_department,
                )

                if category_key == "qms":
                    allowed_groups = set(data.get("scope", {}).get("groups", []))
                    data["document_groups"] = {
                        key: value
                        for key, value in data.get("document_groups", {}).items()
                        if key in allowed_groups
                    }

                file_count = len(DocumentLibraryService._collect_document_files(data))
            statistics.append(
                {
                    "key": category_key,
                    "label": category["label"],
                    "icon": category["icon"],
                    "icon_image": category.get("icon_image", ""),
                    "count": file_count,
                }
            )
        return statistics

    @staticmethod
    def resolve_category(category_key):
        if not category_key:
            return "qms", "", ""

        alias = CATEGORY_ALIASES.get(category_key)
        if alias:
            return (
                alias["key"],
                alias.get("primary", ""),
                alias.get("secondary", ""),
            )

        if category_key in LIBRARY_DATA:
            return category_key, "", ""

        return "qms", "", ""

    @staticmethod
    def get_category_data(category_key, access_department=""):
        data = deepcopy(LIBRARY_DATA.get(category_key, {}))
        data = DocumentLibraryService._merge_uploaded_files(category_key, data, access_department=access_department)
        data = DocumentLibraryService._order_customer_mappings(data)
        if not access_department or not data:
            return data
        # Filter uploaded files within the category data to only those matching the department
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

    @staticmethod
    def get_client_category_data(category_key, qms_level="", access_department=""):
        data = DocumentLibraryService.get_category_data(
            category_key,
            access_department=access_department,
        )

        if category_key == "qms":
            levels = data.pop("levels", {})
            scope = levels.get(qms_level, levels.get("L4", {}))
            data["scope"] = {
                "groups": list(scope.get("groups", [])),
                "subgroups": deepcopy(scope.get("subgroups", {})),
                "can_edit": bool(scope.get("can_edit")),
                "can_delete": bool(scope.get("can_delete")),
            }
            for group_key, allowed_subgroups in scope.get("subgroups", {}).items():
                group = data.get("document_groups", {}).get(group_key, {})
                subfolders = group.get("secondary_options")
                if subfolders is not None:
                    allowed = set(allowed_subgroups)
                    group["secondary_options"] = {
                        key: value
                        for key, value in subfolders.items()
                        if key in allowed
                    }
            data["description"] = "Browse quality management documents by category."

        if category_key == "plant_wise_records":
            data["description"] = "Approved records organized by plant and department."

        return data
