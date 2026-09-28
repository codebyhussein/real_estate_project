
import io
import base64
import xlsxwriter
from datetime import datetime
from odoo import models, fields
from odoo.exceptions import ValidationError


class MaintenanceReportWizard(models.TransientModel):
    _name = 'maintenance.report.wizard'
    _description = 'Maintenance Report Wizard'

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=fields.Date.today,
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.today,
    )
    issue_type = fields.Selection(
        [
            ('plumbing', 'Plumbing'),
            ('electrical', 'Electrical'),
            ('air_condition', 'Air Condition'),
            ('appliance', 'Appliance'),
            ('other', 'Other'),
        ],
        string='Issue Type',
    )
    urgency = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('emergency', 'Emergency'),
        ],
        string='Urgency',
    )
    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
    )
    excel_file = fields.Binary(
        string='Excel File',
        readonly=True,
    )
    excel_filename = fields.Char(
        string='Filename',
        readonly=True,
    )

    # =========================================================
    # Main Action
    # =========================================================

    def action_generate_report(self):
        self.ensure_one()
        self._validate_dates()
        maintenance_requests = self._get_maintenance_requests()
        output = self._generate_excel_report(maintenance_requests)
        self.excel_file = base64.b64encode(output)
        self.excel_filename = self._get_filename()
        return self._return_wizard()

    # =========================================================
    # Validation
    # =========================================================

    def _validate_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError(
                'Date From cannot be greater than Date To.'
            )

    # =========================================================
    # Maintenance Requests
    # =========================================================

    def _get_report_domain(self):
        date_from = datetime.combine(
            self.date_from,
            datetime.min.time(),
        )
        date_to = datetime.combine(
            fields.Date.add(self.date_to, days=1),
            datetime.min.time(),
        )
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<', date_to),
        ]

        if self.issue_type:
            domain.append(
                ('issue_type', '=', self.issue_type)
            )

        if self.urgency:
            domain.append(
                ('urgency', '=', self.urgency)
            )

        if self.property_id:
            domain.append(
                ('property_id', '=', self.property_id.id)
            )

        return domain

    def _get_maintenance_requests(self):
        return self.env['maintenance.request'].search(
            self._get_report_domain(),
            order='create_date desc, id desc',
        )

    # =========================================================
    # Excel Report
    # =========================================================

    def _generate_excel_report(self, maintenance_requests):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(
            output,
            {'in_memory': True},
        )
        worksheet = workbook.add_worksheet('Maintenance Report')
        formats = self._create_formats(workbook)
        self._configure_worksheet(worksheet)
        row = 0

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        worksheet.merge_range(
            row,
            0,
            row,
            10,
            (
                'Maintenance Requests Report | '
                f'{self.date_from} to {self.date_to}'
            ),
            formats['title'],
        )
        worksheet.set_row(row, 32)
        row += 2

        # -----------------------------------------------------
        # Filters
        # -----------------------------------------------------

        row = self._write_filters(
            worksheet,
            row,
            formats,
        )
        row += 1

        # -----------------------------------------------------
        # Maintenance Requests
        # -----------------------------------------------------

        row, header_row, total_cost = self._write_requests_table(
            worksheet,
            row,
            maintenance_requests,
            formats,
        )

        # -----------------------------------------------------
        # Total Cost
        # -----------------------------------------------------

        row = self._write_total_cost(
            worksheet,
            row,
            total_cost,
            formats,
        )
        row += 3

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        row = self._write_summary(
            worksheet,
            row,
            maintenance_requests,
            total_cost,
            formats,
        )

        # -----------------------------------------------------
        # Issue Type Summary
        # -----------------------------------------------------

        row = self._write_issue_summary(
            worksheet,
            row,
            maintenance_requests,
            formats,
        )

        # -----------------------------------------------------
        # Header & Footer
        # -----------------------------------------------------

        self._configure_header_footer(
            worksheet,
            row,
        )
        workbook.close()
        output.seek(0)
        return output.read()

    # =========================================================
    # Excel Formats
    # =========================================================

    def _create_formats(self, workbook):
        PRIMARY = '#5B8DEF'
        LIGHT_BLUE = '#EEF4FF'
        LIGHT_GRAY = '#F7F7F7'
        BORDER = '#D9D9D9'
        TEXT = '#333333'
        MUTED = '#777777'

        currency = self.env.company.currency_id
        currency_symbol = (
            currency.symbol or ''
        ).replace('"', '""')

        if currency_symbol and currency.position == 'after':
            currency_num_format = (
                f'#,##0.00 "{currency_symbol}";'
                f'[Red]-#,##0.00 "{currency_symbol}"'
            )
        elif currency_symbol:
            currency_num_format = (
                f'"{currency_symbol}" #,##0.00;'
                f'[Red]-"{currency_symbol}" #,##0.00'
            )
        else:
            currency_num_format = '#,##0.00;[Red]-#,##0.00'

        border = {
            'border': 1,
            'border_color': BORDER,
        }

        return {
            'title': workbook.add_format({
                'bold': True,
                'font_size': 16,
                'font_color': TEXT,
                'bg_color': LIGHT_BLUE,
                'align': 'center',
                'valign': 'vcenter',
                **border,
            }),
            'section': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'font_color': PRIMARY,
                'bg_color': LIGHT_BLUE,
                'align': 'center',
                'valign': 'vcenter',
                **border,
            }),
            'header': workbook.add_format({
                'bold': True,
                'font_color': TEXT,
                'bg_color': LIGHT_GRAY,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                **border,
            }),
            'data': workbook.add_format({
                'font_color': TEXT,
                'valign': 'vcenter',
                **border,
            }),
            'center': workbook.add_format({
                'font_color': TEXT,
                'align': 'center',
                'valign': 'vcenter',
                **border,
            }),
            'label': workbook.add_format({
                'bold': True,
                'font_color': TEXT,
                'bg_color': LIGHT_GRAY,
                'valign': 'vcenter',
                **border,
            }),
            'currency': workbook.add_format({
                'font_color': TEXT,
                'align': 'right',
                'valign': 'vcenter',
                'num_format': currency_num_format,
                **border,
            }),
            'date': workbook.add_format({
                'font_color': TEXT,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': 'yyyy-mm-dd',
                **border,
            }),
            'note': workbook.add_format({
                'italic': True,
                'font_color': MUTED,
                'align': 'center',
                'valign': 'vcenter',
                **border,
            }),
            'total_label': workbook.add_format({
                'bold': True,
                'font_color': TEXT,
                'bg_color': LIGHT_GRAY,
                'align': 'left',
                'valign': 'vcenter',
                **border,
            }),
            'total': workbook.add_format({
                'bold': True,
                'font_color': TEXT,
                'bg_color': LIGHT_GRAY,
                'align': 'left',
                'valign': 'vcenter',
                'num_format': currency_num_format,
                **border,
            }),
            'completed': workbook.add_format({
                'bold': True,
                'font_color': '#2E7D32',
                'bg_color': '#E8F5E9',
                'align': 'center',
                'valign': 'vcenter',
                **border,
            }),
            'pending': workbook.add_format({
                'bold': True,
                'font_color': '#F57C00',
                'bg_color': '#FFF3E0',
                'align': 'center',
                'valign': 'vcenter',
                **border,
            }),
            'cancelled': workbook.add_format({
                'bold': True,
                'font_color': '#C62828',
                'bg_color': '#FFEBEE',
                'align': 'center',
                'valign': 'vcenter',
                **border,
            }),
            'integer': workbook.add_format({
                'font_color': TEXT,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0',
                **border,
            }),
        }

    # =========================================================
    # Worksheet Configuration
    # =========================================================

    def _configure_worksheet(self, worksheet):
        column_widths = [
            18, 24, 22, 18, 14, 22,
            15, 18, 18, 16, 14,
        ]

        for col, width in enumerate(column_widths):
            worksheet.set_column(col, col, width)

        worksheet.set_default_row(20)
        worksheet.hide_gridlines(2)
        worksheet.freeze_panes(3, 0)
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_margins(
            left=0.3,
            right=0.3,
            top=0.5,
            bottom=0.5,
        )

    # =========================================================
    # Filters
    # =========================================================

    def _write_filters(self, worksheet, row, formats):
        worksheet.merge_range(
            row,
            0,
            row,
            10,
            'REPORT FILTERS',
            formats['section'],
        )
        row += 1

        issue_type_label = (
            dict(self._fields['issue_type'].selection).get(
                self.issue_type,
                'All',
            )
            if self.issue_type
            else 'All'
        )

        urgency_label = (
            dict(self._fields['urgency'].selection).get(
                self.urgency,
                'All',
            )
            if self.urgency
            else 'All'
        )

        filters = [
            ('Issue Type', issue_type_label),
            ('Urgency', urgency_label),
            (
                'Property',
                self.property_id.name
                if self.property_id
                else 'All',
            ),
        ]

        for label, value in filters:
            worksheet.write(
                row,
                0,
                label,
                formats['label'],
            )
            worksheet.merge_range(
                row,
                1,
                row,
                10,
                value,
                formats['data'],
            )
            row += 1

        return row

    # =========================================================
    # Requests Table
    # =========================================================

    def _write_requests_table(
        self,
        worksheet,
        row,
        maintenance_requests,
        formats,
    ):
        worksheet.merge_range(
            row,
            0,
            row,
            10,
            'MAINTENANCE REQUESTS',
            formats['section'],
        )
        row += 1

        headers = [
            'Reference',
            'Property',
            'Tenant',
            'Issue Type',
            'Urgency',
            'Assigned To',
            'Preferred Date',
            'Scheduled Date',
            'Completion Date',
            'Actual Cost',
            'Status',
        ]

        header_row = row

        for col, header in enumerate(headers):
            worksheet.write(
                row,
                col,
                header,
                formats['header'],
            )

        worksheet.set_row(row, 30)
        row += 1

        issue_type_selection = dict(
            self.env['maintenance.request']
            ._fields['issue_type']
            .selection
        )
        urgency_selection = dict(
            self.env['maintenance.request']
            ._fields['urgency']
            .selection
        )
        state_selection = dict(
            self.env['maintenance.request']
            ._fields['state']
            .selection
        )

        total_cost = 0.0

        for maintenance in maintenance_requests:
            issue_label = issue_type_selection.get(
                maintenance.issue_type,
                '',
            )
            urgency_label = urgency_selection.get(
                maintenance.urgency,
                '',
            )
            state_label = state_selection.get(
                maintenance.state,
                '',
            )

            values = [
                maintenance.name or '',
                maintenance.property_id.name or '',
                maintenance.tenant_id.name or '',
                issue_label,
                urgency_label,
                maintenance.assigned_to.name or '',
                maintenance.preferred_date,
                maintenance.scheduled_date,
                maintenance.completion_date,
                maintenance.actual_cost or 0.0,
                state_label,
            ]

            for col, value in enumerate(values):
                if col in (6, 7, 8):
                    cell_format = formats['date']

                    if value:
                        worksheet.write(
                            row,
                            col,
                            value,
                            cell_format,
                        )
                    else:
                        worksheet.write_blank(
                            row,
                            col,
                            None,
                            cell_format,
                        )

                elif col == 9:
                    worksheet.write(
                        row,
                        col,
                        value,
                        formats['currency'],
                    )

                elif col == 10:
                    if maintenance.state == 'completed':
                        cell_format = formats['completed']
                    elif maintenance.state == 'cancelled':
                        cell_format = formats['cancelled']
                    else:
                        cell_format = formats['pending']

                    worksheet.write(
                        row,
                        col,
                        value,
                        cell_format,
                    )

                elif col in (3, 4):
                    worksheet.write(
                        row,
                        col,
                        value,
                        formats['center'],
                    )
                else:
                    worksheet.write(
                        row,
                        col,
                        value,
                        formats['data'],
                    )

            total_cost += maintenance.actual_cost or 0.0
            row += 1

        if not maintenance_requests:
            worksheet.merge_range(
                row,
                0,
                row,
                10,
                'No maintenance requests found.',
                formats['note'],
            )
            row += 1
        else:
            worksheet.add_table(
                header_row,
                0,
                row - 1,
                10,
                {
                    'style': 'Table Style Medium 2',
                    'columns': [
                        {'header': header}
                        for header in headers
                    ],
                },
            )

        return row, header_row, total_cost

    # =========================================================
    # Total Cost
    # =========================================================

    def _write_total_cost(
        self,
        worksheet,
        row,
        total_cost,
        formats,
    ):
        worksheet.merge_range(
            row,
            8,
            row,
            9,
            'TOTAL COST',
            formats['total_label'],
        )
        worksheet.write(
            row,
            10,
            total_cost,
            formats['total'],
        )
        return row + 1

    # =========================================================
    # Summary
    # =========================================================

    def _write_summary(
        self,
        worksheet,
        row,
        maintenance_requests,
        total_cost,
        formats,
    ):
        worksheet.merge_range(
            row,
            0,
            row,
            10,
            'SUMMARY',
            formats['section'],
        )
        row += 1

        total_requests = len(maintenance_requests)
        completed_requests = 0

        for request in maintenance_requests:
            if request.state == 'completed':
                completed_requests += 1

        pending_requests = total_requests - completed_requests

        summary = [
            ('Total Requests', total_requests, False),
            ('Completed', completed_requests, False),
            ('Pending', pending_requests, False),
            ('Total Actual Cost', total_cost, True),
        ]

        for label, value, is_currency in summary:
            worksheet.write(
                row,
                0,
                label,
                formats['label'],
            )

            cell_format = (
                formats['currency']
                if is_currency
                else formats['integer']
            )

            worksheet.merge_range(
                row,
                1,
                row,
                2,
                value,
                cell_format,
            )
            row += 1

        return row + 1

    # =========================================================
    # Issue Type Summary
    # =========================================================

    def _write_issue_summary(
        self,
        worksheet,
        row,
        maintenance_requests,
        formats,
    ):
        worksheet.merge_range(
            row,
            0,
            row,
            10,
            'ISSUE TYPE SUMMARY',
            formats['section'],
        )
        row += 1

        headers = [
            'Issue Type',
            'Requests',
            'Total Actual Cost',
        ]

        for col, header in enumerate(headers):
            worksheet.write(
                row,
                col,
                header,
                formats['header'],
            )

        row += 1

        issue_type_selection = dict(
            self.env['maintenance.request']
            ._fields['issue_type']
            .selection
        )

        issue_type_totals = {
            issue_type: {
                'count': 0,
                'cost': 0.0,
            }
            for issue_type in issue_type_selection
        }

        for maintenance in maintenance_requests:
            totals = issue_type_totals.get(
                maintenance.issue_type
            )

            if totals is not None:
                totals['count'] += 1
                totals['cost'] += (
                    maintenance.actual_cost or 0.0
                )

        for issue_type, issue_label in issue_type_selection.items():
            totals = issue_type_totals[issue_type]

            worksheet.write(
                row,
                0,
                issue_label,
                formats['data'],
            )
            worksheet.write(
                row,
                1,
                totals['count'],
                formats['integer'],
            )
            worksheet.write(
                row,
                2,
                totals['cost'],
                formats['currency'],
            )
            row += 1

        return row

    # =========================================================
    # Header & Footer
    # =========================================================

    def _configure_header_footer(self, worksheet, row):
        worksheet.set_header(
            '&LReal Estate'
            '&CMaintenance Report'
            f'&R{self.date_from} - {self.date_to}'
        )
        worksheet.set_footer(
            '&LConfidential&RPage &P of &N'
        )
        worksheet.print_area(
            0,
            0,
            row - 1,
            10,
        )

    # =========================================================
    # Filename
    # =========================================================

    def _get_filename(self):
        return (
            f'Maintenance_Report_'
            f'{self.date_from}_'
            f'{self.date_to}.xlsx'
        )

    # =========================================================
    # Return Wizard
    # =========================================================

    def _return_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [
                (False, 'form'),
            ],
            'target': 'new',
        }
 