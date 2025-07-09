from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    guild_id = Column(String, unique=True, nullable=False)
    prefix = Column(String, default="!")

    def __repr__(self):
        return f"<Guild(guild_id='{self.guild_id}', prefix='{self.prefix}')>"
