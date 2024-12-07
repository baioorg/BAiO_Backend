from django.http import JsonResponse

def list_models(request):
    mock_response = {
        "object": "list",
        "data": [
            {"id": "mock-model-001", "object": "model", "created": 0, "owned_by": "system"},
            {"id": "mock-model-002", "object": "model", "created": 0, "owned_by": "system"},
            {"id": "mock-model-003", "object": "model", "created": 0, "owned_by": "system"},
        ]
    }
    return JsonResponse(mock_response)
