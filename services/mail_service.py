from datetime import datetime
from html import escape

from flask_mail import Message

from extensions import mail
from services.presentation_service import plant_code


def _safe_html(value, fallback="N/A"):
    return escape(str(value or fallback), quote=True)


def _build_status_email_html(
    *,
    title,
    subtitle,
    intro,
    details,
    status_label,
    header_start,
    header_end,
    badge_background,
    badge_color,
    note="",
):
    detail_rows = "".join(
        f"""
          <tr>
            <td style="width:150px;padding:5px 10px 5px 0;color:#475467;font-weight:700;">{_safe_html(label)}</td>
            <td style="padding:5px 0;color:#1d2939;word-break:break-word;">{_safe_html(value)}</td>
          </tr>
        """
        for label, value in details
    )
    note_block = (
        f"""
          <div style="margin:20px 0 0;padding:13px 15px;background:#f6f9fc;border-left:4px solid {header_start};border-radius:4px;font-size:13px;line-height:1.6;color:#475467;">
            {_safe_html(note)}
          </div>
        """
        if note
        else ""
    )
    current_year = datetime.now().year
    return f"""
      <!doctype html>
      <html lang="en">
        <body style="margin:0;padding:0;background:#eef3f7;font-family:Arial,Helvetica,sans-serif;color:#344054;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#eef3f7;">
            <tr>
              <td align="center" style="padding:24px 12px;">
                <table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:640px;background:#ffffff;border:1px solid #d8e3ec;border-radius:8px;overflow:hidden;">
                  <tr>
                    <td align="center" style="padding:24px 28px;background:{header_start};background:linear-gradient(105deg,{header_start} 0%,{header_end} 100%);color:#ffffff;">
                      <div style="font-size:22px;line-height:1.25;font-weight:700;">{_safe_html(title)}</div>
                      <div style="margin-top:7px;font-size:12px;line-height:1.5;color:#ffffff;opacity:.92;">{_safe_html(subtitle)}</div>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:26px 30px 22px;">
                      <p style="margin:0 0 18px;font-size:14px;line-height:1.65;color:#475467;">{_safe_html(intro)}</p>
                      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-size:13px;line-height:1.45;">
                        {detail_rows}
                      </table>
                      {note_block}
                      <div style="margin:22px 0 4px;text-align:center;font-size:16px;color:#667085;">
                        <strong>Status:</strong>
                        <span style="display:inline-block;margin-left:5px;padding:5px 10px;background:{badge_background};color:{badge_color};border-radius:999px;font-size:13px;font-weight:700;">{_safe_html(status_label)}</span>
                      </div>
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
                header_start, header_end = "#168a50", "#27b36a"
                status_color, status_bg = "#137a46", "#dcf7e8"
            elif status == "Hold":
                header_start, header_end = "#c77800", "#f0a500"
                status_color, status_bg = "#9a5b00", "#fff1d6"
            else:
                header_start, header_end = "#b42318", "#e5484d"
                status_color, status_bg = "#a11f16", "#fde7e7"
            rejection_comment = (rejection_comment or "").strip()
            status_phrase = "marked as update required" if status == "Hold" else status.lower()
            subject_status = "Update Required" if status == "Hold" else status
            comment_block = ""
            if status in {"Rejected", "Hold"} and rejection_comment:
                comment_label = "Update requested" if status == "Hold" else "Rejection comments"
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
                comment_label = "Update requested" if status == "Hold" else "Rejection comments"
                rejection_html = rejection_comment
            display_status = "Update required" if status == "Hold" else status
            details = [
                ("Document", record.get("original_file_name") or record.get("file_name")),
                ("Uploaded by", f"{record.get('name') or 'N/A'} ({record.get('user_id') or 'N/A'})"),
                ("Plant", plant_code(record.get("plant", ""))),
                ("Department", record.get("department")),
                ("Customer", record.get("customer")),
                ("Document number", record.get("document_number")),
                ("Revision number", record.get("revision_number")),
                ("Category", record.get("category")),
                ("Updated at", decision_made_at or record.get("approval_updated_at")),
            ]
            if rejection_html:
                details.append((comment_label, rejection_html))
            msg.html = _build_status_email_html(
                title=f"Document {subject_status}",
                subtitle="Document Management System | Approval decision notification",
                intro=f"Your document has been {status_phrase}.",
                details=details,
                status_label=display_status,
                header_start=header_start,
                header_end=header_end,
                badge_background=status_bg,
                badge_color=status_color,
                note="Open the Document Management System dashboard to review the latest document status.",
            )
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
            approved_on = approved_at or record.get("final_approved_at") or record.get("approval_updated_at")
            msg.html = _build_status_email_html(
                title="Master Records Approved",
                subtitle="Document Management System | Final approval notification",
                intro="A Master Records document has received final approval.",
                details=[
                    ("Document", record.get("original_file_name") or record.get("file_name")),
                    ("Plant", plant_code(record.get("plant", ""))),
                    ("Department", record.get("department")),
                    ("Document number", record.get("document_number")),
                    ("Revision number", record.get("revision_number")),
                    ("First approver", record.get("first_approver")),
                    ("Final approver", record.get("final_approver")),
                    ("Approved at", approved_on),
                ],
                status_label="Approved",
                header_start="#168a50",
                header_end="#27b36a",
                badge_background="#dcf7e8",
                badge_color="#137a46",
            )
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
            msg.html = _build_status_email_html(
                title="Document Approved and Shared",
                subtitle="Document Management System | Final approval notification",
                intro="A document has received final approval and has been shared with you.",
                details=[
                    ("Document", record.get("original_file_name") or record.get("file_name")),
                    ("Plant", plant_code(record.get("plant", ""))),
                    ("Department", record.get("department")),
                    ("Document number", record.get("document_number")),
                    ("Revision number", record.get("revision_number")),
                    ("First approver", record.get("first_approver")),
                    ("Final approver", record.get("final_approver")),
                    ("Approved at", approved_on),
                ],
                status_label="Approved",
                header_start="#168a50",
                header_end="#27b36a",
                badge_background="#dcf7e8",
                badge_color="#137a46",
            )
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def send_quarterly_document_reminder(
        to_emails,
        record,
        document_url,
        revision_upload_url,
    ):
        """Ask document stakeholders to review an approved file each quarter."""
        try:
            recipients = sorted({
                str(email or "").strip().lower()
                for email in to_emails
                if str(email or "").strip()
            })
            if not recipients:
                return False, "No quarterly reminder recipients were found."

            file_name = record.get("original_file_name") or record.get("file_name") or "Document"
            safe_document_url = _safe_html(document_url, "#")
            safe_revision_url = _safe_html(revision_upload_url, "#")
            current_year = datetime.now().year
            msg = Message(
                subject=f"Quarterly document review required: {file_name}",
                recipients=recipients,
            )
            msg.body = (
                "This is your quarterly reminder to review the controlled document below.\n\n"
                f"Document: {file_name}\n"
                f"Document number: {record.get('document_number') or 'N/A'}\n"
                f"Revision number: {record.get('revision_number') or 'N/A'}\n"
                f"Plant: {plant_code(record.get('plant', ''))}\n"
                f"Department: {record.get('department') or 'N/A'}\n\n"
                "If the document is still current, no upload is required. If anything has changed, "
                "upload the revised document for approval using the link below.\n\n"
                f"Upload revised document: {revision_upload_url}\n"
                f"View current document: {document_url}\n\n"
                "This is a system-generated email. Please do not reply to it."
            )
            msg.html = f"""
              <!doctype html>
              <html lang="en">
                <body style="margin:0;padding:0;background:#eef3f7;font-family:Arial,Helvetica,sans-serif;color:#344054;">
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#eef3f7;">
                    <tr><td align="center" style="padding:24px 12px;">
                      <table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:640px;background:#ffffff;border:1px solid #d8e3ec;border-radius:8px;overflow:hidden;">
                        <tr><td align="center" style="padding:24px 28px;background:#075d98;background:linear-gradient(105deg,#075d98 0%,#08a5d7 100%);color:#ffffff;">
                          <div style="font-size:22px;line-height:1.25;font-weight:700;">Quarterly Document Review</div>
                          <div style="margin-top:7px;font-size:12px;line-height:1.5;">Confirm that this controlled document is still current</div>
                        </td></tr>
                        <tr><td style="padding:26px 30px 22px;">
                          <p style="margin:0 0 18px;font-size:14px;line-height:1.65;color:#475467;">Please review this document. If its content has changed, upload a revised version for approval.</p>
                          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-size:13px;line-height:1.45;">
                            <tr><td style="width:150px;padding:5px 10px 5px 0;color:#475467;font-weight:700;">Document</td><td style="padding:5px 0;color:#1d2939;word-break:break-word;">{_safe_html(file_name)}</td></tr>
                            <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Document number</td><td style="padding:5px 0;color:#1d2939;">{_safe_html(record.get('document_number'))}</td></tr>
                            <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Revision number</td><td style="padding:5px 0;color:#1d2939;">{_safe_html(record.get('revision_number'))}</td></tr>
                            <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Plant</td><td style="padding:5px 0;color:#1d2939;">{_safe_html(plant_code(record.get('plant', '')))}</td></tr>
                            <tr><td style="padding:5px 10px 5px 0;color:#475467;font-weight:700;">Department</td><td style="padding:5px 0;color:#1d2939;">{_safe_html(record.get('department'))}</td></tr>
                          </table>
                          <div style="margin:22px 0 12px;text-align:center;">
                            <a href="{safe_revision_url}" style="display:inline-block;padding:12px 22px;background:#087fb9;color:#ffffff;font-size:13px;font-weight:700;text-decoration:none;border-radius:6px;">Upload Revised Document</a>
                          </div>
                          <div style="text-align:center;font-size:12px;"><a href="{safe_document_url}" style="color:#087fb9;">View current document</a></div>
                        </td></tr>
                        <tr><td align="center" style="padding:16px 24px;background:#e7edf4;border-top:1px solid #d2dce6;color:#d92d20;font-size:11px;line-height:1.65;">
                          <strong>&copy; {current_year} Rane Group | Confidential Information</strong><br />
                          This is a system-generated email. Please do not reply to it.
                        </td></tr>
                      </table>
                    </td></tr>
                  </table>
                </body>
              </html>
            """
            mail.send(msg)
            return True, None
        except Exception as exc:
            return False, str(exc)
