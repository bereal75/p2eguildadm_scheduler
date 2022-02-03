import string
from typing import List, Optional
from unicodedata import decimal

from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class WalletBalanceBase(BaseModel):
    walletbalanceid: int
    walletaddress: str
    tokenname: Optional[str]
    contractaddress: str
    balance: Decimal
    balance_dts: Optional[datetime]