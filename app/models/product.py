from peewee import CharField, DecimalField, IntegerField, BooleanField, AutoField

from app.database import BaseModel


class Product(BaseModel):
    id = AutoField()
    name = CharField(unique=True)
    category = CharField()
    price = DecimalField(decimal_places=2)
    stock = IntegerField(default=0)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "products"