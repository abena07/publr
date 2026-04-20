import os
from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["legal"])

_LAST_UPDATED = "April 18, 2026"


def _privacy_html() -> str:
    contact = os.environ.get("PUBLIC_CONTACT_EMAIL", "").strip()
    contact_block = (
        f'<p><strong>Contact:</strong> <a href="mailto:{escape(contact)}">{escape(contact)}</a></p>'
        if contact
        else "<p><strong>Contact:</strong> For privacy requests, email the operator of this Publr deployment.</p>"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Privacy Policy — Publr</title>
  <style>
    body {{ font-family: system-ui, sans-serif; line-height: 1.5; max-width: 42rem; margin: 2rem auto; padding: 0 1rem; color: #111; }}
    h1 {{ font-size: 1.75rem; }}
    h2 {{ font-size: 1.15rem; margin-top: 1.75rem; }}
    p, li {{ font-size: 0.95rem; }}
    .muted {{ color: #555; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Privacy Policy</h1>
  <p class="muted">Last updated: {_LAST_UPDATED}</p>
  <p>Publr (&ldquo;we&rdquo;, &ldquo;us&rdquo;) is a service that helps you publish images from Google Drive to Instagram. This policy describes how we handle information when you use Publr.</p>
  {contact_block}

  <h2>Information we collect</h2>
  <p><strong>Instagram.</strong> We store your <strong>Instagram access token</strong> (and your Instagram professional account id as returned by Meta) so we can <strong>publish photos and other images to your Instagram account on your behalf</strong> after you connect Instagram through Meta&rsquo;s login.</p>
  <ul>
    <li><strong>Account identifiers.</strong> We create and store a unique user id in our database when you sign in with Meta (Instagram).</li>
    <li><strong>Instagram connection data.</strong> We store your Instagram professional account identifier and Instagram access tokens issued by Meta; we use them only to authenticate to Instagram and to create and publish media on Instagram as you direct through Publr.</li>
    <li><strong>Google Drive connection data.</strong> If you connect Google Drive, we store OAuth tokens and the Google Drive folder id you configure so we can list and read image files you choose to sync.</li>
    <li><strong>Optional profile fields.</strong> Your user record may include an email address if the application collects one in the future; today the primary identifier is your connected accounts.</li>
    <li><strong>Operational data.</strong> We may persist Google Drive file identifiers and related URLs to avoid duplicate processing and to retry failed uploads. Image files are downloaded for processing, resized, sent to our image host, and published to Instagram as part of the service.</li>
    <li><strong>Session tokens.</strong> We issue signed session tokens (JWTs) so your client can call authenticated API routes.</li>
  </ul>

  <h2>How we use information</h2>
  <p>We use the data above only to operate Publr: authenticate you, read images from the Google Drive folder you select, upload processed images to our image hosting provider, publish to your Instagram account, and maintain reliable background processing.</p>

  <h2>Where data is processed and stored</h2>
  <p>Data is stored in our PostgreSQL database, on the application server&rsquo;s filesystem (for lightweight processing state files), and with the third-party services below. Hosting location depends on your deployment provider (for example, a cloud platform such as Railway).</p>

  <h2>Third-party services</h2>
  <p>We rely on service providers that have their own privacy policies:</p>
  <ul>
    <li><strong>Meta (Facebook / Instagram)</strong> for Instagram login and publishing.</li>
    <li><strong>Google</strong> for Google Drive access when you connect Drive.</li>
    <li><strong>Cloudinary</strong> for hosting uploaded images used in the publishing flow.</li>
    <li><strong>Hosting and database vendors</strong> that run the application and PostgreSQL.</li>
  </ul>

  <h2>Retention</h2>
  <p>We retain account and token data until you disconnect your accounts, you ask us to delete your data, or we delete it as part of routine service changes. You can request deletion of your information using the contact above.</p>

  <h2>Security</h2>
  <p>We use industry-standard measures appropriate to the service, including transport encryption (HTTPS) for web traffic, protecting secrets via environment configuration, and storing tokens only as needed to perform the automation you requested.</p>

  <h2>Your choices</h2>
  <p>You can stop processing by revoking Publr&rsquo;s access in your Meta and Google account security settings and by ceasing to use the service. You may contact us to request access to or deletion of personal information associated with your account.</p>

  <h2>Children</h2>
  <p>Publr is not directed to children under 13, and we do not knowingly collect personal information from children.</p>

  <h2>Changes</h2>
  <p>We may update this policy from time to time. We will adjust the &ldquo;Last updated&rdquo; date when we do.</p>
</body>
</html>"""


@router.get("/privacy", response_class=HTMLResponse)
def privacy_policy() -> HTMLResponse:
    return HTMLResponse(content=_privacy_html())
