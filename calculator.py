from decimal import Decimal
from typing import List, Dict
from dataclasses import dataclass
from models import Transaction, AnalysisConfig, TransactionType


@dataclass
class AnalysisResult:
    """Results of the Source and Application analysis"""
    total_sources: Decimal
    total_applications: Decimal
    illicit_enrichment: Decimal
    
    # Breakdowns
    sources_by_type: Dict[str, Decimal]
    applications_by_type: Dict[str, Decimal]
    
    # Risk flags
    unexplainable_cash_deposits: Decimal
    unexplained_cash_withdrawals: Decimal  # Withdrawn but not proven spent
    investigation_gaps: List[str]
    
    @property
    def is_complete(self) -> bool:
        """If illicit_enrichment is negative, investigation has gaps"""
        return self.illicit_enrichment >= 0
    
    @property
    def risk_level(self) -> str:
        """Assess risk based on enrichment amount and gaps"""
        if not self.is_complete:
            return "INCOMPLETE_INVESTIGATION"
        if self.illicit_enrichment > 0:
            if self.illicit_enrichment > self.total_sources * Decimal("0.5"):
                return "HIGH_CONFIDENCE_ILLEGAL"
            return "MODERATE_CONFIDENCE_ILLEGAL"
        return "NO_ILLEGAL_ACTIVITY"


class SourceApplicationCalculator:
    """Core calculator implementing the formula"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.transactions: List[Transaction] = []
    
    def add_transaction(self, tx: Transaction):
        """Add a transaction to the analysis"""
        # Validate transaction is within period (except starting/ending balances)
        if tx.type not in {
            TransactionType.STARTING_BALANCE,
            TransactionType.ENDING_BALANCE
        }:
            if not (self.config.period_start <= tx.date <= self.config.period_end):
                raise ValueError(
                    f"Transaction date {tx.date} outside period "
                    f"{self.config.period_start} to {self.config.period_end}"
                )
        
        # Validate spousal transactions
        if tx.is_spousal and not self.config.include_spousal:
            raise ValueError("Spousal transaction but include_spousal is False")
        
        self.transactions.append(tx)
    
    def calculate(self) -> AnalysisResult:
        """Execute the Source and Application formula"""
        
        # Categorize transactions
        sources = [tx for tx in self.transactions if tx.is_source()]
        applications = [tx for tx in self.transactions if tx.is_application()]
        cash_movements = [tx for tx in self.transactions if tx.is_cash_movement()]
        
        # Calculate totals
        total_sources = sum(tx.amount for tx in sources)
        total_applications = sum(tx.amount for tx in applications)
        
        # Calculate illicit enrichment: Applications - Sources
        illicit_enrichment = total_applications - total_sources
        
        # Build breakdowns
        sources_by_type = {}
        for tx in sources:
            key = tx.type.value
            sources_by_type[key] = sources_by_type.get(key, Decimal("0")) + tx.amount
        
        applications_by_type = {}
        for tx in applications:
            key = tx.type.value
            applications_by_type[key] = applications_by_type.get(key, Decimal("0")) + tx.amount
        
        # Cash analysis
        cash_deposits = sum(
            tx.amount for tx in cash_movements 
            if tx.type == TransactionType.CASH_DEPOSIT
        )
        cash_withdrawals = sum(
            tx.amount for tx in cash_movements 
            if tx.type == TransactionType.CASH_WITHDRAWAL
        )
        
        # Identify gaps
        gaps = []
        if illicit_enrichment < 0:
            gaps.append(
                f"Unexplained spending/income gap of {abs(illicit_enrichment)}. "
                f"Possible missing: cash expenditures, undiscovered sources, or timing errors."
            )
        
        # Unexplained cash withdrawals (withdrawn but not proven spent)
        proven_cash_spending = sum(
            tx.amount for tx in applications 
            if tx.type == TransactionType.CASH_SEIZED
        )
        unexplained_cash = cash_withdrawals - proven_cash_spending
        
        return AnalysisResult(
            total_sources=total_sources,
            total_applications=total_applications,
            illicit_enrichment=illicit_enrichment,
            sources_by_type=sources_by_type,
            applications_by_type=applications_by_type,
            unexplainable_cash_deposits=cash_deposits,
            unexplained_cash_withdrawals=unexplained_cash,
            investigation_gaps=gaps
        )