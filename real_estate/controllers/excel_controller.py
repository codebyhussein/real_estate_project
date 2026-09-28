import io
import xlsxwriter
from odoo import http
from odoo.http import request, content_disposition


class RealEstateController(http.Controller):

    @http.route('/real_estate/property/excel_export/<int:property_id>', type='http', auth='user')
    def property_excel_export(self, property_id, **kwargs):
        property_obj = request.env['real_estate.property'].browse(property_id)

        if not property_obj.exists():
            return request.not_found()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Property Details')

        currency_symbol = request.env.company.currency_id.symbol or ''
        escaped_symbol = currency_symbol.replace('"', '""')
        currency_num_format = f'"{escaped_symbol}" #,##0.00;[Red]-"{escaped_symbol}" #,##0.00'
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#176B6B',
            'font_color': 'white',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D6E2E1',
            'text_wrap': True,
        })
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'font_color': 'white',
            'bg_color': '#123B3A',
            'align': 'left',
            'valign': 'vcenter',
        })
        section_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#176B6B',
            'font_size': 11,
            'valign': 'vcenter',
        })
        label_format = workbook.add_format({
            'bold': True,
            'bg_color': '#EAF1F0',
            'border': 1
        })
        data_format = workbook.add_format({'border': 1, 'border_color': '#D6E2E1'})
        alternate_data_format = workbook.add_format({
            'border': 1,
            'border_color': '#D6E2E1',
            'bg_color': '#F4F8F7',
        })
        currency_format = workbook.add_format({
            'num_format': currency_num_format,
            'border': 1,
            'border_color': '#D6E2E1',
        })
        alternate_currency_format = workbook.add_format({
            'num_format': currency_num_format,
            'border': 1,
            'border_color': '#D6E2E1',
            'bg_color': '#F4F8F7',
        })
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1,
            'border_color': '#D6E2E1',
        })
        alternate_date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1,
            'border_color': '#D6E2E1',
            'bg_color': '#F4F8F7',
        })
        note_format = workbook.add_format({
            'italic': True,
            'font_color': '#667572',
            'border': 1,
            'border_color': '#D6E2E1',
        })

        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 19)
        worksheet.set_column('D:E', 16)
        worksheet.set_column('F:G', 16)
        worksheet.set_column('H:I', 15)
        worksheet.set_column('J:J', 18)
        worksheet.set_default_row(21)
        worksheet.hide_gridlines(2)
        worksheet.freeze_panes(3, 0)
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_margins(0.3, 0.3, 0.5, 0.5)

        row = 0
        worksheet.merge_range(row, 0, row, 9, f'PROPERTY REPORT  |  {property_obj.name}', title_format)
        worksheet.set_row(row, 34) 
        row += 2

        worksheet.merge_range(row, 0, row, 9, 'PROPERTY OVERVIEW', section_format)
        row += 1
        property_data = [
            ('Property Name', property_obj.name),
            ('Property Type', dict(property_obj._fields['property_type'].selection).get(property_obj.property_type, '')),
            ('Status', 'Available' if property_obj.available else 'Occupied'),
            ('Agent', property_obj.agent_id.name or ''),
            ('Bedrooms', property_obj.bedrooms),
        ]
        for label, value in property_data:
            worksheet.write(row, 0, label, label_format)
            worksheet.merge_range(row, 1, row, 9, '' if value is False else value, data_format)
            row += 1

        row += 1

        worksheet.merge_range(row, 0, row, 9, 'PRICING & REVENUE', section_format)
        row += 1
        worksheet.write(row, 0, 'Monthly Rent', label_format)
        worksheet.merge_range(row, 1, row, 9, property_obj.price, currency_format)
        row += 1

        leases = property_obj.lease_ids.sorted(key=lambda lease: str(lease.start_date or ''), reverse=True)
        payments = property_obj.payment_ids.sorted(
            key=lambda payment: (str(payment.due_date or ''), payment.id),
            reverse=True,
        )

        row += 1
        worksheet.merge_range(row, 0, row, 9, 'LEASE HISTORY', section_format)
        row += 1
        lease_headers = ['Lease', 'Tenant', 'Monthly Rent', 'Start Date', 'End Date']
        for col, header in enumerate(lease_headers):
            worksheet.write(row, col, header, header_format)
        worksheet.merge_range(row, 5, row, 9, 'Status', header_format)
        row += 1

        if leases:
            for index, lease in enumerate(leases):
                row_format = alternate_data_format if index % 2 else data_format
                rent_format = alternate_currency_format if index % 2 else currency_format
                date_cell_format = alternate_date_format if index % 2 else date_format
                lease_values = [
                    lease.name or '',
                    lease.tenant_id.name or '',
                    lease.monthly_rent,
                    lease.start_date or '',
                    lease.end_date or '',
                ]
                for col, value in enumerate(lease_values):
                    cell_format = rent_format if col == 2 else date_cell_format if col in (3, 4) else row_format
                    worksheet.write(row, col, value, cell_format)
                worksheet.merge_range(
                    row, 5, row, 9,
                    dict(lease._fields['state'].selection).get(lease.state, ''),
                    row_format,
                )
                row += 1

        else:
            worksheet.merge_range(row, 0, row, 9, 'No leases recorded for this property.', note_format)
            row += 1

        row += 1
        worksheet.merge_range(row, 0, row, 9, 'PROPERTY PAYMENT HISTORY', section_format)
        row += 1

        payment_headers = [
            'Lease', 'Tenant', 'Reference', 'Due Date', 'Payment Date',
            'Method', 'Status', 'Amount Due', 'Late Fee', 'Late Fee Applied',
        ]
        for col, header in enumerate(payment_headers):
            worksheet.write(row, col, header, header_format)
        payment_header_row = row
        row += 1
        if request.env.user.has_group('real_estate.group_property_manager'):
            
            if payments:
                for index, payment in enumerate(payments):
                    row_format = alternate_data_format if index % 2 else data_format
                    date_cell_format = alternate_date_format if index % 2 else date_format
                    currency_cell_format = alternate_currency_format if index % 2 else currency_format
                    payment_values = [
                        payment.lease_id.name or '',
                        payment.tenant_id.name or '',
                        payment.name or '',
                        payment.due_date or '',
                        payment.payment_date or '',
                        dict(payment._fields['payment_method'].selection).get(payment.payment_method, ''),
                        dict(payment._fields['state'].selection).get(payment.state, ''),
                        payment.amount,
                        payment.late_fee or 0.0,
                        'Yes' if payment.late_fee_applied else 'No',
                    ]
                    for col, value in enumerate(payment_values):
                        cell_format = (
                            date_cell_format if col in (3, 4)
                            else currency_cell_format if col in (7, 8)
                            else row_format
                        )
                        worksheet.write(row, col, value, cell_format)
                    row += 1
                worksheet.autofilter(payment_header_row, 0, row - 1, 9)
            else:
                worksheet.merge_range(row, 0, row, 9, 'No payments recorded for this property.', note_format)
                row += 1
        else:
            worksheet.merge_range(row, 0, row, 9, 'You do not have permission to view payment history.', note_format)
            row += 1

        worksheet.set_header('&LReal Estate&CProperty Report&R' + property_obj.name)
        worksheet.set_footer('&LConfidential&RPage &P of &N')
        worksheet.print_area(0, 0, row - 1, 9)
        workbook.close()

        output.seek(0)
        filename = f'Property_{property_obj.name.replace(" ", "_")}.xlsx'

        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )