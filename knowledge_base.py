"""
Knowledge Base articles for the Persona-Adaptive Customer Support Agent.
These documents are indexed into FAISS for RAG retrieval.
"""

KB_DOCUMENTS = [
    # ── Billing ──────────────────────────────────────────────────────────────
    {
        "title": "Billing & Invoice Issues",
        "content": (
            "Our billing cycle runs on the 1st of each month. Invoices are sent via email "
            "24 hours before the charge date. To update your payment method, navigate to "
            "Settings → Billing → Payment Methods. Charges appear within 2-3 business days. "
            "For disputed charges, contact billing@support.com with your invoice number. "
            "Refunds are processed within 5-7 business days."
        ),
        "category": "billing",
    },
    {
        "title": "Subscription Plans & Pricing",
        "content": (
            "We offer three plans: Starter ($9/mo), Professional ($29/mo), and Enterprise (custom). "
            "Annual billing gives a 20% discount. Upgrades take effect immediately; "
            "you are billed the prorated difference. Downgrades take effect at the next billing cycle. "
            "Enterprise plans include SLA guarantees, dedicated support, and SSO."
        ),
        "category": "billing",
    },
    # ── Technical ────────────────────────────────────────────────────────────
    {
        "title": "API Authentication & Rate Limits",
        "content": (
            "Authentication uses Bearer tokens (JWT). Obtain a token via POST /auth/token "
            "with your client_id and client_secret. Tokens expire in 3600 seconds; "
            "use the refresh endpoint to renew. Rate limits: 100 req/min on Starter, "
            "500 req/min on Professional, unlimited on Enterprise. "
            "429 responses include a Retry-After header specifying the wait time in seconds. "
            "Enable webhook signatures by setting X-Webhook-Secret in your dashboard."
        ),
        "category": "technical",
    },
    {
        "title": "SDK Integration Guide",
        "content": (
            "SDKs are available for Python, Node.js, Go, and Java. "
            "Install the Python SDK: pip install our-sdk. "
            "Initialize with: client = OurClient(api_key=os.getenv('API_KEY')). "
            "For async support use AsyncOurClient. "
            "Error codes: 400 Bad Request, 401 Unauthorized, 403 Forbidden, "
            "404 Not Found, 429 Rate Limited, 500 Internal Error. "
            "Enable debug logging by setting LOG_LEVEL=DEBUG."
        ),
        "category": "technical",
    },
    {
        "title": "Webhook Configuration",
        "content": (
            "Webhooks deliver real-time event notifications to your endpoint. "
            "Register a webhook URL in Settings → Developer → Webhooks. "
            "Supported events: payment.success, payment.failed, subscription.created, "
            "subscription.cancelled, user.created. "
            "Payloads are signed with HMAC-SHA256. Verify signatures using the secret "
            "shown in your dashboard. Webhook retries: 3 attempts over 24 hours with exponential backoff."
        ),
        "category": "technical",
    },
    {
        "title": "Data Export & Backup",
        "content": (
            "Export your data at any time from Settings → Data → Export. "
            "Formats supported: CSV, JSON, XML. Large exports are emailed as a download link. "
            "Automated backups run nightly; retention is 30 days on Starter, 90 days on Professional, "
            "1 year on Enterprise. Use the /v1/export endpoint programmatically with an admin token."
        ),
        "category": "technical",
    },
    # ── Account ──────────────────────────────────────────────────────────────
    {
        "title": "Password Reset & Account Security",
        "content": (
            "To reset your password, click 'Forgot Password' on the login page. "
            "A reset link is valid for 15 minutes. Enable two-factor authentication (2FA) "
            "under Settings → Security → 2FA. Supported 2FA methods: TOTP apps (Authenticator), "
            "SMS, and hardware keys (FIDO2). "
            "Accounts are locked after 5 failed login attempts; unlock via email verification."
        ),
        "category": "account",
    },
    {
        "title": "Team & User Management",
        "content": (
            "Invite team members from Settings → Team → Invite. "
            "Roles: Owner, Admin, Member, Viewer. "
            "Owners can manage billing; Admins manage users and integrations; "
            "Members have full product access; Viewers have read-only access. "
            "SCIM provisioning is available on Enterprise plans for automated user lifecycle management. "
            "Remove a user by clicking the trash icon next to their name in Settings → Team."
        ),
        "category": "account",
    },
    {
        "title": "SSO & SAML Configuration",
        "content": (
            "Single Sign-On (SSO) is available on Enterprise plans. "
            "Supported protocols: SAML 2.0 and OIDC. "
            "Configure SSO in Settings → Security → SSO. "
            "You will need to provide your Identity Provider (IdP) metadata URL or XML. "
            "Test the configuration using the Test SSO button before enforcing it. "
            "Once enforced, password login is disabled for all non-owner users."
        ),
        "category": "technical",
    },
    # ── Performance ──────────────────────────────────────────────────────────
    {
        "title": "Service Uptime & SLA",
        "content": (
            "We guarantee 99.9% uptime on Professional and 99.99% on Enterprise (SLA). "
            "Scheduled maintenance windows are announced 48 hours in advance via the status page. "
            "Check real-time status at status.ourservice.com. "
            "SLA credits are issued automatically: 10% for <99.9% uptime, 25% for <99.5%. "
            "Incidents are tracked and post-mortems published within 72 hours."
        ),
        "category": "account",
    },
    {
        "title": "Performance Optimization Tips",
        "content": (
            "Use pagination (page & per_page params) for list endpoints to reduce payload size. "
            "Cache API responses using ETags; send If-None-Match header to get 304 responses. "
            "Batch operations are supported via /v1/batch endpoint — send up to 50 items per call. "
            "Enable gzip compression by sending Accept-Encoding: gzip in your requests. "
            "Use regional endpoints (us.api.ourservice.com, eu.api.ourservice.com) for lower latency."
        ),
        "category": "technical",
    },
    # ── Cancellation ─────────────────────────────────────────────────────────
    {
        "title": "Cancellation & Refund Policy",
        "content": (
            "You may cancel your subscription at any time from Settings → Billing → Cancel Plan. "
            "Cancellation takes effect at the end of your current billing period. "
            "No refunds are given for partial months except within the first 14 days (money-back guarantee). "
            "Enterprise cancellations must be submitted via your account manager with 30 days notice. "
            "After cancellation, your data is retained for 30 days before permanent deletion."
        ),
        "category": "billing",
    },
    # ── Onboarding ───────────────────────────────────────────────────────────
    {
        "title": "Getting Started – Onboarding Checklist",
        "content": (
            "1. Verify your email address. "
            "2. Complete your profile under Settings → Profile. "
            "3. Connect your first integration (Settings → Integrations). "
            "4. Create your first project or workspace. "
            "5. Invite teammates. "
            "6. Set up notifications under Settings → Notifications. "
            "Onboarding videos are available at help.ourservice.com/getting-started."
        ),
        "category": "account",
    },
]
