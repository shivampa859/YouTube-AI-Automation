import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from cryptography.fernet import Fernet


load_dotenv()


def get_mongodb_uri():
    """
    Get MongoDB connection URI.

    Streamlit Cloud:
        Read from Streamlit Secrets.

    Local development:
        Read from .env.
    """

    mongodb_uri = None

    # Try Streamlit Secrets first
    try:
        import streamlit as st

        if "MONGODB_URI" in st.secrets:
            mongodb_uri = st.secrets["MONGODB_URI"]

    except Exception:
        pass

    # Fall back to environment variable
    if not mongodb_uri:
        mongodb_uri = os.getenv("MONGODB_URI")

    if not mongodb_uri:
        raise RuntimeError(
            "MONGODB_URI is not configured."
        )

    return mongodb_uri


def get_encryption_key():
    """
    Get the Fernet encryption key.

    Streamlit Cloud:
        Read from Streamlit Secrets.

    Local development:
        Read from .env.
    """

    encryption_key = None

    # Try Streamlit Secrets first
    try:
        import streamlit as st

        if "TOKEN_ENCRYPTION_KEY" in st.secrets:
            encryption_key = st.secrets[
                "TOKEN_ENCRYPTION_KEY"
            ]

    except Exception:
        pass

    # Fall back to environment variable
    if not encryption_key:
        encryption_key = os.getenv(
            "TOKEN_ENCRYPTION_KEY"
        )

    if not encryption_key:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY is not configured."
        )

    return encryption_key.encode()


def encrypt_token(token):
    """
    Encrypt a YouTube refresh token before
    storing it in MongoDB.
    """

    if not token:
        raise ValueError(
            "Refresh token cannot be empty."
        )

    fernet = Fernet(get_encryption_key())

    encrypted_token = fernet.encrypt(
        token.encode()
    )

    return encrypted_token.decode()


def decrypt_token(encrypted_token):
    """
    Decrypt a YouTube refresh token retrieved
    from MongoDB.
    """

    if not encrypted_token:
        raise ValueError(
            "Encrypted token cannot be empty."
        )

    fernet = Fernet(get_encryption_key())

    decrypted_token = fernet.decrypt(
        encrypted_token.encode()
    )

    return decrypted_token.decode()


def get_database():
    """
    Connect to MongoDB Atlas and return the database.
    """

    mongodb_uri = get_mongodb_uri()

    client = MongoClient(
        mongodb_uri,
        serverSelectionTimeoutMS=10000
    )

    # Test the connection
    client.admin.command("ping")

    return client["youtube_automation"]


def save_youtube_connection(
    connection_id,
    channel_id,
    channel_name,
    refresh_token
):
    """
    Save a user's YouTube connection in MongoDB.

    The refresh token is encrypted before storage.
    """

    db = get_database()

    collection = db["youtube_connections"]

    now = datetime.now(timezone.utc)

    encrypted_refresh_token = encrypt_token(
        refresh_token
    )

    connection_data = {
        "connection_id": connection_id,
        "channel_id": channel_id,
        "channel_name": channel_name,
        "refresh_token": encrypted_refresh_token,
        "updated_at": now
    }

    collection.update_one(
        {
            "connection_id": connection_id
        },
        {
            "$set": connection_data,
            "$setOnInsert": {
                "created_at": now
            }
        },
        upsert=True
    )


def get_youtube_connection(connection_id):
    """
    Get a user's YouTube connection from MongoDB.

    The stored refresh token is decrypted before
    being returned.
    """

    db = get_database()

    collection = db["youtube_connections"]

    connection = collection.find_one(
        {
            "connection_id": connection_id
        }
    )

    if not connection:
        return None

    if connection.get("refresh_token"):
        connection["refresh_token"] = decrypt_token(
            connection["refresh_token"]
        )

    return connection


def delete_youtube_connection(connection_id):
    """
    Delete a user's YouTube connection from MongoDB.
    """

    db = get_database()

    collection = db["youtube_connections"]

    collection.delete_one(
        {
            "connection_id": connection_id
        }
    )