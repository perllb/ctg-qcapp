from . import db
from flask_login import UserMixin


# class User(UserMixin,db.Model):
#     id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     name = db.Column(db.String(1000))
class User(db.Model,UserMixin):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )
    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )
    password = db.Column(db.String(100))


class CTGdata(db.Model):

    __tablename__ = 'ctgdatadb'
    projid = db.Column(db.Integer, primary_key=True)
    runfolder = db.Column(
        db.String(80),
        nullable=False,
        primary_key=True
    )
    status = db.Column(
        db.String(280),
        nullable=True,
    )
    bnfdude = db.Column(
        db.String(80),
        nullable=True,
    )
    lsens4 = db.Column(
        db.String(80),
        nullable=True,
    )
    workfolder = db.Column(
        db.String(80),
        nullable=True,
    )
    customerpi = db.Column(
        db.String(80),
        nullable=True,
    )
    customer2 = db.Column(
        db.String(80),
        nullable=True,
    )
    lfs603user = db.Column(
        db.String(80),
        nullable=True,
    )
    deliverycontact = db.Column(
        db.String(80),
        nullable=True,
    )
    datatype = db.Column(
        db.String(80),
        nullable=True,
    )
    library = db.Column(
        db.String(80),
        nullable=True,
    )
    ctgbnf = db.Column(
        db.String(80),
        nullable=True,
    )
    delivered = db.Column(
        db.String(80),
        nullable=True,
    )
    qclogged = db.Column(
        db.String(80),
        nullable=True,
    )
    ctginterop = db.Column(
        db.String(80),
        nullable=True,
    )
    ctgsavsave = db.Column(
        db.String(80),
        nullable=True,
    )
    deliveryrep = db.Column(
        db.String(80),
        nullable=True,
    )
    comment = db.Column(
        db.String(80),
        nullable=True,
    )
    created = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=False
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


def init_db():
    db.create_all()


if __name__ == '__main__':
    init_db()
