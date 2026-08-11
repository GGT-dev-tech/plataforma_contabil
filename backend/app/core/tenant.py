import contextvars
from typing import Optional

# ContextVar to store the current tenant_id for the current request
_tenant_id_ctx_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "tenant_id", default=None
)

def set_tenant_id(tenant_id: str) -> contextvars.Token:
    """Sets the tenant_id in the current context."""
    return _tenant_id_ctx_var.set(tenant_id)

def get_tenant_id() -> Optional[str]:
    """Retrieves the tenant_id from the current context."""
    return _tenant_id_ctx_var.get()

def reset_tenant_id(token: contextvars.Token) -> None:
    """Resets the tenant_id in the current context."""
    _tenant_id_ctx_var.reset(token)
