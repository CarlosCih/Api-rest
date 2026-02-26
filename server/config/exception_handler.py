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
        # Errores DRF (400, 401, 403, 404, etc.)
        data = {
            "error_id": error_id,
            "detail": response.data,
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
        {"error_id": error_id, "detail": "Internal server error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )