from contextlib import contextmanager

from database import Session


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        print("An error occured: ", e)
        session.rollback()
        raise
    finally:
        session.close()
