import sqlite3
import unittest

from symbolchain.nem.Network import Address

from puller.db.MultisigDatabase import MultisigDatabase

from ..test.DatabaseTestUtils import get_all_table_names
from ..test.OptinRequestTestUtils import NEM_ADDRESSES


class MultisigDatabaseTest(unittest.TestCase):
	# region create

	def test_can_create_tables(self):
		# Act:
		table_names = get_all_table_names(MultisigDatabase)

		# Assert:
		self.assertEqual(set(['nem_multisig_id', 'nem_multisig_cosignatory']), table_names)

	# endregion

	# region insert_if_multisig - valid

	def _assert_db_contents(self, connection, expected_multisigs, expected_multisig_cosignatories):
		cursor = connection.cursor()
		cursor.execute('''SELECT * FROM nem_multisig_id ORDER BY id ASC''')
		multisigs = cursor.fetchall()

		cursor.execute('''SELECT * FROM nem_multisig_cosignatory ORDER BY multisig_id ASC, address ASC''')
		multisig_cosignatories = cursor.fetchall()

		# Assert:
		self.assertEqual(expected_multisigs, multisigs)
		self.assertEqual(expected_multisig_cosignatories, multisig_cosignatories)

	def _assert_can_insert_accounts(self, one_or_more_accounts, expected_multisigs, expected_multisig_cosignatories):
		# Arrange:
		with sqlite3.connect(':memory:') as connection:
			accounts = one_or_more_accounts if isinstance(one_or_more_accounts, list) else [one_or_more_accounts]

			database = MultisigDatabase(connection)
			database.create_tables()

			# Act:
			for account in accounts:
				database.insert_if_multisig(account)

			# Assert:
			self._assert_db_contents(connection, expected_multisigs, expected_multisig_cosignatories)

	@staticmethod
	def _addresses_to_accounts(addresses):
		return list(map(lambda address: {'address': address, 'label': None}, addresses))

	def test_can_insert_multisig_account_information(self):
		self._assert_can_insert_accounts({
			'meta': {'cosignatories': self._addresses_to_accounts(NEM_ADDRESSES[:3])},
			'account': {'address': NEM_ADDRESSES[3], 'multisigInfo': {'cosignatoriesCount': 7, 'minCosignatories': 5}}
		}, [
			(1, Address(NEM_ADDRESSES[3]).bytes, 7, 5)
		], [
			(Address(NEM_ADDRESSES[0]).bytes, 1), (Address(NEM_ADDRESSES[1]).bytes, 1), (Address(NEM_ADDRESSES[2]).bytes, 1)
		])

	def test_can_skip_insert_regular_account_information(self):
		self._assert_can_insert_accounts({
			'meta': {'cosignatories': []}, 'account': {'multisigInfo': {}}
		}, [], [])

	def test_can_insert_multiple_multisig_account_informations(self):
		self._assert_can_insert_accounts([
			{
				'meta': {'cosignatories': self._addresses_to_accounts(NEM_ADDRESSES[:3])},
				'account': {'address': NEM_ADDRESSES[3], 'multisigInfo': {'cosignatoriesCount': 7, 'minCosignatories': 5}}
			},
			{
				'meta': {'cosignatories': []},
				'account': {'address': NEM_ADDRESSES[4], 'multisigInfo': {}}
			},
			{
				'meta': {'cosignatories': self._addresses_to_accounts([NEM_ADDRESSES[0]])},
				'account': {'address': NEM_ADDRESSES[1], 'multisigInfo': {'cosignatoriesCount': 6, 'minCosignatories': 4}}},
			{
				'meta': {'cosignatories': self._addresses_to_accounts([NEM_ADDRESSES[2]])},
				'account': {'address': NEM_ADDRESSES[0], 'multisigInfo': {'cosignatoriesCount': 8, 'minCosignatories': 6}}
			},
			{
				'meta': {'cosignatories': self._addresses_to_accounts(NEM_ADDRESSES[:2])},
				'account': {'address': NEM_ADDRESSES[2], 'multisigInfo': {'cosignatoriesCount': 3, 'minCosignatories': 2}}
			},
			{
				'meta': {'cosignatories': []},
				'account': {'multisigInfo': {}}
			}
		], [
			(1, Address(NEM_ADDRESSES[3]).bytes, 7, 5),
			(2, Address(NEM_ADDRESSES[1]).bytes, 6, 4),
			(3, Address(NEM_ADDRESSES[0]).bytes, 8, 6),
			(4, Address(NEM_ADDRESSES[2]).bytes, 3, 2)
		], [
			(Address(NEM_ADDRESSES[0]).bytes, 1), (Address(NEM_ADDRESSES[1]).bytes, 1), (Address(NEM_ADDRESSES[2]).bytes, 1),
			(Address(NEM_ADDRESSES[0]).bytes, 2),
			(Address(NEM_ADDRESSES[2]).bytes, 3),
			(Address(NEM_ADDRESSES[0]).bytes, 4), (Address(NEM_ADDRESSES[1]).bytes, 4)
		])

	# endregion

	# region is_multisig

	@staticmethod
	def _create_database_for_check_cosigners_tests(connection):
		# Arrange:
		database = MultisigDatabase(connection)
		database.create_tables()

		accounts = [
			{
				'meta': {'cosignatories': MultisigDatabaseTest._addresses_to_accounts(NEM_ADDRESSES[:3])},
				'account': {'address': NEM_ADDRESSES[3], 'multisigInfo': {'cosignatoriesCount': 3, 'minCosignatories': 2}}
			},
			{
				'meta': {'cosignatories': []},
				'account': {'address': NEM_ADDRESSES[4], 'multisigInfo': {}}
			},
			{
				'meta': {'cosignatories': MultisigDatabaseTest._addresses_to_accounts([NEM_ADDRESSES[0]])},
				'account': {'address': NEM_ADDRESSES[1], 'multisigInfo': {'cosignatoriesCount': 1, 'minCosignatories': 1}}
			},
			{
				'meta': {'cosignatories': MultisigDatabaseTest._addresses_to_accounts(NEM_ADDRESSES[:2])},
				'account': {'address': NEM_ADDRESSES[2], 'multisigInfo': {'cosignatoriesCount': 2, 'minCosignatories': 1}}
			}
		]

		# Act:
		for account in accounts:
			database.insert_if_multisig(account)

		return database

	def _run_is_multisig_account_test(self, address, expected_result):
		# Arrange:
		with sqlite3.connect(':memory:') as connection:
			database = self._create_database_for_check_cosigners_tests(connection)

			# Act:
			result = database.is_multisig(address)

			# Assert:
			self.assertEqual(expected_result, result)

	def test_is_multisig_returns_false_if_not_multisig_account(self):
		self._run_is_multisig_account_test(Address(NEM_ADDRESSES[4]), False)  # inserted, but skipped
		self._run_is_multisig_account_test(Address(NEM_ADDRESSES[0]), False)  # never inserted

	def test_is_multisig_returns_true_if_multisig_account(self):
		self._run_is_multisig_account_test(Address(NEM_ADDRESSES[1]), True)
		self._run_is_multisig_account_test(Address(NEM_ADDRESSES[2]), True)
		self._run_is_multisig_account_test(Address(NEM_ADDRESSES[3]), True)

	# endregion

	# region check_cosigners

	@staticmethod
	def _pick_nem_addresses(indexes):
		return [Address(NEM_ADDRESSES[index]) for index in indexes]

	def _run_check_cosigners_test(self, address, cosigner_addresses, expected_result):
		# Arrange:
		with sqlite3.connect(':memory:') as connection:
			database = self._create_database_for_check_cosigners_tests(connection)

			# Act:
			result = database.check_cosigners(address, cosigner_addresses)

			# Assert:
			self.assertEqual(expected_result, result)

	def test_cosigners_check_aborts_when_not_multisig_account(self):
		# Arrange:
		with sqlite3.connect(':memory:') as connection:
			database = self._create_database_for_check_cosigners_tests(connection)

			# Act:
			with self.assertRaises(RuntimeError):
				database.check_cosigners(Address(NEM_ADDRESSES[4]), [])

	def test_cosigners_check_fails_when_multisig_account_has_insufficient_cosigners(self):
		self._run_check_cosigners_test(Address(NEM_ADDRESSES[1]), [], (False, []))
		self._run_check_cosigners_test(Address(NEM_ADDRESSES[2]), [], (False, []))
		self._run_check_cosigners_test(Address(NEM_ADDRESSES[3]), [Address(NEM_ADDRESSES[0])], (False, [Address(NEM_ADDRESSES[0])]))

	def test_cosigners_check_passes_when_multisig_account_has_sufficient_cosigners(self):
		self._run_check_cosigners_test(Address(NEM_ADDRESSES[1]), [Address(NEM_ADDRESSES[0])], (True, [Address(NEM_ADDRESSES[0])]))
		self._run_check_cosigners_test(Address(NEM_ADDRESSES[2]), [Address(NEM_ADDRESSES[1])], (True, [Address(NEM_ADDRESSES[1])]))
		self._run_check_cosigners_test(
			Address(NEM_ADDRESSES[3]),
			self._pick_nem_addresses([0, 2]),
			(True, self._pick_nem_addresses([0, 2])))

		self._run_check_cosigners_test(
			Address(NEM_ADDRESSES[2]),
			self._pick_nem_addresses([0, 1]),
			(True, self._pick_nem_addresses([0, 1])))
		self._run_check_cosigners_test(
			Address(NEM_ADDRESSES[3]),
			self._pick_nem_addresses([0, 1, 2]),
			(True, self._pick_nem_addresses([0, 1, 2])))

	def test_cosigners_check_ignores_invalid_cosigners(self):
		self._run_check_cosigners_test(Address(NEM_ADDRESSES[3]), self._pick_nem_addresses([0, 4]), (False, [Address(NEM_ADDRESSES[0])]))

		self._run_check_cosigners_test(
			Address(NEM_ADDRESSES[3]),
			self._pick_nem_addresses([0, 4, 2]),
			(True, self._pick_nem_addresses([0, 2])))

	def test_cosigners_check_ignores_duplicate_cosigners(self):
		self._run_check_cosigners_test(Address(NEM_ADDRESSES[3]), self._pick_nem_addresses([0, 0, 0]), (False, [Address(NEM_ADDRESSES[0])]))

		self._run_check_cosigners_test(
			Address(NEM_ADDRESSES[3]),
			self._pick_nem_addresses([0, 0, 1, 0]),
			(True, self._pick_nem_addresses([0, 1])))

	# endregion
