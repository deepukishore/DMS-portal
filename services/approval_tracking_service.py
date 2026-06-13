class ApprovalTrackingService:
    """Builds a step-by-step approval journey for a document record.

    The approval lifecycle has four checkpoints after upload:
      Pending -> Pending Final Approval -> Approved
    with Rejected as an early exit at either approval stage.
    """

    STATUS_META = {
        "Pending": {
            "label": "Awaiting first approval",
            "badge": "pending",
            "tone": "progress",
        },
        "Pending Final Approval": {
            "label": "Awaiting final approval",
            "badge": "review",
            "tone": "progress",
        },
        "Approved": {
            "label": "Approved & published",
            "badge": "approved",
            "tone": "done",
        },
        "Rejected": {
            "label": "Returned to uploader",
            "badge": "rejected",
            "tone": "rejected",
        },
    }

    @staticmethod
    def _meta(status):
        return ApprovalTrackingService.STATUS_META.get(
            status, ApprovalTrackingService.STATUS_META["Pending"]
        )

    @staticmethod
    def build_tracker(record):
        status = record.get("approval_status") or "Pending"
        uploaded_at = record.get("uploaded_at") or ""
        first_at = record.get("first_approved_at") or ""
        final_at = record.get("final_approved_at") or ""
        updated_at = record.get("approval_updated_at") or ""
        first_by = record.get("first_approver") or record.get("decision_by") or ""
        final_by = record.get("final_approver") or record.get("decision_by") or ""
        uploader = record.get("name") or "Uploader"

        is_rejected = status == "Rejected"
        rejected_after_first = is_rejected and bool(first_at)

        def first_state():
            if status in ("Approved", "Pending Final Approval"):
                return "complete"
            if status == "Pending":
                return "active"
            if is_rejected:
                return "complete" if rejected_after_first else "rejected"
            return "pending"

        def final_state():
            if status == "Approved":
                return "complete"
            if status == "Pending Final Approval":
                return "active"
            if is_rejected:
                return "rejected" if rejected_after_first else "pending"
            return "pending"

        def published_state():
            if status == "Approved":
                return "complete"
            return "pending"

        steps = [
            {
                "icon": "upload",
                "title": "Document Uploaded",
                "desc": "File submitted to the portal and queued for review.",
                "actor": uploader,
                "time": uploaded_at,
                "state": "complete",
            },
            {
                "icon": "bell",
                "title": "First Approver Notified",
                "desc": "An email alert was sent to the first-level approver.",
                "actor": "",
                "time": uploaded_at,
                "state": "complete",
            },
            {
                "icon": "user-check",
                "title": "First-Level Approval",
                "desc": "First approver reviews and forwards the request.",
                "actor": first_by,
                "time": first_at,
                "state": first_state(),
            },
            {
                "icon": "shield-check",
                "title": "Final Approval",
                "desc": "High-level approver makes the final decision.",
                "actor": final_by,
                "time": final_at,
                "state": final_state(),
            },
            {
                "icon": "archive",
                "title": "Published & Saved",
                "desc": "Document is approved and saved to the library.",
                "actor": "",
                "time": final_at or (updated_at if status == "Approved" else ""),
                "state": published_state(),
            },
        ]

        if is_rejected:
            reject_index = 3 if rejected_after_first else 2
            steps[reject_index] = {
                **steps[reject_index],
                "title": "Request Rejected",
                "desc": record.get("rejection_comment")
                or "The approver returned this document to the uploader.",
                "actor": record.get("decision_by") or "",
                "time": updated_at,
                "state": "rejected",
            }

        completed = sum(1 for step in steps if step["state"] == "complete")
        progress_pct = round(completed / len(steps) * 100)

        meta = ApprovalTrackingService._meta(status)

        return {
            "record": record,
            "status": status,
            "status_label": meta["label"],
            "badge": meta["badge"],
            "tone": meta["tone"],
            "progress_pct": progress_pct,
            "steps": steps,
        }

    @staticmethod
    def build_trackers(records):
        return [ApprovalTrackingService.build_tracker(record) for record in records]

    @staticmethod
    def summarize(trackers):
        summary = {"total": len(trackers), "in_progress": 0, "approved": 0, "rejected": 0}
        for tracker in trackers:
            if tracker["status"] == "Approved":
                summary["approved"] += 1
            elif tracker["status"] == "Rejected":
                summary["rejected"] += 1
            else:
                summary["in_progress"] += 1
        return summary
