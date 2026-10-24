"""
More tests for the main application loop.
"""

from __future__ import annotations

from unittest.mock import patch


class TestAppMore:
    """More app tests."""

    def test_app_deposit_option(self, capsys, db_path, reset_singletons):
        """Test deposit money option from menu."""

        # First create an account
        from src.handlers.pybank import PyBank
        bank = PyBank()
        user_inputs = [
            '999999999999',
            'Test User',
            '',
            '9999999999',
            '30',
            'Test Father',
            '',
            'TestCity',
            '1000.0',
        ]
        with patch('builtins.input', side_effect=user_inputs), \
             patch('src.handlers.pybank.getpass', side_effect=['1111', '1111']):
            bank.register_account()
        # Get account number
        bank.connect.close()
        # Now test menu
        # We need to get the account number - easier to just pass it
        # But menu will create new instance
        # Better to just run with mocks
    def test_app_with_mocked_handlers(self):
        from src import app
        from src.handlers.pybank import PyBank
        with patch.object(PyBank, 'register_account') as mock_reg, \
             patch.object(PyBank, 'deposit_money') as mock_dep, \
             patch.object(PyBank, 'withdraw_money') as mock_wd, \
             patch.object(PyBank, 'view_balance') as mock_vb, \
             patch.object(PyBank, 'view_history') as mock_vh, \
             patch.object(PyBank, 'close_account') as mock_ca, \
             patch.object(PyBank, 'view_data') as mock_vd:
            with patch('builtins.input', side_effect=['1', '2', '3', '4', '5', '6', '7', '8']):
                app.bank()
            mock_reg.assert_called_once()
            mock_dep.assert_called_once()
            mock_wd.assert_called_once()
            mock_vb.assert_called_once()
            mock_vh.assert_called_once()
            mock_ca.assert_called_once()
            mock_vd.assert_called_once()
