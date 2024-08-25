from sqlmodel import create_engine, SQLModel, Session, select
from functools import wraps
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy import and_, or_, false, true
from . import models
from src import auth
import os

os.environ['MYSQL_URL'] = f'mysql+pymysql://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}:{os.environ['MYSQL_PORT']}/{os.environ['MYSQL_DATABASE']}'
engine = create_engine(os.environ['MYSQL_URL'])

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

def session_decorator(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        with Session(engine) as session:
            try:
                return func(*args, **kargs, session=session)
            except Exception as e:
                session.rollback()
                raise e
    return wrapper


_sqlmodel_filter_map = {
    "=": lambda column,val: column == str(val),
    "<": lambda column, val: column < val,
    "<=": lambda column, val: column <= val,
    ">": lambda column, val: column > val,
    ">=": lambda column, val: column >= val,
    "<>": lambda column, val: column != val,
    "!=": lambda column, val: column != val,
    "like": lambda column, val: column.like(val),
    "in": lambda column, val: column.in_(val)
}
def _init_filter_dict(table_name, filter_dict: dict, logic: str='and'):
    '''
        filter_dict: {
            field_name: [compare_operators, value],
            ...
        }
    '''
    table = getattr(models, table_name)
    filter_schema = []
    or_filter_schema = []
    for key in filter_dict.keys():
        if key in ['and', 'or']:
            if key == 'and':
                filter_schema.append(_init_filter_dict(table_name, filter_dict[key]))
            else:
                or_filter_schema.append(_init_filter_dict(table_name, filter_dict[key], logic='or'))
        else:
            column = getattr(table, key, None)
            filter_item = filter_dict[key]
            if column is None:
                print('key error')
                return
            if isinstance(filter_item, list):
                filter_schema.append(_sqlmodel_filter_map[filter_item[0]](getattr(table, key), filter_item[1]))
            else:
                filter_schema.append(_sqlmodel_filter_map['='](getattr(table, key), filter_item))

    return  and_(true(), *filter_schema) if not or_filter_schema and logic == 'and' \
            else or_(false(), *filter_schema) if not or_filter_schema and logic == 'or' \
            else or_(*or_filter_schema) if not filter_schema \
            else and_(and_(*filter_schema), or_(*or_filter_schema))
        

@session_decorator
def query_one(table_name: str = None, filter_dict: dict = {}, fields: list = [],  session: Session = None):
    table = getattr(models, table_name)
    if not fields:
        query_chain = select(getattr(models, table_name))
    else:
        query_chain = select(*[getattr(table, field, None) for field in fields])
    filter_schema = _init_filter_dict(table_name=table_name, filter_dict=filter_dict) 
    query_chain = query_chain.where(filter_schema).limit(1)
    ret = session.exec(query_chain).first()
    return ret

@session_decorator
def query(table_name: str, filter_dict: dict = {}, fields: list = [], session: Session = None, offset: int = 0, limit: int = 50):
    table = getattr(models, table_name)
    if not fields:
        query_chain = select(getattr(models, table_name))
    else:
        query_chain = select(*[getattr(table, field, None) for field in fields])
    filter_schema = _init_filter_dict(table_name=table_name, filter_dict=filter_dict) 
    query_chain = query_chain.where(filter_schema).offset(offset).limit(limit)
    ret = session.exec(query_chain).all()
    return ret

@session_decorator
def get_user_files(token: str, session: Session = None):
    user_name = auth.get_identity(token)
    statement = select(models.User).where(models.User.available == 1).limit(1)
    ret = session.exec(statement).first().files
    return models.Response(data=ret)
    
@session_decorator
def insert(table_name: str, item: dict, session: Session = None, unique_key: list[str] = []):
    if unique_key and query_one(table_name, {"or": {key: ['=', item.get(key)]} for key in unique_key}):
        return models.Response(detail='重复名称或邮箱', status_code=409)
    else:
        _item = getattr(models, table_name)(**item)
        session.add(_item)
        # commit 后会清除_item对象
        _item = _item.dict()
        session.commit()
        return models.Response(status_code=200, data=_item)
