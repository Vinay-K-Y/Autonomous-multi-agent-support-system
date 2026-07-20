from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.db.repositories import UserRepository
from app.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(request: Request):
    """
    Dependency to get the current authenticated user from the request.
    This can be used in route handlers like:
    
    @router.get("/protected")
    async def protected_route(current_user = Depends(get_current_user)):
        return {"message": f"Hello {current_user.email}"}
    """
    try:
        # Get token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        async for db in get_db():
            user = await UserRepository.get_by_email(db, email)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive",
                )

            # Store user in request state for later use
            request.state.user = user
            return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def optional_auth(request: Request):
    """
    Optional authentication - doesn't require auth but provides user if available.
    Useful for endpoints that work for both authenticated and unauthenticated users.
    """
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            request.state.user = None
            return None

        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        
        if payload is None:
            request.state.user = None
            return None

        email = payload.get("sub")
        if email is None:
            request.state.user = None
            return None

        async for db in get_db():
            user = await UserRepository.get_by_email(db, email)
            request.state.user = user
            return user

    except Exception:
        request.state.user = None
        return None
