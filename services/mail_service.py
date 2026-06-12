from flask_mail import Message

from extensions import mail


class MailService:
    """Handles outbound email delivery."""

    @staticmethod
    def send_password_reset(to_email, reset_url):
        try:
            msg = Message(
                subject="Smart DMS Password Reset",
                recipients=[to_email],
                body=(
                    "Click the link below to reset your password:\n\n"
                    f"{reset_url}\n\n"
                    "This link expires in 1 hour."
                ),
            )
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def send_upload_confirmation(to_email, file_name, uploader_name):
        """Send confirmation email when a file is uploaded for approval."""
        try:
            msg = Message(
                subject=f"File uploaded for approval: {file_name}",
                recipients=[to_email],
            )
            msg.body = (
                f"Your file has been successfully uploaded and is now pending approval.\n\n"
                f"File: {file_name}\n"
                f"Uploaded by: {uploader_name}\n\n"
                "You will receive another notification once the file has been reviewed."
            )
            msg.html = f"""
                <p>Your file has been successfully uploaded and is now pending approval.</p>
                <table cellpadding="6" cellspacing="0" border="0">
                  <tr><td><strong>File</strong></td><td>{file_name}</td></tr>
                  <tr><td><strong>Uploaded by</strong></td><td>{uploader_name}</td></tr>
                  <tr><td><strong>Status</strong></td><td>Pending Review</td></tr>
                </table>
                <p style="margin-top:16px;color:#6e7681;">You will receive another notification once the file has been reviewed.</p>
            """
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def send_document_approval_request(to_email, review_url, record):
        try:
            msg = Message(
                subject=f"Approval request: {record['file_name']}",
                recipients=[to_email],
            )
            msg.body = (
                "A new document is waiting for approval.\n\n"
                f"File: {record['file_name']}\n"
                f"Uploaded by: {record['name']} ({record['user_id']})\n"
                f"Plant: {record['plant']}\n"
                f"Department: {record['department']}\n"
                f"Customer: {record['customer']}\n"
                f"Document number: {record.get('document_number', 'N/A')}\n"
                f"Revision number: {record.get('revision_number', 'N/A')}\n"
                f"Category: {record.get('category', 'N/A')}\n"
                f"Current status: {record['approval_status']}\n\n"
                "Open the review page below to preview the file and mark it approved or rejected:\n"
                f"{review_url}"
            )
            msg.html = f"""
                <p>A new document is waiting for approval.</p>
                <table cellpadding="6" cellspacing="0" border="0">
                  <tr><td><strong>File</strong></td><td>{record['file_name']}</td></tr>
                  <tr><td><strong>Uploaded by</strong></td><td>{record['name']} ({record['user_id']})</td></tr>
                  <tr><td><strong>Plant</strong></td><td>{record['plant']}</td></tr>
                  <tr><td><strong>Department</strong></td><td>{record['department']}</td></tr>
                  <tr><td><strong>Customer</strong></td><td>{record['customer']}</td></tr>
                  <tr><td><strong>Document number</strong></td><td>{record.get('document_number', 'N/A')}</td></tr>
                  <tr><td><strong>Revision number</strong></td><td>{record.get('revision_number', 'N/A')}</td></tr>
                  <tr><td><strong>Category</strong></td><td>{record.get('category', 'N/A')}</td></tr>
                  <tr><td><strong>Status</strong></td><td>{record['approval_status']}</td></tr>
                </table>
                <p style="margin-top:16px;">
                  <a href="{review_url}" style="background:#f0a500;color:#0d1117;padding:10px 16px;border-radius:6px;text-decoration:none;font-weight:600;">
                    Review document
                  </a>
                </p>
            """
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def send_approval_decision_notification(to_email, record, status, decision_made_at=None, rejection_comment=""):
        """Send notification to uploader about approval decision."""
        try:
            status_color = "#3fb950" if status == "Approved" else "#f85149"
            status_bg = "rgba(63,185,80,.15)" if status == "Approved" else "rgba(248,81,73,.15)"
            rejection_comment = (rejection_comment or "").strip()
            comment_block = ""
            if status == "Rejected" and rejection_comment:
                comment_block = f"Rejection comments: {rejection_comment}\n"
            
            msg = Message(
                subject=f"Document {status}: {record['file_name']}",
                recipients=[to_email],
            )
            msg.body = (
                f"Your document has been {status.lower()}.\n\n"
                f"File: {record['file_name']}\n"
                f"Uploaded by: {record['name']} ({record['user_id']})\n"
                f"Plant: {record['plant']}\n"
                f"Department: {record['department']}\n"
                f"Customer: {record['customer']}\n"
                f"Document number: {record.get('document_number', 'N/A')}\n"
                f"Revision number: {record.get('revision_number', 'N/A')}\n"
                f"Category: {record.get('category', 'N/A')}\n"
                f"Status: {status}\n"
                f"Updated at: {decision_made_at or record.get('approval_updated_at', 'N/A')}\n\n"
                f"{comment_block}\n"
                f"You can view your document in the Smart DMS dashboard."
            )
            rejection_html = ""
            if status == "Rejected" and rejection_comment:
                rejection_html = f"""
                  <tr><td><strong>Rejection comments</strong></td><td>{rejection_comment}</td></tr>
                """
            msg.html = f"""
                <p>Your document has been <strong>{status.lower()}</strong>.</p>
                <table cellpadding="6" cellspacing="0" border="0">
                  <tr><td><strong>File</strong></td><td>{record['file_name']}</td></tr>
                  <tr><td><strong>Uploaded by</strong></td><td>{record['name']} ({record['user_id']})</td></tr>
                  <tr><td><strong>Plant</strong></td><td>{record['plant']}</td></tr>
                  <tr><td><strong>Department</strong></td><td>{record['department']}</td></tr>
                  <tr><td><strong>Customer</strong></td><td>{record['customer']}</td></tr>
                  <tr><td><strong>Document number</strong></td><td>{record.get('document_number', 'N/A')}</td></tr>
                  <tr><td><strong>Revision number</strong></td><td>{record.get('revision_number', 'N/A')}</td></tr>
                  <tr><td><strong>Category</strong></td><td>{record.get('category', 'N/A')}</td></tr>
                  <tr><td><strong>Status</strong></td><td><span style="background:{status_bg};color:{status_color};padding:4px 8px;border-radius:4px;font-weight:600;">{status}</span></td></tr>
                  <tr><td><strong>Updated at</strong></td><td>{decision_made_at or record.get('approval_updated_at', 'N/A')}</td></tr>
                  {rejection_html}
                </table>
                <p style="margin-top:16px;color:#6e7681;">You can view your document in the Smart DMS dashboard.</p>
            """
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def send_master_records_final_notification(to_emails, record, approved_at=None):
        """Notify selected people after final Master Records approval."""
        try:
            recipients = [email for email in to_emails if email]
            if not recipients:
                return True, None

            msg = Message(
                subject=f"Master Records approved: {record['file_name']}",
                recipients=recipients,
            )
            msg.body = (
                "A Master Records document has received final approval.\n\n"
                f"File: {record['file_name']}\n"
                f"Plant: {record['plant']}\n"
                f"Department: {record['department']}\n"
                f"Document number: {record.get('document_number', 'N/A')}\n"
                f"Revision number: {record.get('revision_number', 'N/A')}\n"
                f"First approver: {record.get('first_approver', 'N/A')}\n"
                f"Final approver: {record.get('final_approver', 'N/A')}\n"
                f"Approved at: {approved_at or record.get('final_approved_at') or record.get('approval_updated_at', 'N/A')}\n"
            )
            msg.html = f"""
                <p>A Master Records document has received final approval.</p>
                <table cellpadding="6" cellspacing="0" border="0">
                  <tr><td><strong>File</strong></td><td>{record['file_name']}</td></tr>
                  <tr><td><strong>Plant</strong></td><td>{record['plant']}</td></tr>
                  <tr><td><strong>Department</strong></td><td>{record['department']}</td></tr>
                  <tr><td><strong>Document number</strong></td><td>{record.get('document_number', 'N/A')}</td></tr>
                  <tr><td><strong>Revision number</strong></td><td>{record.get('revision_number', 'N/A')}</td></tr>
                  <tr><td><strong>First approver</strong></td><td>{record.get('first_approver', 'N/A')}</td></tr>
                  <tr><td><strong>Final approver</strong></td><td>{record.get('final_approver', 'N/A')}</td></tr>
                  <tr><td><strong>Approved at</strong></td><td>{approved_at or record.get('final_approved_at') or record.get('approval_updated_at', 'N/A')}</td></tr>
                </table>
            """
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)
