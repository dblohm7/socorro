# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from configman.dotdict import DotDict
import mock

from socorro.cron.crontabber_app import CronTabberApp
from socorro.external.boto.connection_context import S3ConnectionContext
from socorro.schemas import CRASH_REPORT_JSON_SCHEMA_AS_STRING
from socorro.unittest.cron.jobs.base import IntegrationTestBase


class TestUploadCrashReportJSONSchemaCronApp(IntegrationTestBase):
    job = 'socorro.cron.jobs.upload_crash_report_json_schema.UploadCrashReportJSONSchemaCronApp|30d'

    def _setup_config_manager(self):
        return super(TestUploadCrashReportJSONSchemaCronApp, self)._setup_config_manager(
            jobs_string=self.job,
            extra_value_source=DotDict({
                'resource.boto.resource_class': S3ConnectionContext
            })
        )

    @mock.patch('boto.connect_s3')
    def test_run(self, connect_s3):

        key = mock.MagicMock()
        connect_s3().get_bucket().get_key.return_value = None
        connect_s3().get_bucket().new_key.return_value = key

        with self._setup_config_manager().context() as config:
            tab = CronTabberApp(config)
            tab.run_all()

            information = self._load_structure()
            app_name = 'upload-crash-report-json-schema'
            assert information[app_name]
            assert not information[app_name]['last_error']
            assert information[app_name]['last_success']

        key.set_contents_from_string.assert_called_with(
            CRASH_REPORT_JSON_SCHEMA_AS_STRING
        )
