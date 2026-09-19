import smtplib
from app.models.order import OrderOrm
from app.tasks.email_tasks import send_order_email

class FakeSMTP:

    last_msg=None
    
    def __init__(self,*args,**kwargs):
        pass

    def ehlo(self):
        pass

    def send_message(self,msg):
        FakeSMTP.last_msg=msg

    def __enter__(self):
        return self

    def __exit__(self,*args):
        return False



def test_send_order_email_ok(db,order,monkeypatch):
    monkeypatch.setattr('app.tasks.email_tasks.SessionLocal', lambda:db)
    monkeypatch.setattr(smtplib,'SMTP',FakeSMTP)
    res=send_order_email(order['id'])
    assert res=='ok'
    assert FakeSMTP.last_msg['To']=='user@mail.com'



def test_send_order_email_order_not_found(db,monkeypatch):
    FakeSMTP.last_msg=None
    monkeypatch.setattr(smtplib,'SMTP',FakeSMTP)
    res=send_order_email(9999)
    assert res=='order_not_found'
    assert FakeSMTP.last_msg is None




def test_send_order_email_user_not_found(db,monkeypatch):
    FakeSMTP.last_msg=None
    monkeypatch.setattr('app.tasks.email_tasks.SessionLocal', lambda:db)
    monkeypatch.setattr(smtplib,'SMTP',FakeSMTP)

    order = OrderOrm(user_id=999999,status="pending",total_price=100)
    db.add(order)
    db.commit()
    db.refresh(order)

    res=send_order_email(order.id)
    
    assert res=='user_not_found'
    assert FakeSMTP.last_msg is None