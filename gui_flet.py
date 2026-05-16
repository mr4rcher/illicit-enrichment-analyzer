#!/usr/bin/env python3
"""
Illicit Enrichment Analyzer - GUI
Built with Flet (Flutter-based)
"""

import flet as ft
from decimal import Decimal
from datetime import date

from models import Transaction, TransactionType, AnalysisConfig
from calculator import SourceApplicationCalculator, AnalysisResult


def create_maria_chen_demo_data():
    """Create the demo case for display"""
    config = AnalysisConfig(
        subject_name="Maria Chen",
        period_start=date(2023, 1, 1),
        period_end=date(2023, 12, 31),
        include_spousal=False,
        currency="USD"
    )
    
    calc = SourceApplicationCalculator(config)
    
    # Sources
    calc.add_transaction(Transaction(
        date=date(2023, 1, 1), amount=Decimal("25000"),
        currency="USD", type=TransactionType.STARTING_BALANCE,
        description="Opening balance", evidence_reference="Chase_Stmt_Dec2022.pdf"
    ))
    
    for month in range(1, 13):
        calc.add_transaction(Transaction(
            date=date(2023, month, 15), amount=Decimal("7500"),
            currency="USD", type=TransactionType.SALARY,
            description=f"Monthly salary {month}/2023", evidence_reference="Payroll_2023.xlsx"
        ))
    
    calc.add_transaction(Transaction(
        date=date(2023, 3, 15), amount=Decimal("12000"),
        currency="USD", type=TransactionType.INHERITANCE,
        description="Aunt Margaret estate", evidence_reference="Probate_Court_0847.pdf"
    ))
    
    calc.add_transaction(Transaction(
        date=date(2023, 5, 1), amount=Decimal("15000"),
        currency="USD", type=TransactionType.LOAN_RECEIVED,
        description="Credit Union loan", evidence_reference="Loan_Agreement_CUP-4451.pdf"
    ))
    
    # Applications
    calc.add_transaction(Transaction(
        date=date(2023, 4, 10), amount=Decimal("65000"),
        currency="USD", type=TransactionType.PURCHASE_ASSET,
        description="Sea Ray boat purchase", evidence_reference="Marina_Purchase_Agreement.pdf"
    ))
    
    calc.add_transaction(Transaction(
        date=date(2023, 7, 20), amount=Decimal("28000"),
        currency="USD", type=TransactionType.PURCHASE_ASSET,
        description="Monte Carlo trip", evidence_reference="Amex_July2023.pdf"
    ))
    
    calc.add_transaction(Transaction(
        date=date(2023, 9, 5), amount=Decimal("35000"),
        currency="USD", type=TransactionType.PURCHASE_ASSET,
        description="Investment condo down payment", evidence_reference="RE_Purchase_45OceanView.pdf"
    ))
    
    calc.add_transaction(Transaction(
        date=date(2023, 11, 30), amount=Decimal("5000"),
        currency="USD", type=TransactionType.LOAN_REPAYMENT,
        description="Loan repayment", evidence_reference="CUP_Loan_Nov2023.pdf"
    ))
    
    calc.add_transaction(Transaction(
        date=date(2023, 12, 15), amount=Decimal("8000"),
        currency="USD", type=TransactionType.CHARITABLE_DONATION,
        description="Youth Sailing Program", evidence_reference="Charitable_Receipt_2023.pdf"
    ))
    
    calc.add_transaction(Transaction(
        date=date(2023, 12, 31), amount=Decimal("42000"),
        currency="USD", type=TransactionType.ENDING_BALANCE,
        description="Ending bank balances", evidence_reference="Chase_Dec2023.pdf"
    ))
    
    # Suspicious cash
    calc.add_transaction(Transaction(
        date=date(2023, 6, 15), amount=Decimal("15000"),
        currency="USD", type=TransactionType.CASH_DEPOSIT,
        description="Unexplained ATM cash deposit", evidence_reference="Chase_June2023.pdf",
        notes="Source declined"
    ))
    
    return calc.calculate(), config


