"""
Tests for the Pydantic data models in src/validators/models.py.

This module tests validation rules for User, Account, and TransactionRecord
models including field constraints, defaults, aliases, and error handling.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.validators.models import Account, TransactionRecord, User


class TestUserValidation:
    """Test suite for User model validation."""
    
    def test_valid_user_is_accepted(self):
        """Test that valid user data passes validation."""
        user = User(
            aadhar_num='123456789012',
            name='Alice Example',
            email='alice@example.com',
            phone='9876543210',
            age=30,
            fatherName='Bob Example',
            address='123 Main St',
            city='Metropolis',
            initialBal=1000.0,
        )
        assert user.aadhar_num == '123456789012'
        assert user.father_name == 'Bob Example'
        assert user.initial_balance == 1000.0

    def test_email_is_optional(self):
        """Test that email can be omitted or set to None."""
        user = User(
            aadhar_num='123456789012',
            name='Alice Example',
            email=None,
            phone='9876543210',
            age=30,
            fatherName='Bob Example',
            city='Metropolis',
            initialBal=0.0,
        )
        assert user.email is None

    @pytest.mark.parametrize(
        'bad_aadhar',
        ['123', '1234567890123', 'abcd12345678', '1234-5678-9012', ''],
    )
    def test_invalid_aadhar_numbers_are_rejected(self, bad_aadhar):
        """Test that invalid Aadhar numbers are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num=bad_aadhar,
                name='Alice Example',
                phone='9876543210',
                age=30,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=0.0,
            )

    def test_name_too_short_is_rejected(self):
        """Test that names shorter than 3 characters are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='Al',
                phone='9876543210',
                age=30,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=0.0,
            )

    def test_name_too_long_is_rejected(self):
        """Test that names longer than 50 characters are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='A' * 51,
                phone='9876543210',
                age=30,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=0.0,
            )

    def test_invalid_email_is_rejected(self):
        """Test that malformed email addresses are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='Alice Example',
                email='not-an-email',
                phone='9876543210',
                age=30,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=0.0,
            )

    @pytest.mark.parametrize('phone', ['12345', '1234567890123456'])
    def test_phone_length_constraints(self, phone):
        """Test that phone numbers outside valid length range are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='Alice Example',
                phone=phone,
                age=30,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=0.0,
            )

    @pytest.mark.parametrize('age', [0, -1, 126, 200])
    def test_age_range_is_enforced(self, age):
        """Test that ages outside valid range (1-125) are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='Alice Example',
                phone='9876543210',
                age=age,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=0.0,
            )

    def test_negative_initial_balance_is_rejected(self):
        """Test that negative initial balances are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='Alice Example',
                phone='9876543210',
                age=30,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=-50.0,
            )

    def test_address_can_be_none(self):
        """Test that address is optional and can be None."""
        user = User(
            aadhar_num='123456789012',
            name='Alice Example',
            phone='9876543210',
            age=30,
            fatherName='Bob Example',
            city='Metropolis',
            initialBal=0.0,
            address=None,
        )
        assert user.address is None

    def test_address_too_long_is_rejected(self):
        """Test that addresses longer than 200 characters are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='Alice Example',
                phone='9876543210',
                age=30,
                fatherName='Bob Example',
                city='Metropolis',
                initialBal=0.0,
                address='A' * 201,
            )

    def test_city_too_short_is_rejected(self):
        """Test that city names shorter than 2 characters are rejected."""
        with pytest.raises(ValidationError):
            User(
                aadhar_num='123456789012',
                name='Alice Example',
                phone='9876543210',
                age=30,
                fatherName='Bob Example',
                city='A',
                initialBal=0.0,
            )


class TestAccountValidation:
    """Test suite for Account model validation."""
    
    def test_valid_account_is_accepted(self):
        """Test that valid account data passes validation with defaults."""
        account = Account(
            accountNum=500001,
            userId=1,
            balance=1000.0,
            currency='INR',
        )
        assert account.account_num == 500001
        assert account.account_type == 'savings'
        assert account.is_active is True

    def test_negative_balance_is_rejected(self):
        """Test that negative account balances are rejected."""
        with pytest.raises(ValidationError):
            Account(accountNum=500001, userId=1, balance=-10.0)

    def test_invalid_currency_length_is_rejected(self):
        """Test that currency codes must be exactly 3 characters."""
        with pytest.raises(ValidationError):
            Account(accountNum=500001, userId=1, currency='IN')

    def test_account_num_must_be_positive(self):
        """Test that account numbers must be greater than 0."""
        with pytest.raises(ValidationError):
            Account(accountNum=0, userId=1)

    def test_user_id_must_be_positive(self):
        """Test that user IDs must be greater than 0."""
        with pytest.raises(ValidationError):
            Account(accountNum=500001, userId=0)


class TestTransactionRecordValidation:
    """Test suite for TransactionRecord model validation."""
    
    def test_valid_transaction_is_accepted(self):
        """Test that valid transaction data passes validation."""
        txn = TransactionRecord(
            id=1,
            accountNum=500001,
            transactionType='deposit',
            amount=100.0,
            balanceAfter=1100.0,
            timestamp='2024-01-01T12:00:00',
        )
        assert txn.transaction_type == 'deposit'
        assert txn.balance_after == 1100.0

    def test_negative_amount_is_rejected(self):
        """Test that negative transaction amounts are rejected."""
        with pytest.raises(ValidationError):
            TransactionRecord(
                id=1,
                accountNum=500001,
                transactionType='deposit',
                amount=-10.0,
                balanceAfter=1000.0,
                timestamp='2024-01-01T12:00:00',
            )

