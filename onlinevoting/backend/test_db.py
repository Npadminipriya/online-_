from app import db, Election

elections = Election.query.all()
print(elections)