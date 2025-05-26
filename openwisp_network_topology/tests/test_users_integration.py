from openwisp_users.tests.test_admin import TestBasicUsersIntegration


class TestUsersIntegration(TestBasicUsersIntegration):
    """
    tests integration with openwisp_users
    """

    is_integration_test = True

    _notifications_params = {
        "notificationsetting_set-TOTAL_FORMS": 0,
        "notificationsetting_set-INITIAL_FORMS": 0,
        "notificationsetting_set-MIN_NUM_FORMS": 0,
        "notificationsetting_set-MAX_NUM_FORMS": 0,
    }

    def _get_org_edit_form_inline_params(self, user, org):
        params = super()._get_org_edit_form_inline_params(user, org)
        params.update(self._notifications_params)
        return params

    def _get_user_edit_form_inline_params(self, user, org):
        params = super()._get_user_edit_form_inline_params(user, org)
        params.update(self._notifications_params)
        return params


del TestBasicUsersIntegration
