from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import uuid
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    request = context.get("request")
    response = exception_handler(exc, context)

    error_id = str(uuid.uuid4())

    if response is not None:
        # Normalizar errores a formato consistente
        errors = {}
        
        if isinstance(response.data, dict):
            # Si es dict, mantener la estructura
            errors = response.data
        elif isinstance(response.data, list):
            # Si es lista, poner en non_field_errors
            errors = {"non_field_errors": response.data}
        else:
            # Cualquier otro caso
            errors = {"detail": str(response.data)}
        
        data = {
            "error_id": error_id,
            "errors": errors,
        }
        
        logger.warning(
            "API error",
            extra={
                "error_id": error_id,
                "path": getattr(request, "path", None),
                "method": getattr(request, "method", None),
                "status_code": response.status_code,
            },
        )
        return Response(data, status=response.status_code)

    # Errores no controlados (500)
    logger.exception(
        "Unhandled exception",
        extra={
            "error_id": error_id,
            "path": getattr(request, "path", None),
            "method": getattr(request, "method", None),
        },
    )
    return Response(
        {
            "error_id": error_id,
            "errors": {"detail": "Internal server error"}
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )