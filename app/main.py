# app/main.py
from typing import List, Optional
import strawberry
from fastapi import FastAPI, Request, HTTPException
from strawberry.fastapi import GraphQLRouter
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select


# -----------------------
# DB models (SQLModel)
# -----------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    is_active: bool = True

    houses: List["House"] = Relationship(back_populates="owner")
    garages: List["Garage"] = Relationship(back_populates="owner")
    cars: List["Car"] = Relationship(back_populates="owner")
    driver_license: Optional["DriverLicence"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"uselist": False}
    )


class House(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="houses")
    garages: List["Garage"] = Relationship(back_populates="house")


class Garage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    house_id: Optional[int] = Field(default=None, foreign_key="house.id")

    owner: Optional[User] = Relationship(back_populates="garages")
    house: Optional[House] = Relationship(back_populates="garages")
    cars: List["Car"] = Relationship(back_populates="garage")


class Car(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    garage_id: Optional[int] = Field(default=None, foreign_key="garage.id")

    owner: Optional[User] = Relationship(back_populates="cars")
    garage: Optional[Garage] = Relationship(back_populates="cars")


class DriverLicence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str
    user_id: int = Field(foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="driver_license")


# -----------------------
# DB setup
# -----------------------
sqlite_url = "sqlite:///./test_graphql.db"
engine = create_engine(sqlite_url, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


# -----------------------
# GraphQL types (Strawberry)
# -----------------------
@strawberry.type
class DriverLicenceType:
    id: int
    number: str

    @strawberry.field
    def owner(self, info) -> Optional["UserType"]:
        session: Session = info.context["session"]
        dl = session.get(DriverLicence, self.id)
        if not dl:
            return None
        u = session.get(User, dl.user_id)
        if not u:
            return None
        return UserType(id=u.id, email=u.email, is_active=u.is_active)


@strawberry.type
class CarType:
    id: int
    model: str

    @strawberry.field
    def owner(self, info) -> Optional["UserType"]:
        session: Session = info.context["session"]
        c = session.get(Car, self.id)
        if not c or not c.owner_id:
            return None
        u = session.get(User, c.owner_id)
        return UserType(id=u.id, email=u.email, is_active=u.is_active)

    @strawberry.field
    def garage(self, info) -> Optional["GarageType"]:
        session: Session = info.context["session"]
        c = session.get(Car, self.id)
        if not c or not c.garage_id:
            return None
        g = session.get(Garage, c.garage_id)
        return GarageType(id=g.id, title=g.title)


@strawberry.type
class GarageType:
    id: int
    title: str

    @strawberry.field
    def owner(self, info) -> Optional["UserType"]:
        session: Session = info.context["session"]
        g = session.get(Garage, self.id)
        if not g or not g.owner_id:
            return None
        u = session.get(User, g.owner_id)
        return UserType(id=u.id, email=u.email, is_active=u.is_active)

    @strawberry.field
    def house(self, info) -> Optional["HouseType"]:
        session: Session = info.context["session"]
        g = session.get(Garage, self.id)
        if not g or not g.house_id:
            return None
        h = session.get(House, g.house_id)
        return HouseType(id=h.id, title=h.title)

    @strawberry.field
    def cars(self, info) -> List[CarType]:
        session: Session = info.context["session"]
        cars = session.exec(select(Car).where(Car.garage_id == self.id)).all()
        return [CarType(id=c.id, model=c.model) for c in cars]


@strawberry.type
class HouseType:
    id: int
    title: str

    @strawberry.field
    def owner(self, info) -> Optional["UserType"]:
        session: Session = info.context["session"]
        h = session.get(House, self.id)
        if not h or not h.owner_id:
            return None
        u = session.get(User, h.owner_id)
        return UserType(id=u.id, email=u.email, is_active=u.is_active)

    @strawberry.field
    def garages(self, info) -> List[GarageType]:
        session: Session = info.context["session"]
        garages = session.exec(select(Garage).where(Garage.house_id == self.id)).all()
        return [GarageType(id=g.id, title=g.title) for g in garages]


@strawberry.type
class UserType:
    id: int
    email: str
    is_active: bool

    @strawberry.field
    def houses(self, info) -> List[HouseType]:
        session: Session = info.context["session"]
        houses = session.exec(select(House).where(House.owner_id == self.id)).all()
        return [HouseType(id=h.id, title=h.title) for h in houses]

    @strawberry.field
    def garages(self, info) -> List[GarageType]:
        session: Session = info.context["session"]
        garages = session.exec(select(Garage).where(Garage.owner_id == self.id)).all()
        return [GarageType(id=g.id, title=g.title) for g in garages]

    @strawberry.field
    def cars(self, info) -> List[CarType]:
        session: Session = info.context["session"]
        cars = session.exec(select(Car).where(Car.owner_id == self.id)).all()
        return [CarType(id=c.id, model=c.model) for c in cars]

    @strawberry.field
    def driver_license(self, info) -> Optional[DriverLicenceType]:
        session: Session = info.context["session"]
        dl = session.exec(select(DriverLicence).where(DriverLicence.user_id == self.id)).first()
        if not dl:
            return None
        return DriverLicenceType(id=dl.id, number=dl.number)


# -----------------------
# Query & Mutation
# -----------------------
@strawberry.type
class Query:
    @strawberry.field
    def all_users(self, info) -> List[UserType]:
        session: Session = info.context["session"]
        users = session.exec(select(User)).all()
        return [UserType(id=u.id, email=u.email, is_active=u.is_active) for u in users]

    @strawberry.field
    def user(self, info, id: int) -> Optional[UserType]:
        session: Session = info.context["session"]
        u = session.get(User, id)
        if not u:
            return None
        return UserType(id=u.id, email=u.email, is_active=u.is_active)

    @strawberry.field
    def all_houses(self, info) -> List[HouseType]:
        session: Session = info.context["session"]
        hs = session.exec(select(House)).all()
        return [HouseType(id=h.id, title=h.title) for h in hs]

    @strawberry.field
    def all_garages(self, info) -> List[GarageType]:
        session: Session = info.context["session"]
        gs = session.exec(select(Garage)).all()
        return [GarageType(id=g.id, title=g.title) for g in gs]

    @strawberry.field
    def all_cars(self, info) -> List[CarType]:
        session: Session = info.context["session"]
        cs = session.exec(select(Car)).all()
        return [CarType(id=c.id, model=c.model) for c in cs]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, info, email: str, is_active: bool = True) -> UserType:
        session: Session = info.context["session"]
        u = User(email=email, is_active=is_active)
        session.add(u)
        session.commit()
        session.refresh(u)
        return UserType(id=u.id, email=u.email, is_active=u.is_active)

    @strawberry.mutation
    def create_house(self, info, title: str, owner_id: Optional[int] = None) -> HouseType:
        session: Session = info.context["session"]
        if owner_id and not session.get(User, owner_id):
            raise HTTPException(status_code=404, detail="Owner not found")
        h = House(title=title, owner_id=owner_id)
        session.add(h)
        session.commit()
        session.refresh(h)
        return HouseType(id=h.id, title=h.title)

    @strawberry.mutation
    def create_garage(
        self, info, title: str, owner_id: Optional[int] = None, house_id: Optional[int] = None
    ) -> GarageType:
        session: Session = info.context["session"]
        if owner_id and not session.get(User, owner_id):
            raise HTTPException(status_code=404, detail="Owner not found")
        if house_id and not session.get(House, house_id):
            raise HTTPException(status_code=404, detail="House not found")
        g = Garage(title=title, owner_id=owner_id, house_id=house_id)
        session.add(g)
        session.commit()
        session.refresh(g)
        return GarageType(id=g.id, title=g.title)

    @strawberry.mutation
    def create_car(self, info, model: str, owner_id: Optional[int] = None, garage_id: Optional[int] = None) -> CarType:
        session: Session = info.context["session"]
        if owner_id and not session.get(User, owner_id):
            raise HTTPException(status_code=404, detail="Owner not found")
        if garage_id and not session.get(Garage, garage_id):
            raise HTTPException(status_code=404, detail="Garage not found")
        c = Car(model=model, owner_id=owner_id, garage_id=garage_id)
        session.add(c)
        session.commit()
        session.refresh(c)
        return CarType(id=c.id, model=c.model)

    @strawberry.mutation
    def create_driver_license(self, info, number: str, user_id: int) -> DriverLicenceType:
        session: Session = info.context["session"]
        if not session.get(User, user_id):
            raise HTTPException(status_code=404, detail="User not found")
        # optionally enforce one-per-user
        existing = session.exec(select(DriverLicence).where(DriverLicence.user_id == user_id)).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already has driver licence")
        dl = DriverLicence(number=number, user_id=user_id)
        session.add(dl)
        session.commit()
        session.refresh(dl)
        return DriverLicenceType(id=dl.id, number=dl.number)

    @strawberry.mutation
    def assign_garage_to_house(self, info, garage_id: int, house_id: Optional[int]) -> GarageType:
        session: Session = info.context["session"]
        g = session.get(Garage, garage_id)
        if not g:
            raise HTTPException(status_code=404, detail="Garage not found")
        if house_id is not None and not session.get(House, house_id):
            raise HTTPException(status_code=404, detail="House not found")
        g.house_id = house_id
        session.add(g)
        session.commit()
        session.refresh(g)
        return GarageType(id=g.id, title=g.title)

    @strawberry.mutation
    def transfer_car(
        self, info, car_id: int, new_owner_id: Optional[int] = None, new_garage_id: Optional[int] = None
    ) -> CarType:
        session: Session = info.context["session"]
        c = session.get(Car, car_id)
        if not c:
            raise HTTPException(status_code=404, detail="Car not found")
        if new_owner_id is not None and not session.get(User, new_owner_id):
            raise HTTPException(status_code=404, detail="New owner not found")
        if new_garage_id is not None and not session.get(Garage, new_garage_id):
            raise HTTPException(status_code=404, detail="Garage not found")
        c.owner_id = new_owner_id
        c.garage_id = new_garage_id
        session.add(c)
        session.commit()
        session.refresh(c)
        return CarType(id=c.id, model=c.model)


# bottom part of same file: schema, router, app, context getter
schema = strawberry.Schema(query=Query, mutation=Mutation)


def get_context(request: Request):
    # create a DB session for the request
    session = Session(engine)
    # NOTE: for production you should ensure session is closed after request
    return {"session": session}


graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")


# initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()
