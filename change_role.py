
from datetime import datetime, timedelta

from app import db, models

query_id = 1

query = db.session.query(models.User).filter(models.User.id == query_id)
user = query.first()

if user:
    user.role = 1

user.created_date = datetime.utcnow() - timedelta(hours=720)

db.session.commit()

