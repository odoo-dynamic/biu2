import logging
import threading
import time
import psycopg2
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}

class IrCron(models.Model):
    _inherit = 'ir.cron'

    # check_nextcall = fields.Boolean(default=True)
    # check_nextcall = fields.Boolean(default=False, compute= "check_nextcall")

    # @api.depends('nextcall')
    # def check_nextcall(self):
    #     for record in self:
    #         if record.name == 'Onetime Dispose Assets Scheduler':
    #             if record.nextcall.hour == 0:
    #                 record.nextcall.hour = 9

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):
        """ Run a given job taking care of the repetition.

        :param job_cr: cursor to use to execute the job, safe to commit/rollback
        :param job: job to be run (as a dictionary).
        :param cron_cr: cursor holding lock on the cron job row, to use to update the next exec date,
            must not be committed/rolled back!
        """
        with api.Environment.manage():
            try:
                cron = api.Environment(job_cr, job['user_id'], {
                    'lastcall': fields.Datetime.from_string(job['lastcall'])
                })[cls._name]
                # Use the user's timezone to compare and compute datetimes,
                # otherwise unexpected results may appear. For instance, adding
                # 1 month in UTC to July 1st at midnight in GMT+2 gives July 30
                # instead of August 1st!
                now = fields.Datetime.context_timestamp(cron, datetime.now())
                nextcall = fields.Datetime.context_timestamp(cron, fields.Datetime.from_string(job['nextcall']))
                numbercall = job['numbercall']

                ok = False
                while nextcall < now and numbercall:
                    if numbercall > 0:
                        numbercall -= 1
                    if not ok or job['doall']:
                        cron._callback(job['cron_name'], job['ir_actions_server_id'], job['id'])
                    if numbercall:
                        nextcall += _intervalTypes[job['interval_type']](job['interval_number'])
                        if job['cron_name'] == 'Onetime Dispose Assets Scheduler':
                            if nextcall.hour == 8:
                                nextcall += _intervalTypes['hours'](9)
                    ok = True
                addsql = ''
                if not numbercall:
                    addsql = ', active=False'
                cron_cr.execute("UPDATE ir_cron SET nextcall=%s, numbercall=%s, lastcall=%s"+addsql+" WHERE id=%s",(
                    fields.Datetime.to_string(nextcall.astimezone(pytz.UTC)),
                    numbercall,
                    fields.Datetime.to_string(now.astimezone(pytz.UTC)),
                    job['id']
                ))
                cron.flush()
                cron.invalidate_cache()

            finally:
                job_cr.commit()
                cron_cr.commit()
    