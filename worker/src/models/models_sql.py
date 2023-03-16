from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class MessageTag(Base):
    __tablename__ = "notification_messagetag"

    id = Column(Text, primary_key=True, index=True)
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    tag = Column(String(255), nullable=False)


class NotificationType(Base):
    __tablename__ = "notification_type"

    id = Column(Text, primary_key=True, index=True)
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    title = Column(String(255), nullable=False)


class NotificationGroup(Base):
    __tablename__ = "notification_group"

    id = Column(Text, primary_key=True, index=True)
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    title = Column(String(255), nullable=False)
    notification_type_id = Column(
        ForeignKey("notification_type.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )

    notification_type = relationship("NotificationType")


class NotificationTypeTag(Base):
    __tablename__ = "notification_typetag"

    id = Column(Text, primary_key=True, index=True)
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    notification_type_id = Column(
        ForeignKey("notification_type.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )
    tag_id = Column(
        ForeignKey("notification_messagetag.id", deferrable=True, initially="DEFERRED"), nullable=False, index=True
    )

    notification_type = relationship("NotificationType")
    tag = relationship("MessageTag")


class NotificationUnsubscribeUser(Base):
    __tablename__ = "notification_unsubscribe_user"
    __table_args__ = {"extend_existing": True}

    id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('notification_unsubscribe_user_id_seq'::regclass)"),
    )
    user_id = Column(UUID, nullable=False)
    notification_type_id = Column(
        ForeignKey("notification_type.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )

    notification_type = relationship("NotificationType")


class Template(Base):
    __tablename__ = "notification_template"
    __table_args__ = {"extend_existing": True}

    id = Column(Text, primary_key=True, index=True)
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    code = Column(Text, nullable=False)
    notification_type_id = Column(
        ForeignKey("notification_type.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )

    notification_type = relationship("NotificationType")


class Context(Base):
    __tablename__ = "notification_context"

    id = Column(Text, primary_key=True, index=True)
    params = Column(JSONB(astext_type=Text()), nullable=False)
    template_id = Column(
        ForeignKey("notification_template.id", deferrable=True, initially="DEFERRED"), nullable=False, index=True
    )

    template = relationship("Template")


class NotificationGroupUser(Base):
    __tablename__ = "notification_groupuser"

    id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('notification_groupuser_id_seq'::regclass)"),
    )
    user_id = Column(UUID, nullable=False)
    notification_group_id = Column(
        ForeignKey("notification_group.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )

    notification_group = relationship("NotificationGroup")


class Notification(Base):
    __tablename__ = "notification_notification"

    id = Column(Text, primary_key=True, index=True)
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    send_status = Column(String(50), nullable=False)
    send_date = Column(DateTime(True), nullable=False)
    context_id = Column(
        ForeignKey("notification_context.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )

    context = relationship("Context")
