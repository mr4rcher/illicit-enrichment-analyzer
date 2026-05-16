from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class TransactionType(Enum):
    """Types of financial flows"""
    # Known Lawful Sources (Income)
    SALARY = "salary"
    INHERITANCE = "inheritance"
    LOAN_RECEIVED = "loan_received"
    GIFT_RECEIVED = "gift_received"
    BUSINESS_INCOME = "business_income"
    STARTING_BALANCE = "starting_balance"  # Savings from before period
    
    # Applications (Expenditures/Savings)
    PURCHASE_ASSET = "purchase_asset"
    LOAN_REPAYMENT = "loan_repayment"
    RENT_PAYMENT = "rent_payment"
    UTILITY_PAYMENT = "utility_payment"
    ENDING_BALANCE = "ending_balance"  # Savings accumulated
    CASH_SEIZED = "cash_seized"
    GIFT_GIVEN = "gift_given"
    CHARITABLE_DONATION = "charitable_donation"
    
    # Neutral (Cash movements)
    CASH_WITHDRAWAL = "cash_withdrawal"  # Not an application until spent
    CASH_DEPOSIT = "cash_deposit"  # Suspicious if source unknown


@dataclass
class Transaction:
    """A single financial transaction"""
    date: date
    amount: Decimal
    currency: str
    type: TransactionType
    description: str
    evidence_reference: str  # e.g., "Bank_Statement_Jan_2024.pdf"
    notes: str = ""
    is_spousal: bool = False  # For joint finances
    
    def is_source(self) -> bool:
        """Is this a known lawful source of income?"""
        return self.type in {
            TransactionType.SALARY,
            TransactionType.INHERITANCE,
            TransactionType.LOAN_RECEIVED,
            TransactionType.GIFT_RECEIVED,
            TransactionType.BUSINESS_INCOME,
            TransactionType.STARTING_BALANCE,
        }
    
    def is_application(self) -> bool:
        """Is this an application of funds?"""
        return self.type in {
            TransactionType.PURCHASE_ASSET,
            TransactionType.LOAN_REPAYMENT,
            TransactionType.RENT_PAYMENT,
            TransactionType.UTILITY_PAYMENT,
            TransactionType.ENDING_BALANCE,
            TransactionType.CASH_SEIZED,
            TransactionType.GIFT_GIVEN,
            TransactionType.CHARITABLE_DONATION,
        }
    
    def is_cash_movement(self) -> bool:
        """Is this a cash deposit or withdrawal (neutral)?"""
        return self.type in {
            TransactionType.CASH_WITHDRAWAL,
            TransactionType.CASH_DEPOSIT,
        }


@dataclass
class AnalysisConfig:
    """Configuration for the analysis"""
    subject_name: str
    period_start: date
    period_end: date
    include_spousal: bool = True
    spouse_name: str = ""
    currency: str = "USD"
    
    def validate(self):
        if self.period_end <= self.period_start:
            raise ValueError("Period end must be after period start")
