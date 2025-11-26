import aiohttp
import asyncio
import time
import re
import logging
from typing import Optional, Union, Dict, Any, Coroutine

from .exceptions import (
    InvalidClientError,
    BadRequestError,
    ServerError,
    OTPError,
    InvalidPhoneNumberError,
    UserNotFoundError,
    InsufficientBalanceError,
    RateLimitExceededError,
    UnexpectedResponseError,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OTP:

    def __init__(
        self,
        username: str,
        password: str,
        url: str = "https://safir.bale.ai"
    ) -> None:
        self.client_id = username
        self.client_secret = password
        self.base_url = url.rstrip("/")
        self.token: Optional[str] = None
        self.expires_at: float = 0.0

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        digits = re.sub(r"[^\d]", "", phone.strip())

        if digits.startswith("0") and len(digits) == 11:
            return "98" + digits[1:]
        elif len(digits) == 10:
            return "98" + digits

        return digits

    async def _post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, **kwargs) as response:
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    text = await response.text()
                    raise UnexpectedResponseError(f"Non-JSON response: {text}")

                if 200 <= response.status < 300:
                    return data

                if endpoint.endswith("/auth/token"):
                    if response.status == 401:
                        raise InvalidClientError(data)
                    if response.status == 400:
                        raise BadRequestError(data)
                    if response.status >= 500:
                        raise ServerError(data)

                error_code = data.get("code")
                error_message = data.get("message", "")

                if response.status == 400:
                    if error_code == 8:
                        raise InvalidPhoneNumberError(error_message)
                    if error_code == 18:
                        raise RateLimitExceededError(error_message)
                    if error_code == 20:
                        raise InsufficientBalanceError(error_message)
                    raise OTPError(error_message)

                if response.status == 402:
                    raise InsufficientBalanceError(error_message)
                if response.status == 404:
                    raise UserNotFoundError(error_message)
                if response.status >= 500:
                    raise ServerError(error_message)

                raise UnexpectedResponseError(f"{response.status}: {data}")

    async def _fetch_token(self) -> None:
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "read",
        }

        data = await self._post("/api/v2/auth/token", data=body)
        self.token = data["access_token"]
        expires_in = float(data.get("expires_in", 3600))
        self.expires_at = time.time() + expires_in - 30

    async def _ensure_token(self) -> None:
        if not self.token or time.time() >= self.expires_at:
            await self._fetch_token()

    async def _send_otp(self, phone_number: str, code: int) -> Dict[str, Any]:
        await self._ensure_token()

        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "phone": self._normalize_phone(phone_number),
            "otp": code
        }

        return await self._post("/api/v2/send_otp", json=payload, headers=headers)

    async def send_otp_async(self, phone_number: str, code: Union[int, str]) -> Dict[str, Any]:
        otp_code = int(code) if isinstance(code, str) else code
        return await self._send_otp(phone_number, otp_code)

    def send_otp(self, phone_number: str, code: Union[int, str]) -> Coroutine[Any, Any, Dict[str, Any]]:
        otp_code = int(code) if isinstance(code, str) else code

        try:
            loop = asyncio.get_running_loop()
            return self._send_otp(phone_number, otp_code)
        except RuntimeError:
            return asyncio.run(self._send_otp(phone_number, otp_code))