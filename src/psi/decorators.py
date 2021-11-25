from rest_framework import status
from rest_framework.response import Response

from datetime import datetime


def validate_datetime(func):
    def search(view, request, *args, **kwargs):
        try:
            data = request.data

            if data.get("date_param") is not None:
                kwargs['param'] = {
                    "type": "date",
                    "value": datetime.strptime(data.get("date_param"), "%Y-%m-%d")
                }
            elif data.get("datetime_param") is not None:
                kwargs['param'] = {
                    "type": "datetime",
                    "value": datetime.strptime(data.get("datetime_param"), "%Y-%m-%d %H:%M:%S")
                }
            else:
                return Response({'error': "Missing parameter"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Invalid datetime format"}, status=status.HTTP_400_BAD_REQUEST)
        return func(view, request, *args, **kwargs)
    return search