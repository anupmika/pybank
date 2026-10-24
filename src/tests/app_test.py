"""
Tests for the main application loop.
"""

from __future__ import annotations

from unittest.mock import patch

from src import app


class TestApp:
    """Test application loop."""

    def test_app_close_on_choice_8(self, capsys):
        """Test app exits when choice 8 is selected."""
        with patch('builtins.input', return_value='8'):
            app.bank()
        captured = capsys.readouterr()
        assert 'Exiting' in captured.out

    def test_app_invalid_choice(self, capsys):
        """Test app handles invalid choice."""
        # First invalid, then exit
        with patch('builtins.input', side_effect=['99', '8']):
            app.bank()
        captured = capsys.readouterr()
        assert 'Invalid Choice' in captured.out

    def test_app_all_menu_options(self, capsys):
        """Test all menu options route to the correct PyBank method."""
        from src.handlers.pybank import PyBank
        with patch.object(PyBank, 'register_account') as mock_reg, \
             patch.object(PyBank, 'deposit_money') as mock_dep, \
             patch.object(PyBank, 'withdraw_money') as mock_wd, \
             patch.object(PyBank, 'view_balance') as mock_vb, \
             patch.object(PyBank, 'view_history') as mock_vh, \
             patch.object(PyBank, 'close_account') as mock_ca, \
             patch.object(PyBank, 'view_data') as mock_vd, \
             patch('builtins.input', side_effect=['1', '2', '3', '4', '5', '6', '7', '8']):
            app.bank()
        mock_reg.assert_called_once()
        mock_dep.assert_called_once()
        mock_wd.assert_called_once()
        mock_vb.assert_called_once()
        mock_vh.assert_called_once()
        mock_ca.assert_called_once()
        mock_vd.assert_called_once()
