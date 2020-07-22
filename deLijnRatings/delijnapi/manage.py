from flask.cli import FlaskGroup
from client import app, db, setupDatabaseTables

cli = FlaskGroup(app)

@cli.command()
def recreate_db():
	db.drop_all()
	db.create_all()
	db.session.commit()

@cli.command()
def seed_db():
	setupDatabaseTables()

# @cli.command()
# def seed_db():
# 	db.session.add(User(username="Luuk", email='luukvansloun@live.nl', password='testpass'))
# 	db.session.add(User(username="Henk", email='henk@henk.com', password='passtest'))
# 	db.session.commit()

if __name__ == "__main__":
	cli()