def main(page: ft.Page):
    page.title = "Illicit Enrichment Analyzer"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # State
    current_result = None
    config = None
    
    # UI Elements that need updating
    enrichment_value = ft.Text("$0.00", size=48, weight=ft.FontWeight.BOLD)
    status_text = ft.Text("Ready", color=ft.Colors.GREY_400)
    sources_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Source Type", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Amount", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
    )
    applications_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Application Type", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Amount", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
    )
    
    def run_analysis(e):
        nonlocal current_result, config
        current_result, config = create_maria_chen_demo_data()
        
        # Update enrichment display
        enrichment_amount = current_result.illicit_enrichment
        enrichment_value.value = f"${enrichment_amount:,.2f}"
        
        if enrichment_amount > 0:
            enrichment_value.color = ft.Colors.RED_400
            status_text.value = "⚠️ UNKNOWN OR UNLAWFUL SOURCES"
            status_text.color = ft.Colors.RED_400
        else:
            enrichment_value.color = ft.Colors.GREEN_400
            status_text.value = "✓ No illegal enrichment detected"
            status_text.color = ft.Colors.GREEN_400
        
        # Update sources table
        sources_table.rows.clear()
        for type_key, amount in sorted(current_result.sources_by_type.items()):
            sources_table.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(type_key.replace("_", " ").title())),
                    ft.DataCell(ft.Text(f"${amount:,.2f}")),
                ]
            ))
        # Add total row
        sources_table.rows.append(ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("TOTAL", weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(f"${current_result.total_sources:,.2f}", 
                                  color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)),
            ]
        ))
        
        # Update applications table
        applications_table.rows.clear()
        for type_key, amount in sorted(current_result.applications_by_type.items()):
            applications_table.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(type_key.replace("_", " ").title())),
                    ft.DataCell(ft.Text(f"${amount:,.2f}")),
                ]
            ))
        # Add total row
        applications_table.rows.append(ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("TOTAL", weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(f"${current_result.total_applications:,.2f}", 
                                  color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD)),
            ]
        ))
        
        page.update()
    
    # Layout
    page.add(
        # Header
        ft.Text("SOURCE & APPLICATION ANALYSIS", 
                size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
        ft.Text("Illicit Enrichment Detection System", 
                size=14, color=ft.Colors.GREY_400),
        ft.Divider(),
        
        # Control bar
        ft.Row([
            ft.ElevatedButton(
                "📁 Load Case File",
                icon=ft.Icons.FILE_UPLOAD,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
            ),
            ft.ElevatedButton(
                "▶ Run Analysis",
                icon=ft.Icons.PLAY_ARROW,
                on_click=run_analysis,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
                    bgcolor={ft.ControlState.DEFAULT: ft.Colors.GREEN_700}
                )
            ),
            ft.ElevatedButton(
                "📊 Export Report",
                icon=ft.Icons.TEXT_SNIPPET,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
            ),
        ], spacing=10),
        
        ft.Divider(),
        
        # Results panel
        ft.Row([
            # Left: Summary card
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("ANALYSIS RESULTS", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                        ft.Divider(),
                        ft.Text("Subject: Maria Chen", size=12),
                        ft.Text("Period: 2023-01-01 to 2023-12-31", size=12),
                        ft.Divider(),
                        ft.Text("ILLICIT ENRICHMENT:", size=14, color=ft.Colors.RED_300),
                        enrichment_value,
                        status_text,
                    ], tight=True),
                    padding=20,
                    width=350,
                ),
                elevation=5,
            ),
            
            # Right: Visualization
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Sources vs Applications Comparison", 
                                size=14, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Column([
                                ft.Text("Known Sources", color=ft.Colors.GREEN_400, size=12),
                                ft.Container(
                                    content=ft.Text("$142,000", weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.GREEN_900,
                                    padding=10,
                                    border_radius=5,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.GREY_500),
                            ft.Column([
                                ft.Text("Applications", color=ft.Colors.RED_400, size=12),
                                ft.Container(
                                    content=ft.Text("$183,000", weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.RED_900,
                                    padding=10,
                                    border_radius=5,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Icon(ft.Icons.REMOVE, color=ft.Colors.GREY_500),
                            ft.Column([
                                ft.Text("Discrepancy", color=ft.Colors.AMBER_400, size=12),
                                ft.Container(
                                    content=ft.Text("$41,000", weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.AMBER_900,
                                    padding=10,
                                    border_radius=5,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=20),
                    ]),
                    padding=20,
                    width=700,
                ),
                elevation=5,
            ),
        ], spacing=20, alignment=ft.CrossAxisAlignment.START),
        
        ft.Divider(),
        
        # Tables section
        ft.Row([
            # Sources table
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("KNOWN LAWFUL SOURCES", 
                                size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                        ft.Divider(),
                        ft.Container(content=sources_table, padding=10),
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=15,
                    width=550,
                    height=400,
                ),
                elevation=3,
            ),
            
            # Applications table
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("APPLICATIONS (Expenditures + Savings)", 
                                size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                        ft.Divider(),
                        ft.Container(content=applications_table, padding=10),
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=15,
                    width=550,
                    height=400,
                ),
                elevation=3,
            ),
        ], spacing=20),
    )
    
    # Auto-run on startup
    run_analysis(None)


if __name__ == "__main__":
    ft.app(target=main)