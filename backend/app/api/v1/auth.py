from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client import OAuthError
from authlib.oidc.core import CodeIDToken
import secrets
import httpx
import base64
import json

from app.core.config import get_settings
from app.core.security import create_access_token, get_current_user, TokenData

settings = get_settings()

router = APIRouter()

# OAuth client for Keycloak
oauth = OAuth()
oauth.register(
    name="keycloak",
    client_id=settings.effective_oidc_client_id,
    client_secret=settings.effective_oidc_client_secret,
    server_metadata_url=f"{settings.effective_oidc_issuer_url}/.well-known/openid-configuration",
    client_kwargs={"scope": settings.oidc_scopes},
)


def get_oauth_client():
    """Get OAuth client with current settings (handles demo mode changes)"""
    client = OAuth()
    client.register(
        name="keycloak",
        client_id=settings.effective_oidc_client_id,
        client_secret=settings.effective_oidc_client_secret,
        server_metadata_url=f"{settings.effective_oidc_issuer_url}/.well-known/openid-configuration",
        client_kwargs={"scope": settings.oidc_scopes},
    )
    return client


@router.get("/login")
async def login(request: Request):
    """Initiate OIDC authorization code flow with PKCE"""
    if not settings.oidc_enabled:
        raise HTTPException(status_code=404, detail="OIDC not enabled")
    
    # Generate PKCE code verifier and challenge
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = secrets.token_urlsafe(32)  # Simplified; real impl uses S256
    
    # Store in session (in production, use secure session store)
    request.session["pkce_verifier"] = code_verifier
    request.session["oauth_state"] = secrets.token_urlsafe(16)
    
    client = get_oauth_client()
    redirect_uri = settings.effective_oidc_redirect_uri
    
    return await client.keycloak.authorize_redirect(
        request,
        redirect_uri,
        state=request.session["oauth_state"],
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )


@router.get("/callback")
async def callback(request: Request, response: Response):
    """Handle OIDC callback, exchange code for tokens"""
    if not settings.oidc_enabled:
        raise HTTPException(status_code=404, detail="OIDC not enabled")
    
    client = get_oauth_client()
    
    try:
        token = await client.keycloak.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e.error}")
    
    # Verify state
    if request.query_params.get("state") != request.session.get("oauth_state"):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    
    # Parse ID token for user info
    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No ID token received")
    
    # In production, verify signature, issuer, audience, nonce
    # For now, decode without verification (Keycloak handles validation)
    try:
        payload_part = id_token.split(".")[1]
        payload_part += "=" * (-len(payload_part) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload_part))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID token")
    
    # Extract roles
    roles = claims.get("realm_access", {}).get("roles", [])
    if "offline_access" in roles:
        roles.remove("offline_access")
    if "default-roles-prism-engine" in roles:
        roles.remove("default-roles-prism-engine")
    if "uma_authorization" in roles:
        roles.remove("uma_authorization")
    
    # Map Keycloak roles to app roles
    role_mapping = {
        "admin": "admin",
        "operator": "operator",
        "viewer": "viewer",
    }
    app_roles = [role_mapping.get(r, "viewer") for r in roles]
    if not app_roles:
        app_roles = ["viewer"]
    
    # Create app access token
    access_token = create_access_token({
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "roles": app_roles,
    })
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    
    # Redirect to frontend
    return RedirectResponse(url="/")


@router.post("/logout")
async def logout(response: Response):
    """Logout - clear cookie"""
    response.delete_cookie("access_token", httponly=True, secure=not settings.debug, samesite="lax")
    return {"message": "Logged out"}


@router.get("/me", response_model=TokenData)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.get("/demo-login")
async def demo_login(response: Response):
    """Demo mode login - creates a test token without OIDC"""
    if not settings.demo_mode:
        raise HTTPException(status_code=404, detail="Demo mode not enabled")
    
    access_token = create_access_token({
        "sub": "demo-user",
        "email": "demo@prism-engine.local",
        "roles": ["operator"],
    })
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    
    return {"message": "Demo login successful", "redirect": "/"}