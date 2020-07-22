from flask.cli import FlaskGroup
from client import app, db

cli = FlaskGroup(app)

@cli.command()
def recreate_db():
	db.drop_all()
	db.create_all()
	db.session.commit()

# @cli.command()
# def seed_db():
	
if __name__ == "__main__":
	cli()