import resend
from fastapi import BackgroundTasks
from app.config import settings

resend.api_key = settings.RESEND_API_KEY


class EmailService:
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    async def send_verification_code(self, to_email: str, username: str, code: str):
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Verify your email - Reviewly</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #0a0a0a;
            color: #f5f5f5;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        .wrapper {{
            width: 100%;
            padding: 32px 16px;
            background:
                radial-gradient(circle at top, rgba(59, 130, 246, 0.16), transparent 30%),
                radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.08), transparent 24%),
                linear-gradient(180deg, rgba(255, 255, 255, 0.015), rgba(255, 255, 255, 0));
            background-color: #0a0a0a;
        }}

        .shell {{
            max-width: 640px;
            margin: 0 auto;
        }}

        .brand {{
            text-align: center;
            margin-bottom: 18px;
        }}

        .brand-mark {{
            width: 56px;
            height: 56px;
            margin: 0 auto 14px;
            border-radius: 18px;
            background: rgba(59, 130, 246, 0.14);
            border: 1px solid rgba(59, 130, 246, 0.22);
            color: #3b82f6;
            font-size: 22px;
            font-weight: 700;
            line-height: 56px;
            font-family: "JetBrains Mono", Consolas, monospace;
            box-shadow: 0 0 0 1px rgba(59,130,246,0.18), 0 18px 50px rgba(8,15,36,0.45);
        }}

        .brand-name {{
            color: #f5f5f5;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: -0.02em;
            margin: 0;
        }}

        .brand-copy {{
            color: #a1a1aa;
            font-size: 14px;
            margin: 6px 0 0;
        }}

        .card {{
            background-color: rgba(17, 17, 17, 0.96);
            border: 1px solid #262626;
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
        }}

        .eyebrow {{
            display: inline-block;
            margin-bottom: 14px;
            color: rgba(59, 130, 246, 0.9);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            font-family: "JetBrains Mono", Consolas, monospace;
        }}

        h1 {{
            margin: 0 0 12px;
            color: #f5f5f5;
            font-size: 28px;
            line-height: 1.2;
            font-weight: 700;
            letter-spacing: -0.03em;
        }}

        p {{
            margin: 0 0 16px;
            color: #d4d4d8;
            font-size: 15px;
            line-height: 1.7;
        }}

        .code-block {{
            margin: 28px 0 20px;
            padding: 22px 20px;
            text-align: center;
            border-radius: 18px;
            border: 1px solid rgba(59, 130, 246, 0.3);
            background: linear-gradient(180deg, rgba(59, 130, 246, 0.12), rgba(59, 130, 246, 0.05));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
        }}

        .code-label {{
            margin: 0 0 10px;
            color: #a1a1aa;
            font-size: 11px;
            letter-spacing: 0.24em;
            text-transform: uppercase;
            font-family: "JetBrains Mono", Consolas, monospace;
        }}

        .code {{
            margin: 0;
            color: #f5f5f5;
            font-size: 40px;
            line-height: 1;
            font-weight: 700;
            letter-spacing: 0.32em;
            text-indent: 0.32em;
            font-family: "JetBrains Mono", Consolas, monospace;
        }}

        .meta {{
            margin-top: 18px;
            padding: 14px 16px;
            border-radius: 16px;
            background-color: rgba(34, 197, 94, 0.08);
            border: 1px solid rgba(34, 197, 94, 0.18);
            color: #bbf7d0;
            font-size: 14px;
        }}

        .warning {{
            margin-top: 18px;
            padding: 14px 16px;
            border-radius: 16px;
            background-color: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.18);
            color: #fca5a5;
            font-size: 14px;
            line-height: 1.6;
        }}

        .footer {{
            margin-top: 18px;
            color: #71717a;
            font-size: 12px;
            text-align: center;
            line-height: 1.6;
        }}

        .footer a {{
            color: #93c5fd;
            text-decoration: none;
        }}

        @media only screen and (max-width: 600px) {{
            .card {{
                padding: 24px;
                border-radius: 20px;
            }}

            h1 {{
                font-size: 24px;
            }}

            .code {{
                font-size: 32px;
                letter-spacing: 0.24em;
                text-indent: 0.24em;
            }}
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="shell">
            <div class="brand">
                <div class="brand-mark">R</div>
                <p class="brand-name">Reviewly</p>
                <p class="brand-copy">Structured async code review for engineering teams.</p>
            </div>

            <div class="card">
                <div class="eyebrow">Email Verification</div>
                <h1>Verify your email, {username}</h1>
                <p>Use the 6-digit code below to finish signing in and secure your Reviewly workspace.</p>

                <div class="code-block">
                    <p class="code-label">Verification Code</p>
                    <p class="code">{code}</p>
                </div>

                <div class="meta">
                    This code expires in <strong>15 minutes</strong>.
                </div>

                <div class="warning">
                    For your security, never share this code with anyone. Reviewly support will never ask for it.
                </div>

                <p style="margin-top: 24px;">
                    If you did not request this email, you can safely ignore it.
                </p>
            </div>

            <div class="footer">
                <p>&copy; 2026 Reviewly. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

        text_content = f"""Reviewly

Verify your email, {username}.

Use this 6-digit code to finish signing in to your Reviewly workspace:

{code}

This code expires in 15 minutes.

For your security, never share this code with anyone.
Reviewly support will never ask for it.

If you did not request this email, you can safely ignore it.

© 2026 Reviewly
"""

        params = resend.Emails.SendParams(
            from_=settings.FROM_EMAIL,
            to=[to_email],
            subject="Your verification code - Reviewly",
            html=html_content,
            text=text_content,
        )

        self.background_tasks.add_task(resend.Emails.send, params)
