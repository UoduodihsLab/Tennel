from app.crud.account import AccountCRUD
from app.exceptions import AlreadyExistError
from app.schemas.account import AccountCreate, AccountResponse


class AccountService:
    def __init__(self):
        self.crud = AccountCRUD()

    async def create_account(self, create_data: AccountCreate):
        created_account = self.crud.get_by_phone(create_data.phone)

        if created_account:
            raise AlreadyExistError('此账号已存在，请勿重复添加')

        create_dict = create_data.model_dump()

        create_dict.update({'session_name': create_data.phone})

        new_account = self.crud.create(create_dict)

        return AccountResponse.model_validate(new_account)
