import inspect
import structlog
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar, Union, Dict

from ..exceptions import BaseAPIException


F = TypeVar("F", bound=Callable[..., Any])


def _scrub_context(context: Dict[str, Any]) -> Dict[str, Any]:
    scrub_keys = {"password", "hashed_password", "token", "access_token"}
    return {k: ("<redacted>" if k in scrub_keys else v) for k, v in context.items()}


def service_error_logger(operation: str) -> Callable[[F], F]:
    """Decorator for service methods to log errors with rich context.

    Logs domain context and re-raises exceptions so FastAPI/global handlers can respond.
    """

    log = structlog.get_logger()

    def decorator(func: F) -> F:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any):
                bound_args = inspect.signature(func).bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                ctx = {k: v for k, v in bound_args.arguments.items() if k != "self"}
                ctx = _scrub_context(ctx)
                try:
                    return await func(*args, **kwargs)
                except BaseAPIException as exc:
                    log.warning(
                        "service_error",
                        operation=operation,
                        service=getattr(args[0].__class__, "__name__", args[0].__class__.__name__),
                        method=func.__name__,
                        **ctx,
                        detail=str(exc.detail),
                        status_code=exc.status_code,
                    )
                    raise
                except Exception as exc:
                    log.error(
                        "service_unexpected_error",
                        operation=operation,
                        service=getattr(args[0].__class__, "__name__", args[0].__class__.__name__),
                        method=func.__name__,
                        **ctx,
                        error=str(exc),
                        exc_info=True,
                    )
                    raise

            return async_wrapper  # type: ignore[return-value]

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any):
            bound_args = inspect.signature(func).bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            ctx = {k: v for k, v in bound_args.arguments.items() if k != "self"}
            ctx = _scrub_context(ctx)
            try:
                return func(*args, **kwargs)
            except BaseAPIException as exc:
                log.warning(
                    "service_error",
                    operation=operation,
                    service=getattr(args[0].__class__, "__name__", args[0].__class__.__name__),
                    method=func.__name__,
                    **ctx,
                    detail=str(exc.detail),
                    status_code=exc.status_code,
                )
                raise
            except Exception as exc:
                log.error(
                    "service_unexpected_error",
                    operation=operation,
                    service=getattr(args[0].__class__, "__name__", args[0].__class__.__name__),
                    method=func.__name__,
                    **ctx,
                    error=str(exc),
                    exc_info=True,
                )
                raise

        return sync_wrapper  # type: ignore[return-value]

    return decorator


