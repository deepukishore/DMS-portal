from datetime import datetime
from html import escape

from flask_mail import Message

from extensions import mail
from services.presentation_service import plant_code


class MailService:
    """Handles outbound email delivery."""

    @staticmethod
    def send_password_reset(to_email, reset_url):
        try:
            msg = Message(
                subject="Document Management System Password Reset",
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
            recipients = to_email if isinstance(to_email, list) else [to_email]
            recipients = [email for email in recipients if email]
            if not recipients:
                return False, "No approval recipients configured."

            file_name = record.get("original_file_name") or record.get("file_name") or "Document"
            approval_status = record.get("approval_status") or "Pending"
            is_final_stage = approval_status == "Pending Final Approval"
            stage_label = "Final approval" if is_final_stage else "First-stage approval"
            status_label = "Pending final approval" if is_final_stage else "Pending first-stage review"
            uploaded_by = record.get("name") or "Not available"
            user_id = record.get("user_id") or "N/A"
            uploaded_at = record.get("uploaded_at") or "N/A"
            current_year = datetime.now().year

            def safe(value, fallback="N/A"):
                text = str(value or fallback)
                return escape(text, quote=True)

            msg = Message(
                subject=f"Action required - {stage_label}: {file_name}",
                recipients=recipients,
            )
            msg.body = (
                "Dear Reviewer,\n\n"
                f"A document requires your {stage_label.lower()} in the Document Management System.\n\n"
                f"Document: {file_name}\n"
                f"Uploaded by: {uploaded_by} ({user_id})\n"
                f"Uploaded at: {uploaded_at}\n"
                f"Plant: {plant_code(record.get('plant', ''))}\n"
                f"Department: {record.get('department') or 'N/A'}\n"
                f"Customer: {record.get('customer') or 'N/A'}\n"
                f"Document number: {record.get('document_number') or 'N/A'}\n"
                f"Revision number: {record.get('revision_number') or 'N/A'}\n"
                f"Category: {record.get('category') or 'N/A'}\n"
                f"Approval status: {status_label}\n\n"
                "Please preview the document, verify its details, and record your decision. "
                "If changes are needed, select Update required and provide clear comments.\n\n"
                f"Review document: {review_url}\n\n"
                "This is a system-generated email. Please do not reply to it."
            )
            msg.html = f"""
              <!doctype html>
              <html lang="en">
                <body style="margin:0;padding:0;background:#eaf3f8;font-family:Arial,Helvetica,sans-serif;color:#344054;">
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#eaf3f8;">
                    <tr>
                      <td align="center" style="padding:24px 12px;">
                        <table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:640px;background:#ffffff;border:1px solid #d8e3ec;border-radius:8px;overflow:hidden;">
                          <tr>
                            <td align="center" style="padding:24px 28px;background:#075d98;background:linear-gradient(105deg,#075d98 0%,#08a5d7 100%);color:#ffffff;">
                              <div style="font-size:22px;line-height:1.25;font-weight:700;">Document Approval Request</div>
                              <div style="margin-top:7px;font-size:12px;line-height:1.5;color:#e9f8ff;">Document Management System &nbsp;|&nbsp; Secure review and controlled approval</div>
                            </td>
                          </tr>
                          <tr>
                            <td style="padding:26px 30px 22px;">
                              <p style="margin:0 0 14px;font-size:14px;line-height:1.55;color:#344054;">Dear Reviewer,</p>
                              <p style="margin:0 0 18px;font-size:14px;line-height:1.65;color:#475467;">
                                A document has been submitted and requires your <strong style="color:#1d2939;">{safe(stage_label.lower())}</strong>.
                              </p>

                              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-size:13px;line-height:1.45;">
                                <tr><td style="width:150px;padding:5px 10px 5px 0;color:#475467;font-weight:700;">Document</td><td style="padding:5px 0;color:#1d2939;word-break:break-word;">{safe(file_name)}</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Document number</td><td style="padding:5px 0;color:#1d2939;">{safe(record.get('document_number'))}</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Revision number</td><td style="padding:5px 0;color:#1d2939;">{safe(record.get('revision_number'))}</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Category</td><td style="padding:5px 0;color:#1d2939;">{safe(record.get('category'))}</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Plant</td><td style="padding:5px 0;color:#1d2939;">{safe(plant_code(record.get('plant', '')))}</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Department</td><td style="padding:5px 0;color:#1d2939;">{safe(record.get('department'))}</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Customer</td><td style="padding:5px 0;color:#1d2939;">{safe(record.get('customer'))}</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Uploaded by</td><td style="padding:5px 0;color:#1d2939;">{safe(uploaded_by)} ({safe(user_id)})</td></tr>
                                <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Uploaded at</td><td style="padding:5px 0;color:#1d2939;">{safe(uploaded_at)}</td></tr>
                              </table>

                              <div style="margin:20px 0 18px;padding:13px 15px;background:#f6f9fc;border-left:4px solid #087fb9;border-radius:4px;font-size:13px;line-height:1.6;color:#475467;">
                                <strong style="color:#1d2939;">Action required:</strong> Preview the document, verify the details, and record your decision. If changes are needed, choose <strong>Update required</strong> and provide clear comments for the uploader.
                              </div>

                              <div style="margin:0 0 12px;text-align:center;font-size:16px;color:#667085;">
                                <strong>Approval Status:</strong> {safe(status_label)}
                              </div>
                              <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center">
                                <tr>
                                  <td align="center" style="border-radius:6px;background:#087fb9;">
                                    <a href="{safe(review_url)}" style="display:inline-block;padding:12px 24px;color:#ffffff;font-size:13px;font-weight:700;text-decoration:none;border-radius:6px;">Review Document</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                          <tr>
                            <td align="center" style="padding:16px 24px;background:#e7edf4;border-top:1px solid #d2dce6;color:#d92d20;font-size:11px;line-height:1.65;">
                              <strong>&copy; {current_year} Rane Group | Confidential Information</strong><br />
                              This is a system-generated email. Please do not reply to it.
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </body>
              </html>
            """
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def send_approval_decision_notification(to_email, record, status, decision_made_at=None, rejection_comment=""):
        """Send notification to uploader about approval decision."""
        try:
            if status == "Approved":
                status_color, status_bg = "#3fb950", "rgba(63,185,80,.15)"
            elif status == "Hold":
                status_color, status_bg = "#d29922", "rgba(210,153,34,.15)"
            else:
                status_color, status_bg = "#f85149", "rgba(248,81,73,.15)"
            rejection_comment = (rejection_comment or "").strip()
            status_phrase = "placed on hold" if status == "Hold" else status.lower()
            subject_status = "On Hold" if status == "Hold" else status
            comment_block = ""
            if status in {"Rejected", "Hold"} and rejection_comment:
                comment_label = "Corrections requested" if status == "Hold" else "Rejection comments"
                comment_block = f"{comment_label}: {rejection_comment}\n"
            
            msg = Message(
                subject=f"Document {subject_status}: {record['file_name']}",
                recipients=[to_email],
            )
            msg.body = (
                f"Your document has been {status_phrase}.\n\n"
                f"File: {record['file_name']}\n"
                f"Uploaded by: {record['name']} ({record['user_id']})\n"
                f"Plant: {plant_code(record['plant'])}\n"
                f"Department: {record['department']}\n"
                f"Customer: {record['customer']}\n"
                f"Document number: {record.get('document_number', 'N/A')}\n"
                f"Revision number: {record.get('revision_number', 'N/A')}\n"
                f"Category: {record.get('category', 'N/A')}\n"
                f"Status: {status}\n"
                f"Updated at: {decision_made_at or record.get('approval_updated_at', 'N/A')}\n\n"
                f"{comment_block}\n"
                f"You can view your document in the Document Management System dashboard."
            )
            rejection_html = ""
            if status in {"Rejected", "Hold"} and rejection_comment:
                comment_label = "Corrections requested" if status == "Hold" else "Rejection comments"
                rejection_html = f"""
                  <tr><td><strong>{comment_label}</strong></td><td>{rejection_comment}</td></tr>
                """
            msg.html = f"""
                <p>Your document has been <strong>{status_phrase}</strong>.</p>
                <table cellpadding="6" cellspacing="0" border="0">
                  <tr><td><strong>File</strong></td><td>{record['file_name']}</td></tr>
                  <tr><td><strong>Uploaded by</strong></td><td>{record['name']} ({record['user_id']})</td></tr>
                  <tr><td><strong>Plant</strong></td><td>{plant_code(record['plant'])}</td></tr>
                  <tr><td><strong>Department</strong></td><td>{record['department']}</td></tr>
                  <tr><td><strong>Customer</strong></td><td>{record['customer']}</td></tr>
                  <tr><td><strong>Document number</strong></td><td>{record.get('document_number', 'N/A')}</td></tr>
                  <tr><td><strong>Revision number</strong></td><td>{record.get('revision_number', 'N/A')}</td></tr>
                  <tr><td><strong>Category</strong></td><td>{record.get('category', 'N/A')}</td></tr>
                  <tr><td><strong>Status</strong></td><td><span style="background:{status_bg};color:{status_color};padding:4px 8px;border-radius:4px;font-weight:600;">{status}</span></td></tr>
                  <tr><td><strong>Updated at</strong></td><td>{decision_made_at or record.get('approval_updated_at', 'N/A')}</td></tr>
                  {rejection_html}
                </table>
                <p style="margin-top:16px;color:#6e7681;">You can view your document in the Document Management System dashboard.</p>
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
                f"Plant: {plant_code(record['plant'])}\n"
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
                  <tr><td><strong>Plant</strong></td><td>{plant_code(record['plant'])}</td></tr>
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

    @staticmethod
    def send_final_shared_notification(to_emails, record, approved_at=None):
        """Notify selected people after final approval."""
        try:
            recipients = [email for email in to_emails if email]
            if not recipients:
                return True, None

            msg = Message(
                subject=f"Document approved and shared: {record['file_name']}",
                recipients=recipients,
            )
            approved_on = approved_at or record.get('final_approved_at') or record.get('approval_updated_at', 'N/A')
            msg.body = (
                "A document has received final approval and has been shared with you.\n\n"
                f"File: {record['file_name']}\n"
                f"Plant: {plant_code(record['plant'])}\n"
                f"Department: {record['department']}\n"
                f"Document number: {record.get('document_number', 'N/A')}\n"
                f"Revision number: {record.get('revision_number', 'N/A')}\n"
                f"First approver: {record.get('first_approver', 'N/A')}\n"
                f"Final approver: {record.get('final_approver', 'N/A')}\n"
                f"Approved at: {approved_on}\n"
            )
            msg.html = f"""
                <p>A document has received final approval and has been shared with you.</p>
                <table cellpadding="6" cellspacing="0" border="0">
                  <tr><td><strong>File</strong></td><td>{record['file_name']}</td></tr>
                  <tr><td><strong>Plant</strong></td><td>{plant_code(record['plant'])}</td></tr>
                  <tr><td><strong>Department</strong></td><td>{record['department']}</td></tr>
                  <tr><td><strong>Document number</strong></td><td>{record.get('document_number', 'N/A')}</td></tr>
                  <tr><td><strong>Revision number</strong></td><td>{record.get('revision_number', 'N/A')}</td></tr>
                  <tr><td><strong>First approver</strong></td><td>{record.get('first_approver', 'N/A')}</td></tr>
                  <tr><td><strong>Final approver</strong></td><td>{record.get('final_approver', 'N/A')}</td></tr>
                  <tr><td><strong>Approved at</strong></td><td>{approved_on}</td></tr>
                </table>
            """
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)
