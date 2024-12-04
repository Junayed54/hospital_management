import time
import base64
from hashlib import sha256
from struct import pack
from django.conf import settings  # Ensure you have Agora credentials set in settings.py

class RtcTokenBuilder:
    @staticmethod
    def buildTokenWithUid(app_id, app_certificate, channel_name, uid, expiration_time, privilege_expired_ts):
        """
        Generate an RTC token for a given channel and user ID (uid).
        
        :param app_id: Agora app id (from the Agora console)
        :param app_certificate: Agora app certificate (from the Agora console)
        :param channel_name: Unique channel name (e.g., appointment ID)
        :param uid: User ID (set to 0 for guests)
        :param expiration_time: Token expiration time in seconds since Unix epoch
        :param privilege_expired_ts: Expiration time of privilege in seconds since Unix epoch
        :return: Token string
        """

        ts = int(time.time())
        # Define token validity period (in seconds)
        expiry = expiration_time

        # Prepare token parameters
        privilege = 0  # The token is for a guest user with UID 0
        channel = channel_name

        # Generate token
        base_str = RtcTokenBuilder._generate_base_string(
            app_id, ts, privilege, channel, uid, expiry
        )
        signature = RtcTokenBuilder._generate_signature(
            app_certificate, base_str
        )

        # Token is a base64-encoded string, concatenated with timestamp and signature
        token = f'{base_str}{signature}'
        return token

    @staticmethod
    def _generate_base_string(app_id, ts, privilege, channel, uid, expiry):
        """
        Generate the base string for token construction.
        
        :param app_id: Agora app id
        :param ts: Timestamp of the token request
        :param privilege: Token privilege type (0 for guest, 1 for host)
        :param channel: Channel name
        :param uid: User ID (0 for guest)
        :param expiry: Token expiration time
        :return: Base string for token construction
        """

        # Create the base string
        base_string = f"{app_id}{channel}{uid}{ts}{expiry}{privilege}"
        return base_string

    @staticmethod
    def _generate_signature(app_certificate, base_string):
        """
        Generate the signature using the app_certificate and the base string.
        
        :param app_certificate: Agora app certificate (private key)
        :param base_string: The base string
        :return: Signature for token
        """
        # Generate SHA-256 hash signature
        hash_object = sha256()
        hash_object.update(base_string.encode("utf-8"))
        signature = base64.b64encode(hash_object.digest()).decode("utf-8")
        
        return signature
