import strawberry
from strawberry.fastapi import GraphQLRouter
from app.db.schemas import UserOut
from app.core.security import get_current_user

@strawberry.type
class Query:
    @strawberry.field
    async def current_user(self, info) -> UserOut:
        user = await get_current_user(info.context["request"])
        return UserOut.from_orm(user)

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)