import json
from django.core.management.base import BaseCommand
from chat.models import LLMProvider, Model

class Command(BaseCommand):
    help = "Load LLM providers and models from a JSON file"

    def handle(self, *args, **kwargs):
        # Load JSON data
        with open("chat/management/LLM_Providers_Models.json", "r") as file:
            data = json.load(file)


        # Parse and save data to the database
        for provider_data in data["LLM-providers"]:
            provider, _ = LLMProvider.objects.get_or_create(id=provider_data["id"], url=provider_data["url"], name=provider_data["name"])

            for model_data in provider_data["models"]:
                Model.objects.get_or_create(
                    id=model_data["id"],
                    name=model_data["name"],
                    provider=provider
                )

        self.stdout.write(self.style.SUCCESS("Data loaded successfully"))
