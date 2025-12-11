import json
from functools import lru_cache

from fastapi import Depends

from api.v1.models.create_customer import CustomerCreate
from clients.crm_client import CrmClient, get_crm_client
from clients.schemas import ExternalCustomer


class CustomerService:

    def __init__(self, crm_client: CrmClient):
        self.crm_client = crm_client

    async def create_user(self, data: CustomerCreate):

        params = {
            "customer": json.dumps(
                {
                    "firstName": data.first_name,
                    "lastName": data.last_name,
                    "email": data.email,
                    "phones": [{"number": v.number} for v in data.phones],
                }
            )
        }

        return await self.crm_client.post(
            path="api/v5/customers/create", data={**params}
        )

    async def get_user(self, filters: dict):

        params = {
            "limit": filters.get("page_size"),
            "page": filters.get("page_number"),
            **{
                f"filter[{k}]": v
                for k, v in filters.items()
                if k not in ["page_number", "page_size"]
            },
        }

        response = await self.crm_client.get(path="api/v5/customers", params={**params})

        try:
            return [
                ExternalCustomer.model_validate(customer)
                for customer in response["customers"]
            ]
        except Exception as e:
            raise e


@lru_cache()
def get_customer_service(
    crm_client: CrmClient = Depends(get_crm_client),
) -> CustomerService:
    return CustomerService(crm_client)
