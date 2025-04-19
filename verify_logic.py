
import re
import smtplib
import socket
import dns.resolver

DISPOSABLE_DOMAINS = {"mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com"}
BLACKLISTED_DOMAINS = {"spamdomain.com", "fakemail.net"}
ROLE_BASED_PREFIXES = {"admin", "info", "support", "contact", "sales", "billing", "webmaster"}

def is_valid_syntax(email):
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(regex, email) is not None

def extract_domain(email):
    return email.lower().split("@")[-1]

def has_mx_record(domain):
    try:
        dns.resolver.resolve(domain, "MX")
        return True
    except Exception:
        return False

def smtp_check(email):
    try:
        domain = extract_domain(email)
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_host = str(mx_records[0].exchange)
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_host)
        server.helo("example.com")
        server.mail("me@example.com")
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

def is_disposable(domain):
    return domain in DISPOSABLE_DOMAINS

def is_blacklisted(domain):
    return domain in BLACKLISTED_DOMAINS

def is_role_based(email):
    prefix = email.lower().split("@")[0]
    return prefix in ROLE_BASED_PREFIXES

def verify_email(email):
    domain = extract_domain(email)
    syntax = is_valid_syntax(email)
    mx = has_mx_record(domain) if syntax else False
    smtp = smtp_check(email) if mx else False
    disposable = is_disposable(domain)
    blacklisted = is_blacklisted(domain)
    role_based = is_role_based(email)

    risk_score = 1
    if not syntax:
        risk_score = 10
    elif not mx:
        risk_score = 8
    elif not smtp:
        risk_score = 7
    elif disposable:
        risk_score = 6
    elif blacklisted:
        risk_score = 9
    elif role_based:
        risk_score = 4

    status = "valid" if risk_score <= 3 else "risky" if risk_score <= 7 else "invalid"

    return {
        "email": email,
        "status": status,
        "risk_score": risk_score,
        "syntax": syntax,
        "mx": mx,
        "smtp": smtp,
        "disposable": disposable,
        "blacklisted": blacklisted,
        "role_based": role_based
    }
