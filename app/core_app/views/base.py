from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from ..tasks import send_email_template_test
from drf_yasg.utils import swagger_auto_schema

# Create your views here.


class SendEmailTemplateTest(viewsets.ViewSet):
    @swagger_auto_schema(
        request_body={
            "email": "string",
        },
        responses={200: "Send email template success!"},
    )
    def list(self, request):
        email = request.query_params.get("email")
        send_email_template_test(email)
        return Response(
            {"message": "Send email template success!"}, status=status.HTTP_200_OK
        )
