"""
More tests for the main application loop.
"""

from __future__ import annotations

from unittest.mock import patch


class TestAppMore:
    """More app tests."""

    def test_app_deposit_option(self, capsys, db_path, reset_singletons):
        """Test deposit money option from menu end to end."""
        import re

        from src.handlers.pybank import PyBank

        # First create an account
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
        captured = capsys.readouterr()
        m = re.search(r'Account Number is: (\d+)', captured.out)
        acc = m.group(1)
        bank.connect.close()

        # Deposit via the menu, then exit
        from src import app
        with patch('builtins.input', side_effect=['2', acc, '500.0', '8']):
            app.bank()
        captured2 = capsys.readouterr()
        assert 'DEPOSIT TRANSACTION SUCCESSFUL' in captured2.out
