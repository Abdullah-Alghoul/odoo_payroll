# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp.tests import common


class TestHrFiscalyear(common.TransactionCase):
    def setUp(self):
        super(TestHrFiscalyear, self).setUp()
        self.user_model = self.env["res.users"]
        self.company_model = self.env['res.company']
        self.payslip_model = self.env["hr.payslip"]
        self.run_model = self.env['hr.payslip.run']
        self.fy_model = self.env['hr.fiscalyear']
        self.period_model = self.env['hr.period']

        self.company_id = self.company_model.create({
            'name': 'Company 1',
            'currency_id': self.env.ref('base.CAD').id,
        })

        self.today = datetime.now().date()

        self.vals = {
            'company_id': self.company_id.id,
            'date_start': '2015-01-01',
            'date_stop': '2015-12-31',
            'schedule_pay': 'monthly',
            'payment_day': '2',
            'payment_weekday': '0',
            'payment_week': '1',
            'name': 'Test',
        }

    def create_fiscal_year(self, vals=None):
        if vals is None:
            vals = {}

        self.vals.update(vals)
        return self.fy_model.create(self.vals)

    def get_periods(self, fiscal_year):
        return fiscal_year.period_ids.sorted(key=lambda p: p.date_start)

    def check_period(self, period, date_start, date_stop, date_payment):
        if date_start:
            self.assertEqual(period.date_start, date_start)
        if date_stop:
            self.assertEqual(period.date_stop, date_stop)
        if date_payment:
            self.assertEqual(period.date_payment, date_payment)

    def test_create_periods_monthly(self):
        fy = self.create_fiscal_year()
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.check_period(periods[0], '2015-01-01', '2015-01-31', '2015-02-02')
        self.check_period(periods[1], '2015-02-01', '2015-02-28', '2015-03-02')
        self.check_period(periods[2], '2015-03-01', '2015-03-31', '2015-04-02')
        self.check_period(
            periods[11], '2015-12-01', '2015-12-31', '2016-01-02')

    def test_create_periods_monthly_custom_year(self):
        fy = self.create_fiscal_year({
            'date_start': '2015-03-16',
            'date_stop': '2016-03-15',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.check_period(periods[0], '2015-03-16', '2015-04-15', '2015-04-17')
        self.check_period(periods[1], '2015-04-16', '2015-05-15', '2015-05-17')
        self.check_period(periods[2], '2015-05-16', '2015-06-15', '2015-06-17')
        self.check_period(
            periods[11], '2016-02-16', '2016-03-15', '2016-03-17')

    def test_create_periods_semi_monthly(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'semi-monthly',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 24)
        self.check_period(periods[0], '2015-01-01', '2015-01-15', '2015-01-17')
        self.check_period(periods[1], '2015-01-16', '2015-01-31', '2015-02-02')
        self.check_period(periods[2], '2015-02-01', '2015-02-15', '2015-02-17')
        self.check_period(periods[3], '2015-02-16', '2015-02-28', '2015-03-02')
        self.check_period(
            periods[23], '2015-12-16', '2015-12-31', '2016-01-02')

    def test_create_periods_semi_monthly_custom_year(self):
        fy = self.create_fiscal_year({
            'date_start': '2015-03-20',
            'date_stop': '2016-03-19',
            'schedule_pay': 'semi-monthly',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 24)
        self.check_period(periods[0], '2015-03-20', '2015-04-03', '2015-04-05')
        self.check_period(periods[1], '2015-04-04', '2015-04-19', '2015-04-21')
        self.check_period(periods[2], '2015-04-20', '2015-05-04', '2015-05-06')
        self.check_period(
            periods[22], '2016-02-20', '2016-03-05', '2016-03-07')
        self.check_period(
            periods[23], '2016-03-06', '2016-03-19', '2016-03-21')

    def test_create_periods_annually(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'annually',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 1)
        self.check_period(periods[0], '2015-01-01', '2015-12-31', '2016-01-02')

    def test_create_periods_annually_custom_year(self):
        fy = self.create_fiscal_year({
            'date_start': '2015-03-16',
            'date_stop': '2016-03-15',
            'schedule_pay': 'annually',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 1)
        self.check_period(periods[0], '2015-03-16', '2016-03-15', '2016-03-17')

    def test_create_periods_weekly(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'weekly',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 52)
        self.check_period(periods[0], '2015-01-01', '2015-01-07', '2015-01-11')
        self.check_period(periods[1], '2015-01-08', '2015-01-14', '2015-01-18')
        self.check_period(periods[2], '2015-01-15', '2015-01-21', '2015-01-25')
        self.check_period(
            periods[51], '2015-12-24', '2015-12-30', '2016-01-03')

    def test_create_periods_weekly_payment_same_week(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'weekly',
            'payment_week': '0',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 52)
        self.assertEqual(periods[0].date_payment, '2015-01-04')
        self.assertEqual(periods[1].date_payment, '2015-01-11')
        self.assertEqual(periods[2].date_payment, '2015-01-18')
        self.assertEqual(periods[51].date_payment, '2015-12-27')

    def test_create_periods_weekly_payment_2_weeks(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'weekly',
            'payment_week': '2',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 52)
        self.assertEqual(periods[0].date_payment, '2015-01-18')
        self.assertEqual(periods[1].date_payment, '2015-01-25')
        self.assertEqual(periods[2].date_payment, '2015-02-01')
        self.assertEqual(periods[51].date_payment, '2016-01-10')

    def test_create_periods_monthly_payment_fifth_day(self):
        fy = self.create_fiscal_year({
            'payment_day': '5',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.assertEqual(periods[0].date_payment, '2015-02-05')
        self.assertEqual(periods[1].date_payment, '2015-03-05')
        self.assertEqual(periods[2].date_payment, '2015-04-05')
        self.assertEqual(periods[11].date_payment, '2016-01-05')

    def test_create_periods_monthly_payment_last_day(self):
        fy = self.create_fiscal_year({
            'payment_day': '0',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.assertEqual(periods[0].date_payment, '2015-01-31')
        self.assertEqual(periods[1].date_payment, '2015-02-28')
        self.assertEqual(periods[2].date_payment, '2015-03-31')
        self.assertEqual(periods[11].date_payment, '2015-12-31')

    def test_create_periods_semi_monthly_payment_fifth_day(self):
        fy = self.create_fiscal_year({
            'payment_day': '5',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.assertEqual(periods[0].date_payment, '2015-02-05')
        self.assertEqual(periods[1].date_payment, '2015-03-05')
        self.assertEqual(periods[2].date_payment, '2015-04-05')
        self.assertEqual(periods[11].date_payment, '2016-01-05')

    def test_create_periods_semi_monthly_payment_last_day(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'semi-monthly',
            'payment_day': '0',
            'date_start': '2015-03-20',
            'date_stop': '2016-03-19',
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 24)
        self.assertEqual(periods[0].date_payment, '2015-04-03')
        self.assertEqual(periods[1].date_payment, '2015-04-19')
        self.assertEqual(periods[2].date_payment, '2015-05-04')
        self.assertEqual(periods[22].date_payment, '2016-03-05')
        self.assertEqual(periods[23].date_payment, '2016-03-19')
