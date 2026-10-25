"""
Additional tests for PyBank to improve coverage.
"""

from __future__ import annotations

from unittest.mock import patch


class TestPyBankMoreCoverage:
    """More coverage tests."""

    def test_view_data_inactive_account(self, bank, capsys, db_path, reset_singletons):
        """Test view_data for inactive account."""
        user_inputs = [
            '888888888888',
            'Inactive User',
            '',
            '8888888888',
            '30',
            'Father',
            '',
            'City',
            '100.0',
        ]
        with patch('builtins.input', side_effect=user_inputs), \
             patch('src.handlers.pybank.getpass', side_effect=['1111', '1111']):
            bank.register_account()
        captured = capsys.readouterr()
        import re
        m = re.search(r'Account Number is: (\d+)', captured.out)
        acc = m.group(1) if m else '500100'
        # Close it
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='1111'):
            bank.close_account()
        # Try to view
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='1111'):
            bank.view_data()
        captured2 = capsys.readouterr()
        assert 'closed' in captured2.out.lower() or 'inactive' in captured2.out.lower()

    def test_view_history_inactive_account(self, bank, capsys):
        """Test view_history for inactive account."""
        user_inputs = [
            '777777777777',
            'Inactive User2',
            '',
            '7777777777',
            '30',
            'Father',
            '',
            'City',
            '100.0',
        ]
        with patch('builtins.input', side_effect=user_inputs), \
             patch('src.handlers.pybank.getpass', side_effect=['2222', '2222']):
            bank.register_account()
        captured = capsys.readouterr()
        import re
        m = re.search(r'Account Number is: (\d+)', captured.out)
        acc = m.group(1) if m else '500101'
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='2222'):
            bank.close_account()
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='2222'):
            bank.view_history()
        captured2 = capsys.readouterr()
        assert 'inactive' in captured2.out.lower() or 'closed' in captured2.out.lower()

    def test_close_account_already_closed(self, bank, capsys):
        """Test closing already closed account."""
        user_inputs = [
            '666666666666',
            'Closed User',
            '',
            '6666666666',
            '30',
            'Father',
            '',
            'City',
            '100.0',
        ]
        with patch('builtins.input', side_effect=user_inputs), \
             patch('src.handlers.pybank.getpass', side_effect=['3333', '3333']):
            bank.register_account()
        captured = capsys.readouterr()
        import re
        m = re.search(r'Account Number is: (\d+)', captured.out)
        acc = m.group(1) if m else '500102'
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='3333'):
            bank.close_account()
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='3333'):
            bank.close_account()
        captured2 = capsys.readouterr()
        assert 'already' in captured2.out.lower()

    def test_deposit_inactive_account(self, bank, capsys):
        """Test deposit into inactive account."""
        user_inputs = [
            '555555555555',
            'Inactive Dep',
            '',
            '5555555555',
            '30',
            'Father',
            '',
            'City',
            '100.0',
        ]
        with patch('builtins.input', side_effect=user_inputs), \
             patch('src.handlers.pybank.getpass', side_effect=['4444', '4444']):
            bank.register_account()
        captured = capsys.readouterr()
        import re
        m = re.search(r'Account Number is: (\d+)', captured.out)
        acc = m.group(1) if m else '500103'
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='4444'):
            bank.close_account()
        with patch('builtins.input', side_effect=[acc, '50']):
            bank.deposit_money()
        captured2 = capsys.readouterr()
        assert 'inactive' in captured2.out.lower()

    def test_withdraw_inactive_account(self, bank, capsys):
        """Test withdraw from inactive account."""
        user_inputs = [
            '444444444444',
            'Inactive Wd',
            '',
            '4444444444',
            '30',
            'Father',
            '',
            'City',
            '100.0',
        ]
        with patch('builtins.input', side_effect=user_inputs), \
             patch('src.handlers.pybank.getpass', side_effect=['5555', '5555']):
            bank.register_account()
        captured = capsys.readouterr()
        import re
        m = re.search(r'Account Number is: (\d+)', captured.out)
        acc = m.group(1) if m else '500104'
        with patch('builtins.input', return_value=acc), \
             patch('src.handlers.pybank.getpass', return_value='5555'):
            bank.close_account()
        with patch('builtins.input', side_effect=[acc, '10']), \
             patch('src.handlers.pybank.getpass', return_value='5555'):
            bank.withdraw_money()
        captured2 = capsys.readouterr()
        assert 'inactive' in captured2.out.lower()
