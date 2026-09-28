"""
Generates 6 comprehensive, realistic, multi-page legal sample contracts
with realistic clauses, proper formatting, and varied risk profiles.
"""

import os
import fitz  # PyMuPDF

SAMPLE_DIRS = [
    os.path.join(os.path.dirname(__file__), "sample_pdfs"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_contracts_to_upload")
]

for d in SAMPLE_DIRS:
    os.makedirs(d, exist_ok=True)

contracts = [
    {
        "filename": "1_Master_Services_Agreement_Enterprise.pdf",
        "title": "MASTER SERVICES AND CONSULTING AGREEMENT",
        "subtitle": "Enterprise IT Engineering & Cloud Migration Services",
        "parties": "BETWEEN: Apex Global Technologies Inc. (\"Client\") AND Meridian Financial Solutions Ltd. (\"Consultant\")",
        "date": "Effective Date: October 1, 2025",
        "sections": [
            ("1. APPOINTMENT AND SCOPE OF SERVICES", [
                "1.1 Scope of Work. The Consultant shall provide enterprise cloud transformation, database re-architecture, and software development services as specified in Statements of Work ('SOW') executed under this Agreement.",
                "1.2 Performance Standards. All consulting services shall be performed in a professional, workmanlike manner consistent with prevailing enterprise software industry standards and cybersecurity best practices.",
                "1.3 Key Personnel. The Consultant agrees to assign senior software architects with at least eight (8) years of enterprise experience. Replacement of key personnel requires prior written approval from the Client."
            ]),
            ("2. COMPENSATION AND PAYMENT TERMS", [
                "2.1 Service Fees. The Client shall pay the Consultant a fixed monthly retainer of $45,000 for core architecture services, plus pre-approved milestone deliverables specified in each applicable SOW.",
                "2.2 Invoicing and Net 30. Invoices shall be issued at the conclusion of each calendar month. The Client agrees to pay all undisputed invoices within thirty (30) calendar days of receipt.",
                "2.3 Late Payment Interest. Any undisputed invoice balance unpaid after thirty (30) days shall accrue interest at the lesser rate of 1.0% per month or the maximum statutory rate permitted by law.",
                "2.4 Disputed Invoices. In the event of a good-faith billing dispute, the Client must notify Consultant within fifteen (15) days of invoice receipt and pay the undisputed portion in full."
            ]),
            ("3. SERVICE LEVEL AGREEMENT (SLA) & UPTIME GUARANTEE", [
                "3.1 System Availability. The Consultant warrants that the deployed cloud services architecture shall maintain ninety-nine and nine-tenths percent (99.9%) system availability during each measurement month.",
                "3.2 Incident Severity Levels. High-severity incidents causing core system outages shall be responded to within fifteen (15) minutes, with mitigation commenced within one (1) hour of notification.",
                "3.3 Service Credits. If availability falls below 99.5% in any calendar month, Client shall receive a credit equal to fifteen percent (15%) of the applicable monthly service fee applied to the next invoice."
            ]),
            ("4. INTELLECTUAL PROPERTY RIGHTS AND WORK FOR HIRE", [
                "4.1 Client Ownership. All custom software code, database schemas, architectural designs, and deliverables created specifically for Client under this Agreement shall constitute 'Work Made for Hire' and remain the exclusive property of Client.",
                "4.2 Pre-existing IP. Consultant retains all rights in its pre-existing proprietary tools, frameworks, and reusable libraries. Consultant hereby grants Client a perpetual, irrevocable, worldwide license to use such tools as integrated into the deliverables.",
                "4.3 Third-Party Open Source. Consultant shall not introduce any copyleft or viral open-source licenses (e.g., GPL v3) into Client production code without explicit advance written authorization."
            ]),
            ("5. CONFIDENTIALITY AND TRADE SECRET PROTECTION", [
                "5.1 Duty of Confidentiality. Each party agrees to hold all proprietary trade secrets, financial records, algorithms, customer lists, and business strategies of the other party in strict confidence.",
                "5.2 Standard of Care. The receiving party shall employ the same standard of reasonable care used to protect its own sensitive trade secrets, and in no event less than a reasonable commercial standard.",
                "5.3 Survival of Obligations. The confidentiality duties set forth in this Section shall survive termination of this Agreement for five (5) years, and indefinitely with respect to verified trade secrets."
            ]),
            ("6. DATA SECURITY AND REGULATORY COMPLIANCE", [
                "6.1 Security Standards. Consultant shall maintain administrative, physical, and technical safeguards compliant with SOC2 Type II, ISO 27001, and applicable data privacy regulations including GDPR.",
                "6.2 Data Breach Notification. Consultant must notify Client in writing within twenty-four (24) hours of becoming aware of any actual or suspected unauthorized access to Client sensitive data."
            ]),
            ("7. LIMITATION OF LIABILITY", [
                "7.1 Mutual Liability Cap. Except for breaches of confidentiality or gross negligence, neither party's total aggregate liability arising out of this Agreement shall exceed the total fees paid by Client during the preceding twelve (12) months.",
                "7.2 Consequential Damages Exclusion. In no event shall either party be liable to the other for indirect, incidental, punitive, or consequential lost profits arising out of this Agreement."
            ]),
            ("8. INDEMNIFICATION", [
                "8.1 Consultant Indemnity. Consultant shall defend, indemnify, and hold harmless Client against third-party claims alleging that the deliverables infringe any registered patent, copyright, or trademark.",
                "8.2 Client Indemnity. Client shall indemnify Consultant against third-party claims resulting from Client data or specifications provided to Consultant."
            ]),
            ("9. TERM AND TERMINATION", [
                "9.1 Agreement Term. This Agreement shall take effect on October 1, 2025 and continue for an initial term of two (2) years, unless terminated earlier in accordance with this Section.",
                "9.2 Termination for Convenience. Either party may terminate this Agreement without cause by providing sixty (60) days advance written notice to the other party.",
                "9.3 Termination for Cause. Either party may terminate immediately if the other party commits a material breach and fails to cure such breach within thirty (30) days of receiving written notice."
            ]),
            ("10. DISPUTE RESOLUTION AND GOVERNING LAW", [
                "10.1 Governing Law. This Agreement shall be governed by, construed, and enforced in accordance with the laws of the State of New York, without regard to conflicts of law principles.",
                "10.2 Arbitration. Any controversy or dispute arising out of this Agreement shall be settled by binding arbitration administered by the American Arbitration Association (AAA) in New York, NY."
            ])
        ]
    },
    {
        "filename": "2_High_Risk_Vendor_Supply_Contract.pdf",
        "title": "EXCLUSIVE GLOBAL VENDOR SUPPLY & PROCUREMENT AGREEMENT",
        "subtitle": "Warning: High-Risk Asymmetric Commercial Terms",
        "parties": "BETWEEN: Titan Conglomerate Holdings LLC (\"Buyer\") AND Nova Manufacturing Ltd. (\"Vendor\")",
        "date": "Effective Date: November 15, 2025",
        "sections": [
            ("1. EXCLUSIVE SUPPLY OBLIGATIONS & MINIMUM QUOTAS", [
                "1.1 Vendor Exclusivity. The Vendor is exclusively bound to manufacture and supply all electronic component assemblies solely to Buyer. Vendor shall not sell, license, or supply identical or similar products to any competitor or third party.",
                "1.2 Buyer Freedom of Sourcing. The Buyer reserves complete discretion to procure components from alternative manufacturers at any time without notice or minimum purchase commitment.",
                "1.3 Strict Delivery Penalties. Time is strictly of the essence. If Vendor delivers shipments even one (1) day after scheduled date, Vendor shall forfeit twenty-five percent (25%) of total invoice value."
            ]),
            ("2. DELAYED PAYMENT & BUYER WITHHOLDING RIGHTS", [
                "2.1 Extended Payment Terms. Buyer shall issue payment ninety (90) calendar days after physical receipt and inspection of products (Net 90 payment cycle).",
                "2.2 Unilateral Withholding. Buyer reserves the absolute right to withhold payments indefinitely without notice if Buyer determines, in its sole subjective discretion, that product quality is deficient.",
                "2.3 Zero Late Interest. Any deferred or overdue payments by Buyer shall not accrue interest, penalties, or administrative charges of any kind."
            ]),
            ("3. IMMEDIATE UNILATERAL TERMINATION WITHOUT CAUSE", [
                "3.1 Immediate Cancellation. The Buyer may terminate this Agreement immediately at any time, for any reason or no reason, without prior notice and without incurring any liability or termination fees.",
                "3.2 Vendor Termination Restriction. The Vendor may not terminate this Agreement for convenience under any circumstances and must continue fulfillment until all issued purchase orders are satisfied."
            ]),
            ("4. UNLIMITED VENDOR LIABILITY & DAMAGE EXPOSURE", [
                "4.1 Uncapped Vendor Liability. The Vendor assumes full, uncapped, and unlimited liability for any direct, indirect, consequential, punitive, exemplary, or special damages suffered by Buyer.",
                "4.2 Consequential Loss Guarantee. Vendor shall be strictly liable for Buyer lost enterprise market share, factory downtime costs, and commercial profits resulting from any component defect."
            ]),
            ("5. ONE-SIDED INDEMNIFICATION & LIQUIDATED DAMAGES", [
                "5.1 Total Vendor Indemnity. Vendor shall defend, fully indemnify, and hold harmless Buyer and its affiliates against any and all claims, lawsuits, costs, damages, fines, and attorney fees without financial limitation.",
                "5.2 No Reciprocal Indemnification. Buyer shall have zero indemnification or defense obligations toward Vendor under any circumstance.",
                "5.3 Daily Compounding Penalties. For any disputed delivery or defective unit, Vendor agrees to pay liquidated damages of fifteen percent (15%) of the purchase order value compounded daily."
            ]),
            ("6. UNRESTRICTED AUDIT & INTELLECTUAL PROPERTY SURRENDER", [
                "6.1 Intrusive Audit Rights. Buyer representatives may enter Vendor manufacturing premises at any hour without prior notice to inspect proprietary facilities, trade secrets, and financial books.",
                "6.2 IP Forfeiture. All proprietary schematics, tooling, firmware source code, and manufacturing processes utilized by Vendor shall become the sole property of Buyer upon signature of this Agreement."
            ]),
            ("7. GOVERNING LAW AND JURISDICTION", [
                "7.1 Governing Law. This contract shall be governed strictly by the domestic laws of the State of Delaware.",
                "7.2 Submission to Jurisdiction. Vendor submits to the exclusive personal jurisdiction of Delaware state courts, waiving all objections to venue and convenience."
            ])
            # Note: Intentionally OMITTED Dispute Resolution / Arbitration and Force Majeure clauses!
        ]
    },
    {
        "filename": "3_Mutual_Non_Disclosure_Agreement.pdf",
        "title": "MUTUAL NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT",
        "subtitle": "Standard Bilateral Trade Secret & IP Protection Covenant",
        "parties": "BETWEEN: CyberCore Dynamics Inc. (\"Party A\") AND Horizon Ventures LLC (\"Party B\")",
        "date": "Effective Date: January 10, 2026",
        "sections": [
            ("1. PURPOSE AND DEFINITION OF CONFIDENTIAL INFORMATION", [
                "1.1 Business Purpose. The parties desire to explore a mutual strategic technology partnership and investment opportunity (the 'Permitted Purpose').",
                "1.2 Scope of Information. 'Confidential Information' includes all non-public technical data, source code, financial projections, business plans, customer identities, and product roadmaps disclosed by either party.",
                "1.3 Form of Disclosure. Information disclosed in written, graphic, machine-readable, or oral form clearly identified as confidential shall be protected hereunder."
            ]),
            ("2. EXCLUSIONS FROM CONFIDENTIAL OBLIGATIONS", [
                "2.1 Public Domain. Obligations do not apply to information that is or becomes publicly available through no breach or wrongful act of the receiving party.",
                "2.2 Prior Knowledge. Information proven to have been in lawful possession of the receiving party prior to disclosure without confidentiality restrictions is excluded.",
                "2.3 Independent Development. Information independently developed by employees without reference to or reliance upon the disclosing party's Confidential Information is excluded."
            ]),
            ("3. NON-DISCLOSURE AND STANDARD OF REASONABLE CARE", [
                "3.1 Restriction on Use. The receiving party agrees to use Confidential Information solely to evaluate the Permitted Purpose and for no other commercial benefit.",
                "3.2 Need-to-Know Limitation. Disclosure is strictly restricted to employees, legal counsel, and financial advisors who require access and are bound by confidentiality agreements.",
                "3.3 Degree of Care. Each party shall exercise at least the same degree of reasonable care used to safeguard its own confidential materials of like sensitivity."
            ]),
            ("4. TERM, RETURN OF MATERIALS & INJUNCTIVE RELIEF", [
                "4.1 Duration. This Agreement and the confidentiality covenants contained herein shall remain in full force for three (3) years following the Effective Date.",
                "4.2 Certified Destruction. Upon written demand, the receiving party shall within fourteen (14) days return or destroy all physical and digital copies of Confidential Information.",
                "4.3 Equitable Relief. Both parties acknowledge that unauthorized disclosure causes irreparable injury and that the disclosing party is entitled to seek injunctive relief without bond."
            ]),
            ("5. GOVERNING LAW AND ARBITRATION", [
                "5.1 Governing Law. This Agreement shall be construed and interpreted in accordance with the laws of the State of Delaware.",
                "5.2 Dispute Resolution. Any dispute arising out of this Agreement shall be resolved through expedited arbitration before the American Arbitration Association in Wilmington, Delaware."
            ])
        ]
    },
    {
        "filename": "4_Commercial_Real_Estate_Lease_Agreement.pdf",
        "title": "COMMERCIAL OFFICE PROPERTY LEASE AGREEMENT",
        "subtitle": "Class-A Financial District Office Space Tenancy",
        "parties": "BETWEEN: Metro Tower Properties REIT (\"Landlord\") AND Vertex Legal Technologies LLP (\"Tenant\")",
        "date": "Effective Date: December 1, 2025",
        "sections": [
            ("1. LEASED PREMISES AND TERM", [
                "1.1 Leased Premises. Landlord hereby leases to Tenant, and Tenant leases from Landlord, Suite 1400 comprising approximately 8,500 rentable square feet located at 100 Wall Street, New York, NY.",
                "1.2 Term of Tenancy. The initial lease term shall be five (5) years, commencing on January 1, 2026 ('Commencement Date') and expiring December 31, 2030, unless renewed pursuant to Section 1.3.",
                "1.3 Option to Renew. Tenant shall have the option to extend the term for one additional period of three (3) years upon six (6) months prior written notice at Fair Market Value."
            ]),
            ("2. RENT, ESCALATION AND SECURITY DEPOSIT", [
                "2.1 Monthly Base Rent. Tenant shall pay Landlord a monthly base rent of $52,000, payable on the first day of each calendar month in advance via electronic funds transfer.",
                "2.2 Annual Escalation. On each anniversary of the Commencement Date, base rent shall increase by three and one-half percent (3.5%) over the preceding lease year.",
                "2.3 Security Deposit. Upon execution, Tenant shall deposit with Landlord $156,000 (three months rent) as security for full and faithful performance of Tenant's covenants."
            ]),
            ("3. COMMON AREA MAINTENANCE (CAM) & OPERATING EXPENSES", [
                "3.1 Proportionate Share. Tenant shall pay its proportionate share (4.25%) of annual Building Operating Costs, including real estate taxes, building security, janitorial, and HVAC services.",
                "3.2 Utilities. Tenant shall pay directly for its metered electrical consumption and high-speed fiber telecommunication services."
            ]),
            ("4. PERMITTED USE, REPAIRS AND ALTERATIONS", [
                "4.1 Permitted Use. The Premises shall be used exclusively for general executive and professional office purposes and legal software development.",
                "4.2 Maintenance and Repairs. Landlord shall maintain building foundations, exterior walls, and core elevators. Tenant shall keep interior premises in good order and repair.",
                "4.3 Tenant Alterations. Tenant shall not perform structural modifications without prior written approval from Landlord, which approval shall not be unreasonably withheld."
            ]),
            ("5. DEFAULT REMEDIES AND CASUALTY", [
                "5.1 Events of Default. An event of default occurs if Tenant fails to pay rent within ten (10) days after written notice, or fails to cure non-monetary default within thirty (30) days.",
                "5.2 Landlord Remedies. Upon default, Landlord may re-enter the Premises, terminate this Lease, and recover all unpaid rent and consequential re-letting expenses.",
                "5.3 Casualty and Rent Abatement. If premises are rendered untenantable by fire or casualty, rent shall abate proportionately during restoration period."
            ]),
            ("6. GOVERNING LAW AND DISPUTE RESOLUTION", [
                "6.1 Governing Law. This Lease shall be governed and construed in accordance with the substantive laws of the State of New York.",
                "6.2 Waiver of Jury Trial. To the extent permitted by law, Landlord and Tenant waive trial by jury in any action or proceeding arising out of this Lease."
            ])
        ]
    },
    {
        "filename": "5_Software_SaaS_and_Cloud_Services_Agreement.pdf",
        "title": "ENTERPRISE SOFTWARE-AS-A-SERVICE (SaaS) SUBSCRIPTION AGREEMENT",
        "subtitle": "Cloud Platform Infrastructure, HIPAA & Security Specifications",
        "parties": "BETWEEN: CloudVault Systems Inc. (\"Provider\") AND Premier Healthcare Services Corp. (\"Subscriber\")",
        "date": "Effective Date: February 1, 2026",
        "sections": [
            ("1. SUBSCRIPTION GRANT AND AUTHORIZED USERS", [
                "1.1 Service Grant. Provider grants Subscriber a non-exclusive, worldwide, subscription-based right to access and use the CloudVault Enterprise Clinical Suite during the Subscription Term.",
                "1.2 User Seats. The subscription includes five hundred (500) named user seats and five million monthly API transactions. Additional seats may be added under supplemental orders.",
                "1.3 Access Credentials. Subscriber is responsible for maintaining strict confidentiality of user credentials and multi-factor authentication (MFA) enforcement."
            ]),
            ("2. DATA PRIVACY, HIPAA COMPLIANCE & SECURITY", [
                "2.1 Patient Data Protection. Provider acknowledges that Subscriber Data may contain Protected Health Information (PHI) governed by HIPAA and the HITECH Act.",
                "2.2 Business Associate Agreement. Contemporaneously with this Agreement, parties shall execute the Standard HIPAA Business Associate Agreement ('BAA') incorporated herein by reference.",
                "2.3 Data Encryption. Provider warrants all Subscriber Data is encrypted at rest using AES-256 encryption and in transit using TLS 1.3 protocol standards."
            ]),
            ("3. SERVICE LEVEL AGREEMENT (SLA) & UPTIME CREDITS", [
                "3.1 99.95% Availability Guarantee. Provider guarantees the CloudVault production environment shall maintain minimum monthly uptime of 99.95%, excluding scheduled maintenance windows.",
                "3.2 Tiered Downtime Credits. If uptime falls below 99.95%, Subscriber receives 10% credit; below 99.0%, Subscriber receives 25% credit; below 98.0%, Subscriber receives 50% fee credit.",
                "3.3 Chronic Failure Right. If uptime falls below 98.0% in any two consecutive months, Subscriber may terminate this Agreement immediately without penalty and receive a prorated refund."
            ]),
            ("4. SUBSCRIPTION FEES AND BILLING", [
                "4.1 Annual Fee. Subscriber shall pay an annual enterprise subscription fee of $180,000, invoiced annually in advance with Net 30 payment terms.",
                "4.2 Tax Exemption. Fees exclude applicable sales, use, or value-added taxes, which shall be invoiced unless Subscriber provides a valid statutory tax exemption certificate."
            ]),
            ("5. LIMITATION OF LIABILITY & IP INDEMNITY", [
                "5.1 Liability Cap. Provider's total aggregate liability under this Agreement shall not exceed two times (2x) the total annual subscription fee paid by Subscriber.",
                "5.2 IP Infringement Indemnity. Provider shall defend Subscriber against any third-party claim asserting that CloudVault software infringes any patent, copyright, or trade secret."
            ]),
            ("6. TERM, DATA RETRIEVAL AND TERMINATION", [
                "6.1 Subscription Term. Initial term of one (1) year, automatically renewing for successive one-year terms unless either party gives sixty (60) days advance non-renewal notice.",
                "6.2 Post-Termination Data Export. Upon termination, Provider shall maintain Subscriber Data available for secure export in standard format for sixty (60) days without additional charge."
            ]),
            ("7. GOVERNING LAW AND JURISDICTION", [
                "7.1 Governing Law. This Agreement is governed by the laws of the State of California, without regard to conflict of laws principles.",
                "7.2 Jurisdiction. Parties consent to exclusive personal jurisdiction and venue in the state and federal courts located in San Francisco County, California."
            ])
        ]
    },
    {
        "filename": "6_Executive_Employment_and_Restrictive_Covenants.pdf",
        "title": "EXECUTIVE EMPLOYMENT & RESTRICTIVE COVENANTS AGREEMENT",
        "subtitle": "Senior Executive Appointment, Equity Incentive & Non-Compete",
        "parties": "BETWEEN: Sterling Capital Partners LLC (\"Company\") AND Executive Officer (\"Executive\")",
        "date": "Effective Date: March 1, 2026",
        "sections": [
            ("1. POSITION, DUTIES AND RESPONSIBILITIES", [
                "1.1 Executive Role. Company employs Executive as Chief Technology Officer ('CTO'), reporting directly to the Chief Executive Officer and Board of Directors.",
                "1.2 Best Efforts. Executive shall devote full business time, attention, skill, and best efforts to the business and technology operations of the Company.",
                "1.3 Outside Activities. Executive shall not engage in any other business activities or board memberships without the express written consent of the Board."
            ]),
            ("2. COMPENSATION, ANNUAL BONUS & EQUITY INCENTIVES", [
                "2.1 Base Salary. Company shall pay Executive an annual base salary of $325,000, payable in semi-monthly installments in accordance with standard payroll practices.",
                "2.2 Annual Incentive Bonus. Executive shall be eligible for an annual performance bonus with a target of forty percent (40%) of base salary, based on milestones approved by Compensation Committee.",
                "2.3 Long-Term Equity Grant. Executive shall be granted an option to purchase 250,000 Common Units vesting over four (4) years with a one-year cliff."
            ]),
            ("3. TERMINATION OF EMPLOYMENT & SEVERANCE", [
                "3.1 At-Will Employment. Executive's employment is at-will, terminable by either party at any time with or without Cause.",
                "3.2 Termination for Cause. Company may terminate immediately for Cause (fraud, embezzlement, felony conviction, gross willful misconduct). Upon Cause termination, severance is zero.",
                "3.3 Severance Without Cause. If Company terminates Executive without Cause, Executive shall receive twelve (12) months base salary continuation plus subsidized COBRA health benefits for one year."
            ]),
            ("4. RESTRICTIVE COVENANTS: NON-COMPETITION & NON-SOLICITATION", [
                "4.1 Non-Competition. During employment and for twelve (12) months following termination, Executive shall not directly or indirectly manage, advise, or perform services for any competing enterprise.",
                "4.2 Non-Solicitation of Employees. Executive shall not solicit, induce, or hire any employee or contractor of the Company for twelve (12) months post-termination.",
                "4.3 Non-Solicitation of Clients. Executive shall not solicit business from any active client or customer of Company with whom Executive had contact during tenure."
            ]),
            ("5. INVENTIONS ASSIGNMENT AND CONFIDENTIALITY", [
                "5.1 Assignment of Inventions. All patents, algorithms, models, and intellectual property developed by Executive during employment relating to Company business are the exclusive property of Company.",
                "5.2 Confidentiality. Executive shall hold all proprietary trading strategies, client lists, and software systems in strict confidence during and perpetually after employment."
            ]),
            ("6. GOVERNING LAW AND ARBITRATION", [
                "6.1 Governing Law. This Agreement shall be governed by and interpreted under the laws of the State of Delaware.",
                "6.2 Mandatory Arbitration. Any controversy arising out of this Agreement shall be settled by binding arbitration before JAMS in Wilmington, Delaware under its Employment Arbitration Rules."
            ])
        ]
    }
]

def build_pdf(contract_data):
    doc = fitz.open()
    
    # Page setup: Standard US Letter (612 x 792 points)
    page_width, page_height = 612, 792
    margin_x, margin_top, margin_bottom = 54, 54, 54
    printable_width = page_width - (margin_x * 2) # 504 pt
    
    current_page = doc.new_page(width=page_width, height=page_height)
    cursor_y = margin_top
    
    def check_page_break(needed_space):
        nonlocal current_page, cursor_y
        if cursor_y + needed_space > page_height - margin_bottom:
            current_page = doc.new_page(width=page_width, height=page_height)
            cursor_y = margin_top
            # Header on subsequent pages
            current_page.draw_line(
                fitz.Point(margin_x, cursor_y), 
                fitz.Point(page_width - margin_x, cursor_y), 
                color=(0.7, 0.7, 0.7), width=0.5
            )
            current_page.insert_text(
                fitz.Point(margin_x, cursor_y - 8), 
                contract_data["title"][:50] + "...", 
                fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4)
            )
            cursor_y += 18
            return True
        return False

    # Cover Header Banner
    current_page.draw_rect(
        fitz.Rect(margin_x, cursor_y, page_width - margin_x, cursor_y + 65),
        color=(0.15, 0.25, 0.4), fill=(0.94, 0.96, 0.99), width=1
    )
    current_page.insert_text(
        fitz.Point(margin_x + 16, cursor_y + 24),
        contract_data["title"],
        fontsize=13, fontname="hebo", color=(0.1, 0.18, 0.35)
    )
    current_page.insert_text(
        fitz.Point(margin_x + 16, cursor_y + 42),
        contract_data["subtitle"],
        fontsize=10, fontname="helv", color=(0.3, 0.35, 0.45)
    )
    current_page.insert_text(
        fitz.Point(margin_x + 16, cursor_y + 56),
        contract_data["date"],
        fontsize=9, fontname="hebo", color=(0.2, 0.4, 0.6)
    )
    cursor_y += 80

    # Parties block
    parties_rect = fitz.Rect(margin_x, cursor_y, page_width - margin_x, cursor_y + 40)
    current_page.insert_textbox(
        parties_rect,
        contract_data["parties"],
        fontsize=9.5, fontname="helv", color=(0.2, 0.2, 0.2)
    )
    cursor_y += 45

    # Divider line
    current_page.draw_line(
        fitz.Point(margin_x, cursor_y), 
        fitz.Point(page_width - margin_x, cursor_y), 
        color=(0.2, 0.35, 0.55), width=1.5
    )
    cursor_y += 18

    # Render Sections and Clauses
    for sec_title, clauses in contract_data["sections"]:
        check_page_break(50)
        # Section Header
        current_page.draw_rect(
            fitz.Rect(margin_x, cursor_y, page_width - margin_x, cursor_y + 18),
            color=None, fill=(0.90, 0.93, 0.97)
        )
        current_page.insert_text(
            fitz.Point(margin_x + 6, cursor_y + 13),
            sec_title,
            fontsize=10.5, fontname="hebo", color=(0.1, 0.2, 0.4)
        )
        cursor_y += 24

        for clause_text in clauses:
            # Estimate text height
            lines_est = max(1, len(clause_text) // 70) + 1
            clause_height = (lines_est * 13) + 10
            check_page_break(clause_height)

            clause_rect = fitz.Rect(margin_x + 8, cursor_y, page_width - margin_x - 8, cursor_y + clause_height)
            current_page.insert_textbox(
                clause_rect,
                clause_text,
                fontsize=9.5, fontname="helv", color=(0.15, 0.15, 0.15)
            )
            cursor_y += clause_height + 4

        cursor_y += 8

    # Signatures Block
    check_page_break(120)
    cursor_y += 10
    current_page.draw_line(
        fitz.Point(margin_x, cursor_y), 
        fitz.Point(page_width - margin_x, cursor_y), 
        color=(0.7, 0.7, 0.7), width=1
    )
    cursor_y += 14
    current_page.insert_text(
        fitz.Point(margin_x, cursor_y),
        "IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.",
        fontsize=9, fontname="hebi", color=(0.3, 0.3, 0.3)
    )
    cursor_y += 30

    col_w = (printable_width - 40) / 2
    # Left Party
    current_page.draw_line(fitz.Point(margin_x, cursor_y + 25), fitz.Point(margin_x + col_w, cursor_y + 25), color=(0.2, 0.2, 0.2), width=1)
    current_page.insert_text(fitz.Point(margin_x, cursor_y + 38), "Authorized Representative", fontsize=9, fontname="hebo")
    current_page.insert_text(fitz.Point(margin_x, cursor_y + 50), "Date: October 1, 2025", fontsize=8.5, fontname="helv", color=(0.4, 0.4, 0.4))

    # Right Party
    r_start = margin_x + col_w + 40
    current_page.draw_line(fitz.Point(r_start, cursor_y + 25), fitz.Point(r_start + col_w, cursor_y + 25), color=(0.2, 0.2, 0.2), width=1)
    current_page.insert_text(fitz.Point(r_start, cursor_y + 38), "Authorized Representative", fontsize=9, fontname="hebo")
    current_page.insert_text(fitz.Point(r_start, cursor_y + 50), "Date: October 1, 2025", fontsize=8.5, fontname="helv", color=(0.4, 0.4, 0.4))

    # Number pages in footer
    total_pages = len(doc)
    for p_no in range(total_pages):
        page = doc[p_no]
        footer_text = f"Page {p_no + 1} of {total_pages}  •  LexiCore Deterministic Legal Repository"
        page.draw_line(fitz.Point(margin_x, page_height - 35), fitz.Point(page_width - margin_x, page_height - 35), color=(0.85, 0.85, 0.85), width=0.5)
        page.insert_text(fitz.Point(margin_x, page_height - 22), footer_text, fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    # Save to all destination directories
    for d in SAMPLE_DIRS:
        out_path = os.path.join(d, contract_data["filename"])
        doc.save(out_path)
    
    doc.close()
    print(f"Generated: {contract_data['filename']} ({total_pages} pages)")

for c in contracts:
    build_pdf(c)

print("All 6 high-quality multi-page sample legal contracts generated successfully!")
